"""Implementation of the API interfaces for the AirTouch 4."""

import asyncio
import contextlib
import datetime
import logging
from collections.abc import Awaitable, Iterable, Mapping, Sequence
from enum import Enum, auto
from typing import Any

from typing_extensions import override

import pyairtouch.api
import pyairtouch.at4.comms.hdr
import pyairtouch.at4.comms.x1F_ext as extended_msg
import pyairtouch.at4.comms.x1FFF10_err_info as err_info_msg
import pyairtouch.at4.comms.x1FFF11_ac_ability as ac_ability_msg
import pyairtouch.at4.comms.x1FFF12_group_names as group_names_msg
import pyairtouch.at4.comms.x1FFF20_quick_timer as quick_timer_msg
import pyairtouch.at4.comms.x1FFF30_console_ver as console_ver_msg
import pyairtouch.at4.comms.x2A_group_ctrl as group_ctrl_msg
import pyairtouch.at4.comms.x2B_group_status as group_status_msg
import pyairtouch.at4.comms.x2C_ac_ctrl as ac_ctrl_msg
import pyairtouch.at4.comms.x2D_ac_status as ac_status_msg
import pyairtouch.at4.comms.x36_ac_timer_ctrl as ac_timer_ctrl_msg
import pyairtouch.at4.comms.x37_ac_timer_status as ac_timer_status_msg
import pyairtouch.comms.heartbeat
import pyairtouch.comms.socket
from pyairtouch.api import AcMode

_LOGGER = logging.getLogger(__name__)

_GROUP_STATUS_TIMEOUT = 300.0
"""Timeout for group status in seconds.

After this interval a request will be sent for updated group status.

This is a work-around for an AirTouch 4 console bug where it stops sending group
status updates.
"""

# AirTouch 4 only supports integer set-points
_TARGET_TEMPERATURE_RESOLUTION = 1.0

_ZONE_POWER_STATE_MAPPING = {
    group_status_msg.GroupPowerState.OFF: pyairtouch.api.ZonePowerState.OFF,
    group_status_msg.GroupPowerState.ON: pyairtouch.api.ZonePowerState.ON,
    group_status_msg.GroupPowerState.TURBO: pyairtouch.api.ZonePowerState.TURBO,
}
_API_ZONE_POWER_MAPPING = {
    pyairtouch.api.ZonePowerState.OFF: group_ctrl_msg.GroupPowerControl.TURN_OFF,
    pyairtouch.api.ZonePowerState.ON: group_ctrl_msg.GroupPowerControl.TURN_ON,
    pyairtouch.api.ZonePowerState.TURBO: group_ctrl_msg.GroupPowerControl.TURBO,
}
_ZONE_CONTROL_METHOD_MAPPING = {
    group_status_msg.GroupControlMethod.DAMPER: pyairtouch.api.ZoneControlMethod.DAMPER,
    group_status_msg.GroupControlMethod.TEMPERATURE: (
        pyairtouch.api.ZoneControlMethod.TEMPERATURE
    ),
}
_SENSOR_BATTERY_STATUS_MAPPING = {
    group_status_msg.SensorBatteryStatus.NORMAL: (
        pyairtouch.api.SensorBatteryStatus.NORMAL
    ),
    group_status_msg.SensorBatteryStatus.LOW: pyairtouch.api.SensorBatteryStatus.LOW,
}


class At4Zone(pyairtouch.api.Zone):
    """An AirTouch 4 implementation of the Zone protocol."""

    def __init__(
        self,
        group_number: int,
        zone_name: str,
        socket: pyairtouch.comms.socket.AirTouchSocket[
            pyairtouch.at4.comms.hdr.At4Header
        ],
    ) -> None:
        """Initialise an AirTouch 4 Zone.

        Zones are known as Groups in the AirTouch 4 protocol.

        Args:
            group_number: The zone's group ID.
            zone_name: The human readable name of the zone.
            socket: The socket for communicating with the AirTouch 4.
        """
        self._name = zone_name
        self._group_status = group_status_msg.GroupStatusData(
            group_number=group_number,
            power_state=group_status_msg.GroupPowerState.OFF,
            control_method=group_status_msg.GroupControlMethod.DAMPER,
            spill_active=False,
            supports_turbo=False,
            has_sensor=False,
            battery_status=group_status_msg.SensorBatteryStatus.NORMAL,
            temperature=0.0,
            damper_percentage=0,
            set_point=None,
        )
        self._socket = socket

        self._subscribers: set[pyairtouch.api.UpdateSubscriber] = set()

    async def update_group_status(
        self, group_status: group_status_msg.GroupStatusData
    ) -> None:
        """Update the group status with new data."""
        if group_status.group_number != self._group_status.group_number:
            raise ValueError("Invalid group_number in updated status")

        old_status = self._group_status
        self._group_status = group_status

        if old_status != group_status:
            await _notify_subscribers([s(self.zone_id) for s in self._subscribers])

    @override
    @property
    def zone_id(self) -> int:
        return self._group_status.group_number

    @override
    @property
    def name(self) -> str:
        return self._name

    @override
    @property
    def supported_power_states(self) -> Sequence[pyairtouch.api.ZonePowerState]:
        supported_states = [
            pyairtouch.api.ZonePowerState.OFF,
            pyairtouch.api.ZonePowerState.ON,
        ]
        if self._group_status.supports_turbo:
            supported_states.append(pyairtouch.api.ZonePowerState.TURBO)
        return supported_states

    @override
    @property
    def power_state(self) -> pyairtouch.api.ZonePowerState:
        return _ZONE_POWER_STATE_MAPPING[self._group_status.power_state]

    @override
    @property
    def control_method(self) -> pyairtouch.api.ZoneControlMethod:
        return _ZONE_CONTROL_METHOD_MAPPING[self._group_status.control_method]

    @override
    @property
    def has_temp_sensor(self) -> bool:
        return self._group_status.has_sensor

    @override
    @property
    def sensor_battery_status(self) -> pyairtouch.api.SensorBatteryStatus:
        return _SENSOR_BATTERY_STATUS_MAPPING[self._group_status.battery_status]

    @override
    @property
    def current_temperature(self) -> float | None:
        return self._group_status.temperature

    @override
    @property
    def target_temperature(self) -> float | None:
        return self._group_status.set_point

    @override
    @property
    def target_temperature_resolution(self) -> float:
        return _TARGET_TEMPERATURE_RESOLUTION

    @override
    @property
    def current_damper_percentage(self) -> int:
        return self._group_status.damper_percentage

    @override
    @property
    def spill_active(self) -> bool:
        return self._group_status.spill_active

    @override
    async def set_power(self, power_control: pyairtouch.api.ZonePowerState) -> None:
        if power_control not in self.supported_power_states:
            raise ValueError(f"power_control {power_control} is not supported")

        await self._send_group_control_message(
            power=_API_ZONE_POWER_MAPPING[power_control]
        )

    @override
    async def set_target_temperature(self, temperature: float) -> None:
        if not self.has_temp_sensor:
            raise ValueError(
                "Cannot change temperature for zones without a temperature sensor"
            )
        # We keep things simple and always change the control method to align
        # with the requested setting.
        await self._send_group_control_message(
            control_method=group_ctrl_msg.GroupControlMethod.TEMPERATURE,
            setting=group_ctrl_msg.GroupSetPointControl(set_point=round(temperature)),
        )

    @override
    async def set_damper_percentage(self, open_percentage: int) -> None:
        if open_percentage < 0 or open_percentage > 100:  # noqa: PLR2004
            raise ValueError(
                f"open_percentage {open_percentage} is out of range [0, 100]"
            )
        await self._send_group_control_message(
            control_method=group_ctrl_msg.GroupControlMethod.DAMPER,
            setting=group_ctrl_msg.GroupDamperControl(open_percentage),
        )

    @override
    def subscribe(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers.add(subscriber)

    @override
    def unsubscribe(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers.discard(subscriber)

    async def _send_group_control_message(
        self,
        power: group_ctrl_msg.GroupPowerControl = (
            group_ctrl_msg.GroupPowerControl.UNCHANGED
        ),
        control_method: group_ctrl_msg.GroupControlMethod = (
            group_ctrl_msg.GroupControlMethod.UNCHANGED
        ),
        setting: group_ctrl_msg.GroupSetting = None,
    ) -> None:
        retry_config = pyairtouch.comms.socket.RETRY_IDEMPOTENT
        if isinstance(setting, group_ctrl_msg.GroupIncreaseDecrease) or (
            control_method == group_ctrl_msg.GroupControlMethod.CHANGE
        ):
            retry_config = pyairtouch.comms.socket.RETRY_NON_IDEMPOTENT

        await self._socket.send(
            message=group_ctrl_msg.GroupControlMessage(
                group_number=self._group_status.group_number,
                power=power,
                control_method=control_method,
                setting=setting,
            ),
            retry_policy=retry_config,
        )


_AC_POWER_STATE_MAPPING = {
    ac_status_msg.AcPowerState.OFF: pyairtouch.api.AcPowerState.OFF,
    ac_status_msg.AcPowerState.ON: pyairtouch.api.AcPowerState.ON,
}
_API_POWER_CONTROL_MAPPING = {
    pyairtouch.api.AcPowerControl.TOGGLE: ac_ctrl_msg.AcPowerControl.TOGGLE,
    pyairtouch.api.AcPowerControl.TURN_OFF: ac_ctrl_msg.AcPowerControl.TURN_OFF,
    pyairtouch.api.AcPowerControl.TURN_ON: ac_ctrl_msg.AcPowerControl.TURN_ON,
}
_AC_SELECTED_MODE_MAPPING = {
    ac_status_msg.AcMode.AUTO: pyairtouch.api.AcMode.AUTO,
    ac_status_msg.AcMode.HEAT: pyairtouch.api.AcMode.HEAT,
    ac_status_msg.AcMode.DRY: pyairtouch.api.AcMode.DRY,
    ac_status_msg.AcMode.FAN: pyairtouch.api.AcMode.FAN,
    ac_status_msg.AcMode.COOL: pyairtouch.api.AcMode.COOL,
    ac_status_msg.AcMode.AUTO_HEAT: pyairtouch.api.AcMode.AUTO,
    ac_status_msg.AcMode.AUTO_COOL: pyairtouch.api.AcMode.AUTO,
}
_AC_ACTIVE_MODE_MAPPING = {
    ac_status_msg.AcMode.AUTO: pyairtouch.api.AcMode.AUTO,
    ac_status_msg.AcMode.HEAT: pyairtouch.api.AcMode.HEAT,
    ac_status_msg.AcMode.DRY: pyairtouch.api.AcMode.DRY,
    ac_status_msg.AcMode.FAN: pyairtouch.api.AcMode.FAN,
    ac_status_msg.AcMode.COOL: pyairtouch.api.AcMode.COOL,
    ac_status_msg.AcMode.AUTO_HEAT: pyairtouch.api.AcMode.HEAT,
    ac_status_msg.AcMode.AUTO_COOL: pyairtouch.api.AcMode.COOL,
}
_API_MODE_CONTROL_MAPPING = {
    pyairtouch.api.AcMode.AUTO: ac_ctrl_msg.AcModeControl.AUTO,
    pyairtouch.api.AcMode.HEAT: ac_ctrl_msg.AcModeControl.HEAT,
    pyairtouch.api.AcMode.DRY: ac_ctrl_msg.AcModeControl.DRY,
    pyairtouch.api.AcMode.FAN: ac_ctrl_msg.AcModeControl.FAN,
    pyairtouch.api.AcMode.COOL: ac_ctrl_msg.AcModeControl.COOL,
}
_AC_FAN_SPEED_MAPPING = {
    ac_status_msg.AcFanSpeed.AUTO: pyairtouch.api.AcFanSpeed.AUTO,
    ac_status_msg.AcFanSpeed.QUIET: pyairtouch.api.AcFanSpeed.QUIET,
    ac_status_msg.AcFanSpeed.LOW: pyairtouch.api.AcFanSpeed.LOW,
    ac_status_msg.AcFanSpeed.MEDIUM: pyairtouch.api.AcFanSpeed.MEDIUM,
    ac_status_msg.AcFanSpeed.HIGH: pyairtouch.api.AcFanSpeed.HIGH,
    ac_status_msg.AcFanSpeed.POWERFUL: pyairtouch.api.AcFanSpeed.POWERFUL,
    ac_status_msg.AcFanSpeed.TURBO: pyairtouch.api.AcFanSpeed.TURBO,
}
_API_FAN_SPEED_CONTROL_MAPPING = {
    pyairtouch.api.AcFanSpeed.AUTO: ac_ctrl_msg.AcFanSpeedControl.AUTO,
    pyairtouch.api.AcFanSpeed.QUIET: ac_ctrl_msg.AcFanSpeedControl.QUIET,
    pyairtouch.api.AcFanSpeed.LOW: ac_ctrl_msg.AcFanSpeedControl.LOW,
    pyairtouch.api.AcFanSpeed.MEDIUM: ac_ctrl_msg.AcFanSpeedControl.MEDIUM,
    pyairtouch.api.AcFanSpeed.HIGH: ac_ctrl_msg.AcFanSpeedControl.HIGH,
    pyairtouch.api.AcFanSpeed.POWERFUL: ac_ctrl_msg.AcFanSpeedControl.POWERFUL,
    pyairtouch.api.AcFanSpeed.TURBO: ac_ctrl_msg.AcFanSpeedControl.TURBO,
}
_API_TIMER_TYPE_MAPPING = {
    pyairtouch.api.AcTimerType.OFF_TIMER: quick_timer_msg.TimerType.OFF_TIMER,
    pyairtouch.api.AcTimerType.ON_TIMER: quick_timer_msg.TimerType.ON_TIMER,
}


class At4AirConditioner(pyairtouch.api.AirConditioner):
    """An AirTouch 4 implementation of the AirConditioner protocol."""

    def __init__(
        self,
        ac_number: int,
        zones: Sequence[At4Zone],
        ac_ability: ac_ability_msg.AcAbility,
        socket: pyairtouch.comms.socket.AirTouchSocket[
            pyairtouch.at4.comms.hdr.At4Header
        ],
    ) -> None:
        """Initialise an AirTouch 4 Air-Conditioner.

        Args:
            ac_id: The ID of the air-conditioner.
            zones: The AirTouch zones associated with this air-conditioner.
            ac_ability: The functions supported by this air-conditioner.
            socket: Socket for communiating with the AirTouch 4.
        """
        self._ac_status = ac_status_msg.AcStatusData(
            ac_number=ac_number,
            power_state=ac_status_msg.AcPowerState.OFF,
            mode=ac_status_msg.AcMode.AUTO,
            fan_speed=ac_status_msg.AcFanSpeed.AUTO,
            spill_active=False,
            timer_set=False,
            set_point=0,
            temperature=0.0,
            error_code=0,
        )
        self._ac_timer_status = ac_timer_status_msg.AcTimerStatusData(
            ac_number=ac_number,
            on_timer=ac_timer_status_msg.AcTimerState(disabled=True, hour=0, minute=0),
            off_timer=ac_timer_status_msg.AcTimerState(disabled=True, hour=0, minute=0),
        )
        self._ac_error_info: str | None = None

        self._zones = zones
        for zone in self._zones:
            zone.subscribe(self._zone_updated)

        self._ac_ability = ac_ability

        self._supported_power_controls = list(_API_POWER_CONTROL_MAPPING.keys())
        self._supported_modes = [
            api_mode
            for api_mode, ac_mode in _API_MODE_CONTROL_MAPPING.items()
            if self._ac_ability.ac_mode_support[ac_mode]
        ]
        self._supported_fan_speeds = [
            api_fan_speed
            for api_fan_speed, ac_fan_speed in _API_FAN_SPEED_CONTROL_MAPPING.items()
            if self._ac_ability.fan_speed_support[ac_fan_speed]
        ]

        self._socket = socket

        self._subscribers: set[pyairtouch.api.UpdateSubscriber] = set()
        self._subscribers_ac_state: set[pyairtouch.api.UpdateSubscriber] = set()

    async def update_ac_status(self, ac_status: ac_status_msg.AcStatusData) -> None:
        """Update the AC Status with new data."""
        if ac_status.ac_number != self._ac_status.ac_number:
            raise ValueError("Invalid ac_number in updated status")

        old_status = self._ac_status
        self._ac_status = ac_status

        if old_status != ac_status:
            # Ensure error information is up to date according to the current
            # error code.
            if ac_status.has_error():
                await self._socket.send(
                    message=extended_msg.ExtendedMessage(
                        sub_message=err_info_msg.AcErrorInformationRequest(
                            ac_number=self.ac_id
                        )
                    ),
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )
            else:
                self._ac_error_info = None

            await _notify_subscribers(
                [
                    s(self.ac_id)
                    for s in self._subscribers.union(self._subscribers_ac_state)
                ]
            )

    async def update_ac_timer_status(
        self, ac_timer_status: ac_timer_status_msg.AcTimerStatusData
    ) -> None:
        """Update the AC Timer Status with new data."""
        if ac_timer_status.ac_number != self._ac_timer_status.ac_number:
            raise ValueError("Invalid ac_number in updated status")

        old_status = self._ac_timer_status
        self._ac_timer_status = ac_timer_status

        if old_status != ac_timer_status:
            await _notify_subscribers(
                [
                    s(self.ac_id)
                    for s in self._subscribers.union(self._subscribers_ac_state)
                ]
            )

    async def update_ac_error_info(self, error_info: str | None) -> None:
        """Update the AC Error Information with new data."""
        old_error_info = self._ac_error_info
        self._ac_error_info = error_info

        if old_error_info != error_info:
            await _notify_subscribers(
                [
                    s(self.ac_id)
                    for s in self._subscribers.union(self._subscribers_ac_state)
                ]
            )

    @override
    @property
    def ac_id(self) -> int:
        return self._ac_status.ac_number

    @override
    @property
    def name(self) -> str:
        return self._ac_ability.ac_name

    @override
    @property
    def supported_power_controls(self) -> Sequence[pyairtouch.api.AcPowerControl]:
        return self._supported_power_controls

    @override
    @property
    def supported_modes(self) -> Sequence[pyairtouch.api.AcMode]:
        return self._supported_modes

    @override
    @property
    def supported_fan_speeds(self) -> Sequence[pyairtouch.api.AcFanSpeed]:
        return self._supported_fan_speeds

    @override
    @property
    def power_state(self) -> pyairtouch.api.AcPowerState:
        return _AC_POWER_STATE_MAPPING[self._ac_status.power_state]

    @override
    @property
    def selected_mode(self) -> pyairtouch.api.AcMode:
        return _AC_SELECTED_MODE_MAPPING[self._ac_status.mode]

    @override
    @property
    def active_mode(self) -> pyairtouch.api.AcMode:
        return _AC_ACTIVE_MODE_MAPPING[self._ac_status.mode]

    @override
    @property
    def selected_fan_speed(self) -> pyairtouch.api.AcFanSpeed:
        return _AC_FAN_SPEED_MAPPING[self._ac_status.fan_speed]

    @override
    @property
    def active_fan_speed(self) -> pyairtouch.api.AcFanSpeed:
        # AirTouch 4 doesn't support Intelligent Auto or any other way to
        # identify the underlying fan speed in Auto fan speed modes, so we just
        # return the currently selected fan speed.
        return _AC_FAN_SPEED_MAPPING[self._ac_status.fan_speed]

    @override
    @property
    def current_temperature(self) -> float:
        return self._ac_status.temperature

    @override
    @property
    def target_temperature(self) -> float:
        return self._ac_status.set_point

    @override
    @property
    def target_temperature_resolution(self) -> float:
        return _TARGET_TEMPERATURE_RESOLUTION

    @override
    @property
    def min_target_temperature(self) -> float:
        return self._ac_ability.min_set_point

    @override
    @property
    def max_target_temperature(self) -> float:
        return self._ac_ability.max_set_point

    @override
    @property
    def spill_state(self) -> pyairtouch.api.AcSpillState:
        if self._ac_status.spill_active:
            return pyairtouch.api.AcSpillState.SPILL
        return pyairtouch.api.AcSpillState.NONE

    @override
    @property
    def zones(self) -> Sequence[pyairtouch.api.Zone]:
        return self._zones

    @override
    def next_quick_timer(
        self, timer_type: pyairtouch.api.AcTimerType
    ) -> datetime.time | None:
        match timer_type:
            case pyairtouch.api.AcTimerType.OFF_TIMER:
                timer_state = self._ac_timer_status.off_timer
            case pyairtouch.api.AcTimerType.ON_TIMER:
                timer_state = self._ac_timer_status.on_timer

        if timer_state.disabled:
            return None
        return datetime.time(hour=timer_state.hour, minute=timer_state.minute)

    @override
    @property
    def error_info(self) -> pyairtouch.api.AcErrorInfo | None:
        if self._ac_status.has_error():
            return pyairtouch.api.AcErrorInfo(
                code=self._ac_status.error_code,
                description=self._ac_error_info,
            )
        return None

    @override
    async def set_power(self, power_control: pyairtouch.api.AcPowerControl) -> None:
        if power_control not in self._supported_power_controls:
            raise ValueError(f"power_control {power_control} is not supported")

        await self._send_ac_control_message(
            power=_API_POWER_CONTROL_MAPPING[power_control]
        )

    @override
    async def set_mode(self, mode: AcMode, *, power_on: bool = False) -> None:
        if mode not in self._supported_modes:
            raise ValueError(f"mode {mode} is not a supported mode")

        power = ac_ctrl_msg.AcPowerControl.UNCHANGED
        if power_on:
            power = ac_ctrl_msg.AcPowerControl.TURN_ON

        await self._send_ac_control_message(
            power=power,
            mode=_API_MODE_CONTROL_MAPPING[mode],
        )

    @override
    async def set_fan_speed(self, fan_speed: pyairtouch.api.AcFanSpeed) -> None:
        if fan_speed not in self._supported_fan_speeds:
            raise ValueError(f"fan_speed {fan_speed} is not a supported fan speed")
        await self._send_ac_control_message(
            fan_speed=_API_FAN_SPEED_CONTROL_MAPPING[fan_speed]
        )

    @override
    async def set_target_temperature(self, temperature: float) -> None:
        # Round to the correct resolution
        rounded_temperature = round(temperature)
        rounded_min = round(self.min_target_temperature)
        rounded_max = round(self.max_target_temperature)
        # Clip the temperature to remain with the min/max values.
        clipped_temperature = min(max(rounded_min, rounded_temperature), rounded_max)
        await self._send_ac_control_message(
            set_point_control=ac_ctrl_msg.AcSetPointValue(clipped_temperature)
        )

    @override
    async def set_quick_timer(
        self,
        timer_type: pyairtouch.api.AcTimerType,
        value: datetime.time | datetime.timedelta,
    ) -> None:
        match value:
            case datetime.timedelta():
                await self._socket.send(
                    message=extended_msg.ExtendedMessage(
                        sub_message=quick_timer_msg.QuickTimerMessage(
                            ac_number=self.ac_id,
                            timer_type=_API_TIMER_TYPE_MAPPING[timer_type],
                            duration=value,
                        )
                    ),
                    # Not strictly IDEMPOTENT since it is a duration, but given the
                    # one minute resolution it is close enough to use that retry policy.
                    retry_policy=pyairtouch.comms.socket.RETRY_IDEMPOTENT,
                )
            case datetime.time():
                new_timer = ac_timer_ctrl_msg.AcTimerState(
                    disabled=False,
                    hour=value.hour,
                    minute=value.minute,
                )
                await self._send_timer_control_message(timer_type, new_timer)

            case _:
                raise ValueError(f"value of type '{type(value)}' is unsupported")

    @override
    async def clear_quick_timer(self, timer_type: pyairtouch.api.AcTimerType) -> None:
        new_timer = ac_timer_ctrl_msg.AcTimerState(
            disabled=True,
            hour=0,
            minute=0,
        )
        await self._send_timer_control_message(timer_type, new_timer)

    @override
    def subscribe(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers.add(subscriber)

    @override
    def unsubscribe(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers.discard(subscriber)

    @override
    def subscribe_ac_state(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers_ac_state.add(subscriber)

    @override
    def unsubscribe_ac_state(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers_ac_state.discard(subscriber)

    async def _zone_updated(self, _: int) -> None:
        # Notify the interested subscribers when a Zone has been updated
        await _notify_subscribers([s(self.ac_id) for s in self._subscribers])

    async def _send_ac_control_message(
        self,
        power: ac_ctrl_msg.AcPowerControl = ac_ctrl_msg.AcPowerControl.UNCHANGED,
        mode: ac_ctrl_msg.AcModeControl = ac_ctrl_msg.AcModeControl.UNCHANGED,
        fan_speed: ac_ctrl_msg.AcFanSpeedControl = (
            ac_ctrl_msg.AcFanSpeedControl.UNCHANGED
        ),
        set_point_control: ac_ctrl_msg.AcSetPointControl = None,
    ) -> None:
        retry_config = pyairtouch.comms.socket.RETRY_IDEMPOTENT
        if (isinstance(set_point_control, ac_ctrl_msg.AcIncreaseDecrease)) or (
            power == ac_ctrl_msg.AcPowerControl.TOGGLE
        ):
            retry_config = pyairtouch.comms.socket.RETRY_NON_IDEMPOTENT
        await self._socket.send(
            message=ac_ctrl_msg.AcControlMessage(
                ac_number=self.ac_id,
                power=power,
                mode=mode,
                fan_speed=fan_speed,
                set_point_control=set_point_control,
            ),
            retry_policy=retry_config,
        )

    async def _send_timer_control_message(
        self,
        timer_type: pyairtouch.api.AcTimerType,
        timer_state: ac_timer_ctrl_msg.AcTimerState,
    ) -> None:
        """Send a Timer Control message to update a single timer state."""
        # Update only the specified timer and retain the other timer at its
        # existing value.
        on_timer = (
            timer_state
            if timer_type == pyairtouch.api.AcTimerType.ON_TIMER
            else self._ac_timer_status.on_timer
        )
        off_timer = (
            timer_state
            if timer_type == pyairtouch.api.AcTimerType.OFF_TIMER
            else self._ac_timer_status.off_timer
        )

        await self._socket.send(
            message=ac_timer_ctrl_msg.AcTimerControlMessage(
                ac_timer_status=[
                    ac_timer_ctrl_msg.AcTimerControlData(
                        ac_number=self.ac_id,
                        on_timer=on_timer,
                        off_timer=off_timer,
                    )
                ]
            ),
            retry_policy=pyairtouch.comms.socket.RETRY_IDEMPOTENT,
        )


class _AirTouchState(Enum):
    """Enum representing the state machine for the AirTouch interface."""

    CLOSED = auto()
    # ↓ Open socket
    CONNECTING = auto()
    # ↓ Connected, send ConsoleVersionRequest
    INIT_VERSION = auto()
    # ↓ Receive ConsoleVersionMessage, send GroupNamesRequest
    INIT_GROUP_NAMES = auto()
    # ↓ Receive GroupNamesMessage, send AcAbilityRequest
    INIT_AC_ABILITY = auto()
    # ↓ Receive AcAbilityMessage, send AcStatusRequest
    INIT_AC_STATUS = auto()
    # ↓ Receive AcStatus, send AcTimerStatusRequest
    INIT_AC_TIMER_STATUS = auto()
    # ↓ Receive AcTimerStatus, send GroupStatusRequest
    INIT_GROUP_STATUS = auto()
    # ↓ Receive GroupStatusMessage
    CONNECTED = auto()


DEFAULT_PORT_NUMBER = 9004
"""Default port number for communicating with the AirTouch controller.

This port number is statically defined within the interface specification.
"""


class AirTouch4(pyairtouch.api.AirTouch):
    """The main entrypoint for the AirTouch 4 API."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        airtouch_id: str,
        serial: str,
        name: str,
        socket: pyairtouch.comms.socket.AirTouchSocket[
            pyairtouch.at4.comms.hdr.At4Header
        ],
    ) -> None:
        """Initialise the AirTouch 4 object.

        Args:
            airtouch_id: The ID of the primary AirTouch controller.
            serial: The serial number for the primary AirTouch controller.
            name: The human readable name for the AirTouch system.
            socket: The socket for communicating with the AirTouch.
                This class will take over ownership of the socket to mange the
                connection state.
        """
        self._loop = loop
        self._airtouch_id = airtouch_id
        self._serial = serial
        self._name = name
        self._socket = socket

        # Using the console version request as a heartbeat also ensures that we
        # receive timely notifications when an update is available.
        def is_heartbeat_response(message: pyairtouch.comms.Message) -> bool:
            if isinstance(message, extended_msg.ExtendedMessage):
                # Use a local variable to keep mypy happy.
                # mypy thinks message is of type ExtendedMessage[Any]
                sub_message: pyairtouch.comms.Message = message.sub_message
                return sub_message.message_id == console_ver_msg.MESSAGE_ID
            return False

        self._heartbeat_manager = pyairtouch.comms.heartbeat.HeartbeatManager(
            loop=loop,
            socket=socket,
            config=pyairtouch.comms.heartbeat.HeartbeatConfig(
                message=extended_msg.ExtendedMessage(
                    console_ver_msg.ConsoleVersionRequest()
                ),
                response_match=is_heartbeat_response,
            ),
        )

        self._console_version = console_ver_msg.ConsoleVersionMessage(
            update_available=False,
            versions=[],
        )

        self._air_conditioners: dict[int, At4AirConditioner] = {}
        self._zones: dict[int, At4Zone] = {}

        self._state = _AirTouchState.CLOSED
        self._initialised_event = asyncio.Event()
        self._group_status_received_event = asyncio.Event()
        self._group_status_request_task: asyncio.Task[None] | None = None

        self._subscribers: set[pyairtouch.api.AirTouchSubscriber] = set()

    @override
    async def init(self) -> bool:
        """Initialise the connection with the AirTouch controller.

        Opens the socket to communicate with the AirTouch and loads initial
        state related to the capabilities of the AirTouch system.
        """
        self._state = _AirTouchState.CONNECTING
        self._socket.subscribe_on_connection_changed(self._connection_changed)
        self._socket.subscribe_on_message_received(self._message_received)
        await self._socket.open_socket()

        # Initialisation should finish quite quickly, but allow up to 5 seconds
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._initialised_event.wait(), timeout=5.0)
        return self._initialised_event.is_set()

    @override
    async def shutdown(self) -> None:
        self._state = _AirTouchState.CLOSED
        self._initialised_event.clear()

        if self._group_status_request_task:
            self._group_status_request_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._group_status_request_task

        await self._heartbeat_manager.stop()
        await self._socket.close()

        # Drop references to previously discovered zones and ACs to allow
        # garbage collection.
        self._air_conditioners.clear()
        self._zones.clear()

    @override
    @property
    def initialised(self) -> bool:
        return self._initialised_event.is_set()

    @override
    @property
    def airtouch_id(self) -> str:
        return self._airtouch_id

    @override
    @property
    def serial(self) -> str:
        return self._serial

    @override
    @property
    def name(self) -> str:
        return self._name

    @override
    @property
    def host(self) -> str:
        return self._socket.host

    @override
    @property
    def model(self) -> pyairtouch.api.AirTouchModel:
        return pyairtouch.api.AirTouchModel.AIRTOUCH_4

    @override
    @property
    def update_available(self) -> bool:
        return self._console_version.update_available

    @override
    @property
    def console_versions(self) -> Sequence[str]:
        return self._console_version.versions

    @override
    @property
    def air_conditioners(self) -> Sequence[pyairtouch.api.AirConditioner]:
        return list(self._air_conditioners.values())

    @override
    async def check_for_updates(self) -> None:
        await self._socket.send(
            message=extended_msg.ExtendedMessage(
                console_ver_msg.ConsoleVersionRequest()
            ),
            retry_policy=pyairtouch.comms.socket.RETRY_IDEMPOTENT,
        )

    @override
    def subscribe(self, subscriber: pyairtouch.api.AirTouchSubscriber) -> None:
        self._subscribers.add(subscriber)

    @override
    def unsubscribe(self, subscriber: pyairtouch.api.AirTouchSubscriber) -> None:
        self._subscribers.discard(subscriber)

    async def _connection_changed(self, *, connected: bool) -> None:
        if connected and self._state == _AirTouchState.CONNECTING:
            # Move into the INIT_VERSION state by sending a ConsoleVersionRequest
            self._state = _AirTouchState.INIT_VERSION
            version_request = extended_msg.ExtendedMessage(
                console_ver_msg.ConsoleVersionRequest()
            )
            await self._socket.send(
                message=version_request,
                retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
            )
        elif connected:
            # Request the latest status in case we've been disconnected for a
            # while.
            await self._socket.send(
                message=ac_status_msg.AcStatusRequest(),
                retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
            )
            await self._socket.send(
                message=group_status_msg.GroupStatusRequest(),
                retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
            )

    async def _message_received(  # noqa: C901
        self, _: pyairtouch.at4.comms.hdr.At4Header, message: pyairtouch.comms.Message
    ) -> None:
        # Process messages according to the current state.
        # Unexpected messages are silently ignored.
        match message:
            case extended_msg.ExtendedMessage(
                console_ver_msg.ConsoleVersionMessage()
            ) if self._state == _AirTouchState.INIT_VERSION:
                self._console_version = message.sub_message
                # Move to the next state
                self._state = _AirTouchState.INIT_GROUP_NAMES
                group_names_request = extended_msg.ExtendedMessage(
                    group_names_msg.GroupNamesRequest(group_number="ALL")
                )
                await self._socket.send(
                    message=group_names_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case extended_msg.ExtendedMessage(
                group_names_msg.GroupNamesMessage(group_names)
            ) if self._state == _AirTouchState.INIT_GROUP_NAMES:
                self._process_group_names_message(group_names)
                # Move to the next state
                self._state = _AirTouchState.INIT_AC_ABILITY
                ability_request = extended_msg.ExtendedMessage(
                    ac_ability_msg.AcAbilityRequest(ac_number="ALL")
                )
                await self._socket.send(
                    message=ability_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case extended_msg.ExtendedMessage(
                ac_ability_msg.AcAbilityMessage(ac_abilities)
            ) if self._state == _AirTouchState.INIT_AC_ABILITY:
                self._process_ac_ability_message(ac_abilities)
                # Move to the next state
                self._state = _AirTouchState.INIT_AC_STATUS
                await self._socket.send(
                    message=ac_status_msg.AcStatusRequest(),
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ac_status_msg.AcStatusMessage(ac_statuses) if (
                self._state == _AirTouchState.INIT_AC_STATUS
            ):
                await self._process_ac_status_message(ac_statuses)
                # Move to the next state
                self._state = _AirTouchState.INIT_AC_TIMER_STATUS
                await self._socket.send(
                    message=ac_timer_status_msg.AcTimerStatusRequest(),
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ac_timer_status_msg.AcTimerStatusMessage(ac_timer_statuses) if (
                self._state == _AirTouchState.INIT_AC_TIMER_STATUS
            ):
                await self._process_ac_timer_status_message(ac_timer_statuses)
                # Move to the next state
                self._state = _AirTouchState.INIT_GROUP_STATUS
                await self._socket.send(
                    message=group_status_msg.GroupStatusRequest(),
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case group_status_msg.GroupStatusMessage(groups) if (
                self._state == _AirTouchState.INIT_GROUP_STATUS
            ):
                await self._process_group_status_message(groups)
                # Move to the next state
                self._state = _AirTouchState.CONNECTED
                await self._heartbeat_manager.start()
                self._group_status_request_task = self._loop.create_task(
                    self._group_status_request_loop()
                )
                self._initialised_event.set()

            case ac_status_msg.AcStatusMessage(ac_statues) if (
                self._state == _AirTouchState.CONNECTED
            ):
                await self._process_ac_status_message(ac_statues)

            case ac_timer_status_msg.AcTimerStatusMessage(ac_timer_statuses) if (
                self._state == _AirTouchState.CONNECTED
            ):
                await self._process_ac_timer_status_message(ac_timer_statuses)

            case group_status_msg.GroupStatusMessage(groups) if (
                self._state == _AirTouchState.CONNECTED
            ):
                self._group_status_received_event.set()
                await self._process_group_status_message(groups)

            case extended_msg.ExtendedMessage(
                console_ver_msg.ConsoleVersionMessage()
            ) if self._state == _AirTouchState.CONNECTED:
                await self._process_console_version_update(message.sub_message)

            case extended_msg.ExtendedMessage(err_info_msg.AcErrorInformationMessage()):
                await self._process_ac_error_info_message(message.sub_message)

    def _process_group_names_message(self, group_names: Mapping[int, str]) -> None:
        for group_number, group_name in group_names.items():
            self._zones[group_number] = At4Zone(
                group_number=group_number,
                zone_name=group_name,
                socket=self._socket,
            )

    def _process_ac_ability_message(
        self, ac_abilities: Sequence[ac_ability_msg.AcAbility]
    ) -> None:
        for ac in ac_abilities:
            # Use the new groups field in preference to the old start/count fields.
            # group_count seems to be incorrect for newer console versions so it
            # can't be relied on.
            if ac.groups is not None:
                ac_zones = [self._zones[zone_id] for zone_id in ac.groups]

            elif len(ac_abilities) == 1:
                # As per the interface specifications, if there's only one AC
                # then all zones belong to it. Real-world messages have shown
                # that the group_count can be zero for the first AC when there
                # is only one AC.
                ac_zones = list(self._zones.values())

            else:
                # This is probably an old console which typically wouldn't be
                # expected in the wild, but we'll just have to trust the
                # group_count here.
                ac_zones = [
                    self._zones[zone_id]
                    for zone_id in range(
                        ac.start_group, ac.start_group + ac.group_count
                    )
                ]

            self._air_conditioners[ac.ac_number] = At4AirConditioner(
                ac_number=ac.ac_number,
                zones=ac_zones,
                ac_ability=ac,
                socket=self._socket,
            )

    async def _process_ac_status_message(
        self, ac_statues: Sequence[ac_status_msg.AcStatusData]
    ) -> None:
        for ac_status in ac_statues:
            ac_instance = self._air_conditioners.get(ac_status.ac_number)
            if ac_instance:
                await ac_instance.update_ac_status(ac_status)
            else:
                _LOGGER.warning("Unknown AC in AC Status: %d", ac_status.ac_number)

    async def _process_ac_timer_status_message(
        self, ac_timer_statuses: Sequence[ac_timer_status_msg.AcTimerStatusData]
    ) -> None:
        for ac_timer_status in ac_timer_statuses:
            ac_instance = self._air_conditioners.get(ac_timer_status.ac_number)
            if ac_instance:
                await ac_instance.update_ac_timer_status(ac_timer_status)
            else:
                # The AC Timer Status always includes an entry for four ACs even
                # if there is only one. Ignore any unmatched ac_number values.
                pass

    async def _process_ac_error_info_message(
        self, ac_error_info: err_info_msg.AcErrorInformationMessage
    ) -> None:
        ac_instance = self._air_conditioners.get(ac_error_info.ac_number)
        if ac_instance:
            await ac_instance.update_ac_error_info(ac_error_info.error_info)

    async def _process_group_status_message(
        self, groups: Sequence[group_status_msg.GroupStatusData]
    ) -> None:
        for group_status in groups:
            zone_instance = self._zones.get(group_status.group_number)
            if zone_instance:
                await zone_instance.update_group_status(group_status)
            else:
                _LOGGER.warning(
                    "Unknown Group in Group Status: %d", group_status.group_number
                )

    async def _process_console_version_update(
        self, console_version: console_ver_msg.ConsoleVersionMessage
    ) -> None:
        old_version = self._console_version
        self._console_version = console_version
        if old_version != console_version:
            await _notify_subscribers([s(self._airtouch_id) for s in self._subscribers])

    async def _group_status_request_loop(self) -> None:
        """Periodically requests updated group status.

        AirTouch 4 sometimes gets stuck in a state where GroupStatus messages
        are not published. This has been observed even while the AC is turned on
        and regular AC Status updates are being received. As a work-around, we
        regularly request updated Group Status if no updates have been received
        for a while.
        """
        # Run until cancelled
        while True:
            try:
                async with asyncio.timeout(_GROUP_STATUS_TIMEOUT) as timeout:
                    while True:
                        await self._group_status_received_event.wait()
                        timeout.reschedule(self._loop.time() + _GROUP_STATUS_TIMEOUT)
                        self._group_status_received_event.clear()
            except TimeoutError:
                _LOGGER.debug("Group status timed out, requesting update")
                if self._socket.is_connected:
                    await self._socket.send(
                        message=group_status_msg.GroupStatusRequest(),
                        retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                    )


async def _notify_subscribers(callbacks: Iterable[Awaitable[Any]]) -> None:
    for coro in asyncio.as_completed(callbacks):
        try:
            _ = await coro
        except Exception:
            _LOGGER.exception("Exception from subscriber")
