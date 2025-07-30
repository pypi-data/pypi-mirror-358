"""Implementation of the API interfaces for the AirTouch 5."""

import asyncio
import contextlib
import datetime
import logging
from collections.abc import Awaitable, Iterable, Mapping, Sequence
from enum import Enum, auto
from typing import Any

from typing_extensions import override

import pyairtouch.api
import pyairtouch.at5.comms.hdr
import pyairtouch.at5.comms.x1FFF10_err_info as err_info_msg
import pyairtouch.at5.comms.x1FFF30_console_ver as console_ver_msg
import pyairtouch.at5.comms.x1FFF49_quick_timer as quick_timer_msg
import pyairtouch.at5.comms.xC020_zone_ctrl as zone_ctrl_msg
import pyairtouch.at5.comms.xC021_zone_status as zone_status_msg
import pyairtouch.at5.comms.xC022_ac_ctrl as ac_ctrl_msg
import pyairtouch.at5.comms.xC023_ac_status as ac_status_msg
import pyairtouch.at5.comms.xC032_ac_timer_ctrl as ac_timer_ctrl_msg
import pyairtouch.at5.comms.xC033_ac_timer_status as ac_timer_status_msg
import pyairtouch.comms.heartbeat
import pyairtouch.comms.socket
from pyairtouch.at5.comms.x1F_ext import (
    ExtendedMessage,
)
from pyairtouch.at5.comms.x1FFF11_ac_ability import (
    AcAbility,
    AcAbilityMessage,
    AcAbilityRequest,
)
from pyairtouch.at5.comms.x1FFF13_zone_names import (
    ZoneNamesMessage,
    ZoneNamesRequest,
)
from pyairtouch.at5.comms.xC0_ctrl_status import ControlStatusMessage

_LOGGER = logging.getLogger(__name__)


# AirTouch 5 supports set-points with a resolution of 0.1 degrees.
_TARGET_TEMPERATURE_RESOLUTION = 0.1

_ZONE_POWER_STATE_MAPPING = {
    zone_status_msg.ZonePowerState.OFF: pyairtouch.api.ZonePowerState.OFF,
    zone_status_msg.ZonePowerState.ON: pyairtouch.api.ZonePowerState.ON,
    zone_status_msg.ZonePowerState.TURBO: pyairtouch.api.ZonePowerState.TURBO,
}
_API_ZONE_POWER_MAPPING = {
    pyairtouch.api.ZonePowerState.OFF: zone_ctrl_msg.ZonePowerControl.TURN_OFF,
    pyairtouch.api.ZonePowerState.ON: zone_ctrl_msg.ZonePowerControl.TURN_ON,
    pyairtouch.api.ZonePowerState.TURBO: zone_ctrl_msg.ZonePowerControl.TURBO,
}
_ZONE_CONTROL_METHOD_MAPPING = {
    zone_status_msg.ZoneControlMethod.DAMPER: pyairtouch.api.ZoneControlMethod.DAMPER,
    zone_status_msg.ZoneControlMethod.TEMPERATURE: (
        pyairtouch.api.ZoneControlMethod.TEMPERATURE
    ),
}
_SENSOR_BATTERY_STATUS_MAPPING = {
    zone_status_msg.SensorBatteryStatus.NORMAL: (
        pyairtouch.api.SensorBatteryStatus.NORMAL
    ),
    zone_status_msg.SensorBatteryStatus.LOW: pyairtouch.api.SensorBatteryStatus.LOW,
}


class At5Zone(pyairtouch.api.Zone):
    """An AirTouch 5 implementation of the Zone protocol."""

    def __init__(
        self,
        zone_number: int,
        zone_name: str,
        socket: pyairtouch.comms.socket.AirTouchSocket[
            pyairtouch.at5.comms.hdr.At5Header
        ],
    ) -> None:
        """Initialise an AirTouch 5 Zone.

        Args:
            zone_number: The zone ID.
            zone_name: The human readable name of the zone.
            socket: The socket for communicating with the AirTouch 5
        """
        self._name = zone_name
        self._zone_status = zone_status_msg.ZoneStatusData(
            zone_number=zone_number,
            power_state=zone_status_msg.ZonePowerState.OFF,
            spill_active=False,
            control_method=zone_status_msg.ZoneControlMethod.DAMPER,
            has_sensor=False,
            battery_status=zone_status_msg.SensorBatteryStatus.NORMAL,
            temperature=0.0,
            damper_percentage=0,
            set_point=None,
        )
        self._socket = socket

        self._supported_power_states = list(_API_ZONE_POWER_MAPPING.keys())

        self._subscribers: set[pyairtouch.api.UpdateSubscriber] = set()

    async def update_zone_status(
        self, zone_status: zone_status_msg.ZoneStatusData
    ) -> None:
        """Update the zone status with new data."""
        if zone_status.zone_number != self._zone_status.zone_number:
            raise ValueError("Invalid zone_number in updated status")

        old_status = self._zone_status
        self._zone_status = zone_status

        if old_status != zone_status:
            await _notify_subscribers([s(self.zone_id) for s in self._subscribers])

    @override
    @property
    def zone_id(self) -> int:
        return self._zone_status.zone_number

    @override
    @property
    def name(self) -> str:
        return self._name

    @override
    @property
    def supported_power_states(self) -> Sequence[pyairtouch.api.ZonePowerState]:
        return self._supported_power_states

    @override
    @property
    def power_state(self) -> pyairtouch.api.ZonePowerState:
        return _ZONE_POWER_STATE_MAPPING[self._zone_status.power_state]

    @override
    @property
    def control_method(self) -> pyairtouch.api.ZoneControlMethod:
        return _ZONE_CONTROL_METHOD_MAPPING[self._zone_status.control_method]

    @override
    @property
    def has_temp_sensor(self) -> bool:
        return self._zone_status.has_sensor

    @override
    @property
    def sensor_battery_status(self) -> pyairtouch.api.SensorBatteryStatus:
        return _SENSOR_BATTERY_STATUS_MAPPING[self._zone_status.battery_status]

    @override
    @property
    def current_temperature(self) -> float | None:
        return self._zone_status.temperature

    @override
    @property
    def target_temperature(self) -> float | None:
        return self._zone_status.set_point

    @override
    @property
    def target_temperature_resolution(self) -> float:
        return _TARGET_TEMPERATURE_RESOLUTION

    @override
    @property
    def current_damper_percentage(self) -> int:
        return self._zone_status.damper_percentage

    @override
    @property
    def spill_active(self) -> bool:
        return self._zone_status.spill_active

    @override
    async def set_power(self, power_control: pyairtouch.api.ZonePowerState) -> None:
        if power_control not in self.supported_power_states:
            raise ValueError(f"power_control {power_control} is not supported")

        await self._send_zone_control_message(
            zone_power=_API_ZONE_POWER_MAPPING[power_control]
        )

    @override
    async def set_target_temperature(self, temperature: float) -> None:
        if not self.has_temp_sensor:
            raise ValueError(
                "Cannot change temperature for zones without a temperature sensor"
            )
        await self._send_zone_control_message(
            zone_setting=zone_ctrl_msg.ZoneSetPointControl(
                round(temperature, ndigits=1)
            )
        )

    @override
    async def set_damper_percentage(self, open_percentage: int) -> None:
        if open_percentage < 0 or open_percentage > 100:  # noqa: PLR2004
            raise ValueError(
                f"open_percentage {open_percentage} is out of range [0, 100]"
            )
        await self._send_zone_control_message(
            zone_setting=zone_ctrl_msg.ZoneDamperControl(open_percentage)
        )

    @override
    def subscribe(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers.add(subscriber)

    @override
    def unsubscribe(self, subscriber: pyairtouch.api.UpdateSubscriber) -> None:
        self._subscribers.discard(subscriber)

    async def _send_zone_control_message(
        self,
        zone_power: zone_ctrl_msg.ZonePowerControl = (
            zone_ctrl_msg.ZonePowerControl.UNCHANGED
        ),
        zone_setting: zone_ctrl_msg.ZoneSetting = None,
    ) -> None:
        message = ControlStatusMessage(
            zone_ctrl_msg.ZoneControlMessage(
                [
                    zone_ctrl_msg.ZoneControlData(
                        zone_number=self.zone_id,
                        zone_power=zone_power,
                        zone_setting=zone_setting,
                    )
                ]
            )
        )
        retry_config = pyairtouch.comms.socket.RETRY_IDEMPOTENT
        if isinstance(zone_setting, zone_ctrl_msg.ZoneIncreaseDecrease) or (
            zone_power == zone_ctrl_msg.ZonePowerControl.TOGGLE
        ):
            retry_config = pyairtouch.comms.socket.RETRY_NON_IDEMPOTENT
        await self._socket.send(message, retry_config)


_AC_POWER_STATE_MAPPING = {
    ac_status_msg.AcPowerState.OFF: pyairtouch.api.AcPowerState.OFF,
    ac_status_msg.AcPowerState.ON: pyairtouch.api.AcPowerState.ON,
    ac_status_msg.AcPowerState.OFF_AWAY: pyairtouch.api.AcPowerState.OFF_AWAY,
    ac_status_msg.AcPowerState.ON_AWAY: pyairtouch.api.AcPowerState.ON_AWAY,
    ac_status_msg.AcPowerState.SLEEP: pyairtouch.api.AcPowerState.SLEEP,
    ac_status_msg.AcPowerState.OFF_FORCED: pyairtouch.api.AcPowerState.OFF_FORCED,
}
_API_POWER_CONTROL_MAPPING = {
    pyairtouch.api.AcPowerControl.TOGGLE: ac_ctrl_msg.AcPowerControl.TOGGLE,
    pyairtouch.api.AcPowerControl.TURN_OFF: ac_ctrl_msg.AcPowerControl.TURN_OFF,
    pyairtouch.api.AcPowerControl.TURN_ON: ac_ctrl_msg.AcPowerControl.TURN_ON,
    pyairtouch.api.AcPowerControl.SET_TO_AWAY: ac_ctrl_msg.AcPowerControl.SET_TO_AWAY,
    pyairtouch.api.AcPowerControl.SET_TO_SLEEP: ac_ctrl_msg.AcPowerControl.SET_TO_SLEEP,
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
_AC_SELECTED_FAN_SPEED_MAPPING = {
    ac_status_msg.AcFanSpeed.AUTO: pyairtouch.api.AcFanSpeed.AUTO,
    ac_status_msg.AcFanSpeed.QUIET: pyairtouch.api.AcFanSpeed.QUIET,
    ac_status_msg.AcFanSpeed.LOW: pyairtouch.api.AcFanSpeed.LOW,
    ac_status_msg.AcFanSpeed.MEDIUM: pyairtouch.api.AcFanSpeed.MEDIUM,
    ac_status_msg.AcFanSpeed.HIGH: pyairtouch.api.AcFanSpeed.HIGH,
    ac_status_msg.AcFanSpeed.POWERFUL: pyairtouch.api.AcFanSpeed.POWERFUL,
    ac_status_msg.AcFanSpeed.TURBO: pyairtouch.api.AcFanSpeed.TURBO,
    # All Intelligent Auto fan speeds indicate Intelligent Auto was selected.
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_AUTO: (
        pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_QUIET: (
        pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_LOW: (
        pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_MEDIUM: (
        pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_HIGH: (
        pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_POWERFUL: (
        pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_TURBO: (
        pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO
    ),
}
_AC_ACTIVE_FAN_SPEED_MAPPING = {
    ac_status_msg.AcFanSpeed.AUTO: pyairtouch.api.AcFanSpeed.AUTO,
    ac_status_msg.AcFanSpeed.QUIET: pyairtouch.api.AcFanSpeed.QUIET,
    ac_status_msg.AcFanSpeed.LOW: pyairtouch.api.AcFanSpeed.LOW,
    ac_status_msg.AcFanSpeed.MEDIUM: pyairtouch.api.AcFanSpeed.MEDIUM,
    ac_status_msg.AcFanSpeed.HIGH: pyairtouch.api.AcFanSpeed.HIGH,
    ac_status_msg.AcFanSpeed.POWERFUL: pyairtouch.api.AcFanSpeed.POWERFUL,
    ac_status_msg.AcFanSpeed.TURBO: pyairtouch.api.AcFanSpeed.TURBO,
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_AUTO: (pyairtouch.api.AcFanSpeed.AUTO),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_QUIET: (pyairtouch.api.AcFanSpeed.QUIET),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_LOW: (pyairtouch.api.AcFanSpeed.LOW),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_MEDIUM: (
        pyairtouch.api.AcFanSpeed.MEDIUM
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_HIGH: (pyairtouch.api.AcFanSpeed.HIGH),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_POWERFUL: (
        pyairtouch.api.AcFanSpeed.POWERFUL
    ),
    ac_status_msg.AcFanSpeed.INTELLIGENT_AUTO_TURBO: (pyairtouch.api.AcFanSpeed.TURBO),
}
_API_FAN_SPEED_CONTROL_MAPPING = {
    pyairtouch.api.AcFanSpeed.AUTO: ac_ctrl_msg.AcFanSpeedControl.AUTO,
    pyairtouch.api.AcFanSpeed.QUIET: ac_ctrl_msg.AcFanSpeedControl.QUIET,
    pyairtouch.api.AcFanSpeed.LOW: ac_ctrl_msg.AcFanSpeedControl.LOW,
    pyairtouch.api.AcFanSpeed.MEDIUM: ac_ctrl_msg.AcFanSpeedControl.MEDIUM,
    pyairtouch.api.AcFanSpeed.HIGH: ac_ctrl_msg.AcFanSpeedControl.HIGH,
    pyairtouch.api.AcFanSpeed.POWERFUL: ac_ctrl_msg.AcFanSpeedControl.POWERFUL,
    pyairtouch.api.AcFanSpeed.TURBO: ac_ctrl_msg.AcFanSpeedControl.TURBO,
    pyairtouch.api.AcFanSpeed.INTELLIGENT_AUTO: (
        ac_ctrl_msg.AcFanSpeedControl.INTELLIGENT_AUTO
    ),
}
_API_TIMER_TYPE_MAPPING = {
    pyairtouch.api.AcTimerType.OFF_TIMER: quick_timer_msg.TimerType.OFF_TIMER,
    pyairtouch.api.AcTimerType.ON_TIMER: quick_timer_msg.TimerType.ON_TIMER,
}


class At5AirConditioner(pyairtouch.api.AirConditioner):
    """An AirTouch 5 implementation of the AirConditioner protocol."""

    def __init__(
        self,
        ac_number: int,
        zones: Sequence[At5Zone],
        ac_ability: AcAbility,
        socket: pyairtouch.comms.socket.AirTouchSocket[
            pyairtouch.at5.comms.hdr.At5Header
        ],
    ) -> None:
        """Initialise an AirTouch 5 Air-Conditioner.

        Args:
            ac_id: The ID of the air-conditioner.
            zones: The AirTouch zones associated with this air-conditioner.
            ac_ability: The functions supported by this air-conditioner.
            socket: Socket for communicating with the AirTouch 5.
        """
        self._ac_status = ac_status_msg.AcStatusData(
            ac_number=ac_number,
            power_state=ac_status_msg.AcPowerState.OFF,
            mode=ac_status_msg.AcMode.AUTO,
            fan_speed=ac_status_msg.AcFanSpeed.AUTO,
            turbo_active=False,
            bypass_active=False,
            spill_active=False,
            timer_set=False,
            set_point=0.0,
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
        self._supported_modes: list[pyairtouch.api.AcMode] = [
            api_mode
            for api_mode, ac_mode in _API_MODE_CONTROL_MAPPING.items()
            if self._ac_ability.ac_mode_support[ac_mode]
        ]
        self._supported_fan_speeds: list[pyairtouch.api.AcFanSpeed] = [
            api_fan_speed
            for api_fan_speed, ac_fan_speed in (_API_FAN_SPEED_CONTROL_MAPPING.items())
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
                    message=ExtendedMessage(
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
    def power_state(self) -> pyairtouch.api.AcPowerState | None:
        return _AC_POWER_STATE_MAPPING.get(self._ac_status.power_state)

    @override
    @property
    def selected_mode(self) -> pyairtouch.api.AcMode | None:
        return _AC_SELECTED_MODE_MAPPING.get(self._ac_status.mode)

    @override
    @property
    def active_mode(self) -> pyairtouch.api.AcMode | None:
        return _AC_ACTIVE_MODE_MAPPING.get(self._ac_status.mode)

    @override
    @property
    def selected_fan_speed(self) -> pyairtouch.api.AcFanSpeed | None:
        return _AC_SELECTED_FAN_SPEED_MAPPING.get(self._ac_status.fan_speed)

    @override
    @property
    def active_fan_speed(self) -> pyairtouch.api.AcFanSpeed | None:
        return _AC_ACTIVE_FAN_SPEED_MAPPING.get(self._ac_status.fan_speed)

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
        match self._ac_status.mode:
            case ac_status_msg.AcMode.HEAT:
                return self._ac_ability.min_heat_set_point
            case ac_status_msg.AcMode.COOL:
                return self._ac_ability.min_cool_set_point
            case _:
                # Really only for the auto modes, but also used for modes that
                # don't support set_points.
                return min(
                    self._ac_ability.min_heat_set_point,
                    self._ac_ability.min_cool_set_point,
                )

    @override
    @property
    def max_target_temperature(self) -> float:
        match self._ac_status.mode:
            case ac_status_msg.AcMode.HEAT:
                return self._ac_ability.max_heat_set_point
            case ac_status_msg.AcMode.COOL:
                return self._ac_ability.max_cool_set_point
            case _:
                # Really only for the auto modes, but also used for modes that
                # don't support set_points.
                return max(
                    self._ac_ability.max_heat_set_point,
                    self._ac_ability.max_cool_set_point,
                )

    @override
    @property
    def spill_state(self) -> pyairtouch.api.AcSpillState:
        if self._ac_status.spill_active:
            return pyairtouch.api.AcSpillState.SPILL
        if self._ac_status.bypass_active:
            return pyairtouch.api.AcSpillState.BYPASS
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
    async def set_mode(
        self, mode: pyairtouch.api.AcMode, power_on: bool = False
    ) -> None:
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
        # Round to the correct resolution.
        rounded_temperature = round(temperature, ndigits=1)
        # Clip the temperature to remain with the min/max values.
        clipped_temperature = min(
            max(self.min_target_temperature, rounded_temperature),
            self.max_target_temperature,
        )
        await self._send_ac_control_message(set_point=clipped_temperature)

    @override
    async def set_quick_timer(
        self,
        timer_type: pyairtouch.api.AcTimerType,
        value: datetime.time | datetime.timedelta,
    ) -> None:
        match value:
            case datetime.timedelta():
                await self._socket.send(
                    message=ExtendedMessage(
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
                new_timer = ac_timer_status_msg.AcTimerState(
                    disabled=False,
                    hour=value.hour,
                    minute=value.minute,
                )
                await self._send_ac_timer_control_message(timer_type, new_timer)

            case _:
                raise ValueError(f"value of type '{type(value)}' is unsupported")

    @override
    async def clear_quick_timer(self, timer_type: pyairtouch.api.AcTimerType) -> None:
        new_timer = ac_timer_status_msg.AcTimerState(
            disabled=True,
            hour=0,
            minute=0,
        )
        await self._send_ac_timer_control_message(timer_type, new_timer)

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
        set_point: float | None = None,
    ) -> None:
        message = ControlStatusMessage(
            ac_ctrl_msg.AcControlMessage(
                [
                    ac_ctrl_msg.AcControlData(
                        ac_number=self.ac_id,
                        power=power,
                        mode=mode,
                        fan_speed=fan_speed,
                        set_point=set_point,
                    )
                ]
            )
        )
        retry_config = pyairtouch.comms.socket.RETRY_IDEMPOTENT
        if power == ac_ctrl_msg.AcPowerControl.TOGGLE:
            retry_config = pyairtouch.comms.socket.RETRY_NON_IDEMPOTENT
        await self._socket.send(message, retry_config)

    async def _send_ac_timer_control_message(
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
            message=ControlStatusMessage(
                sub_message=ac_timer_ctrl_msg.AcTimerControlMessage(
                    ac_timer_status=[
                        ac_timer_ctrl_msg.AcTimerControlData(
                            ac_number=self.ac_id,
                            on_timer=on_timer,
                            off_timer=off_timer,
                        )
                    ]
                )
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
    # ↓ Receive ConsoleVersionMessage, send ZoneNamesRequest
    INIT_ZONE_NAMES = auto()
    # ↓ Receive ZoneNamesMessage, send AcAbilityRequest
    INIT_AC_ABILITY = auto()
    # ↓ Receive AcAbilityMessage, send AcStatusRequest
    INIT_AC_STATUS = auto()
    # ↓ Receive AcStatus, send AcTimerStatusRequest
    INIT_AC_TIMER_STATUS = auto()
    # ↓ Receive AcTimerStatus, send ZoneStatusRequest
    INIT_ZONE_STATUS = auto()
    # ↓ Receive ZoneStatusMessage
    CONNECTED = auto()


DEFAULT_PORT_NUMBER = 9005
"""Default port number for communicating with the AirTouch controller.

This port number is statically defined within the interface specification.
"""


class AirTouch5(pyairtouch.api.AirTouch):
    """The main entrypoint for the AirTouch 5 API."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        airtouch_id: str,
        serial: str,
        name: str,
        socket: pyairtouch.comms.socket.AirTouchSocket[
            pyairtouch.at5.comms.hdr.At5Header
        ],
    ) -> None:
        """Initialise the AirTouch 5 object.

        Args:
            airtouch_id: The ID of the primary AirTouch controller.
            serial: The serial number for the primary AirTouch controller.
            name: The human readable name for the AirTouch system.
            socket: The socket for communicating with the AirTouch.
                This class will take over ownership of the socket to manage the
                connection state.
        """
        self._airtouch_id = airtouch_id
        self._serial = serial
        self._name = name
        self._socket = socket

        # Using the console version request as a heartbeat also ensures that we
        # receive timely notifications when an update is available.
        def is_heartbeat_response(message: pyairtouch.comms.Message) -> bool:
            if isinstance(message, ExtendedMessage):
                # Use a local variable to keep mypy happy.
                # mypy thinks message is of type ExtendedMessage[Any]
                sub_message: pyairtouch.comms.Message = message.sub_message
                return sub_message.message_id == console_ver_msg.MESSAGE_ID
            return False

        self._heartbeat_manager = pyairtouch.comms.heartbeat.HeartbeatManager(
            loop=loop,
            socket=socket,
            config=pyairtouch.comms.heartbeat.HeartbeatConfig(
                message=ExtendedMessage(console_ver_msg.ConsoleVersionRequest()),
                response_match=is_heartbeat_response,
            ),
        )

        self._console_version = console_ver_msg.ConsoleVersionMessage(
            update_available=False,
            versions=[],
        )

        self._air_conditioners: dict[int, At5AirConditioner] = {}
        self._zones: dict[int, At5Zone] = {}

        self._state = _AirTouchState.CLOSED
        self._initialised_event = asyncio.Event()

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
        return pyairtouch.api.AirTouchModel.AIRTOUCH_5

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
            message=ExtendedMessage(console_ver_msg.ConsoleVersionRequest()),
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
            console_version_request = ExtendedMessage(
                console_ver_msg.ConsoleVersionRequest()
            )
            await self._socket.send(
                message=console_version_request,
                retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
            )
        elif connected:
            # Request the latest status in case we've been disconnected for a
            # while.
            await self._socket.send(
                message=ControlStatusMessage(ac_status_msg.AcStatusRequest()),
                retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
            )
            await self._socket.send(
                message=ControlStatusMessage(zone_status_msg.ZoneStatusRequest()),
                retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
            )

    async def _message_received(  # noqa: C901, PLR0912
        self,
        header: pyairtouch.at5.comms.hdr.At5Header,
        message: pyairtouch.comms.Message,
    ) -> None:
        # Process messages according to the current state.
        # Unhandled messages are silently ignored.
        match message:
            case ExtendedMessage(console_ver_msg.ConsoleVersionMessage()) if (
                self._state == _AirTouchState.INIT_VERSION
            ):
                self._console_version = message.sub_message
                # Move to the next state
                self._state = _AirTouchState.INIT_ZONE_NAMES
                zone_names_request = ExtendedMessage(
                    ZoneNamesRequest(zone_number="ALL")
                )
                await self._socket.send(
                    message=zone_names_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ExtendedMessage(ZoneNamesMessage(zone_names)) if (
                self._state == _AirTouchState.INIT_ZONE_NAMES
            ):
                self._process_zone_names_message(zone_names)
                # Move to the next state
                self._state = _AirTouchState.INIT_AC_ABILITY
                ability_request = ExtendedMessage(AcAbilityRequest(ac_number="ALL"))
                await self._socket.send(
                    message=ability_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ExtendedMessage(ZoneNamesRequest()) if (
                header.to_address == pyairtouch.at5.comms.hdr.ADDRESS_CLIENT
                and self._state == _AirTouchState.INIT_ZONE_NAMES
            ):
                # This response may be received for AirTouch systems with no
                # zones configured. Refer to docs/design.md.
                self._state = _AirTouchState.INIT_AC_ABILITY
                ability_request = ExtendedMessage(AcAbilityRequest(ac_number="ALL"))
                await self._socket.send(
                    message=ability_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ExtendedMessage(AcAbilityMessage(ac_abilities)) if (
                self._state == _AirTouchState.INIT_AC_ABILITY
            ):
                self._process_ac_ability_message(ac_abilities)
                # Move to the next state
                self._state = _AirTouchState.INIT_AC_STATUS
                ac_status_request = ControlStatusMessage(
                    ac_status_msg.AcStatusRequest()
                )
                await self._socket.send(
                    message=ac_status_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ControlStatusMessage(ac_status_msg.AcStatusMessage(ac_statuses)) if (
                self._state == _AirTouchState.INIT_AC_STATUS
            ):
                await self._process_ac_status_message(ac_statuses)
                # Move to the next state
                self._state = _AirTouchState.INIT_AC_TIMER_STATUS
                ac_timer_status_request = ControlStatusMessage(
                    ac_timer_status_msg.AcTimerStatusRequest()
                )
                await self._socket.send(
                    message=ac_timer_status_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ControlStatusMessage(
                ac_timer_status_msg.AcTimerStatusMessage(ac_timer_statuses)
            ) if self._state == _AirTouchState.INIT_AC_TIMER_STATUS:
                await self._process_ac_timer_status_message(ac_timer_statuses)
                # Move to the next state
                self._state = _AirTouchState.INIT_ZONE_STATUS
                zone_status_request = ControlStatusMessage(
                    zone_status_msg.ZoneStatusRequest()
                )
                await self._socket.send(
                    message=zone_status_request,
                    retry_policy=pyairtouch.comms.socket.RETRY_CONNECTED,
                )

            case ControlStatusMessage(
                zone_status_msg.ZoneStatusMessage(zone_statuses)
            ) if self._state == _AirTouchState.INIT_ZONE_STATUS:
                await self._process_zone_status_message(zone_statuses)
                # Move to the next state
                self._state = _AirTouchState.CONNECTED
                await self._heartbeat_manager.start()
                self._initialised_event.set()

            case ControlStatusMessage(zone_status_msg.ZoneStatusRequest()) if (
                header.to_address == pyairtouch.at5.comms.hdr.ADDRESS_CLIENT
                and self._state == _AirTouchState.INIT_ZONE_STATUS
            ):
                # This response may be received for AirTouch systems with no
                # zones configured. Refer to docs/design.md.
                self._state = _AirTouchState.CONNECTED
                await self._heartbeat_manager.start()
                self._initialised_event.set()

            case ControlStatusMessage(ac_status_msg.AcStatusMessage(ac_statuses)) if (
                self._state == _AirTouchState.CONNECTED
            ):
                await self._process_ac_status_message(ac_statuses)

            case ControlStatusMessage(
                ac_timer_status_msg.AcTimerStatusMessage(ac_timer_statuses)
            ) if self._state == _AirTouchState.CONNECTED:
                await self._process_ac_timer_status_message(ac_timer_statuses)

            case ControlStatusMessage(
                zone_status_msg.ZoneStatusMessage(zone_statuses)
            ) if self._state == _AirTouchState.CONNECTED:
                await self._process_zone_status_message(zone_statuses)

            case ExtendedMessage(console_ver_msg.ConsoleVersionMessage()) if (
                self._state == _AirTouchState.CONNECTED
            ):
                await self._process_console_version_update(message.sub_message)

            case ExtendedMessage(err_info_msg.AcErrorInformationMessage()):
                await self._process_ac_error_info_message(message.sub_message)

    def _process_zone_names_message(self, zone_names: Mapping[int, str]) -> None:
        for zone_number, zone_name in zone_names.items():
            self._zones[zone_number] = At5Zone(
                zone_number=zone_number,
                zone_name=zone_name,
                socket=self._socket,
            )

    def _process_ac_ability_message(self, ac_abilities: Sequence[AcAbility]) -> None:
        # With multiple ac's, the start/count values might look like:
        # AC1: start_zone:0, zone_count: 3
        # AC2: start_zone:3, zone_count: 2
        # AC3: start_zone:5, zone_count: 3
        for ac in ac_abilities:
            ac_zones = [
                self._zones[zone_id]
                for zone_id in range(ac.start_zone, ac.start_zone + ac.zone_count)
            ]
            self._air_conditioners[ac.ac_number] = At5AirConditioner(
                ac_number=ac.ac_number,
                zones=ac_zones,
                ac_ability=ac,
                socket=self._socket,
            )

    async def _process_ac_status_message(
        self, ac_statuses: Sequence[ac_status_msg.AcStatusData]
    ) -> None:
        for ac_status in ac_statuses:
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
                _LOGGER.warning(
                    "Unknown AC in AC Timer Status: %d", ac_timer_status.ac_number
                )

    async def _process_ac_error_info_message(
        self, ac_error_info: err_info_msg.AcErrorInformationMessage
    ) -> None:
        ac_instance = self._air_conditioners.get(ac_error_info.ac_number)
        if ac_instance:
            await ac_instance.update_ac_error_info(ac_error_info.error_info)

    async def _process_zone_status_message(
        self, zone_statuses: Sequence[zone_status_msg.ZoneStatusData]
    ) -> None:
        for zone_status in zone_statuses:
            zone_instance = self._zones.get(zone_status.zone_number)
            if zone_instance:
                await zone_instance.update_zone_status(zone_status)
            else:
                _LOGGER.warning(
                    "Unknown Zone in Zone Status: %d", zone_status.zone_number
                )

    async def _process_console_version_update(
        self, console_version: console_ver_msg.ConsoleVersionMessage
    ) -> None:
        old_version = self._console_version
        self._console_version = console_version
        if old_version != console_version:
            await _notify_subscribers([s(self._airtouch_id) for s in self._subscribers])


async def _notify_subscribers(callbacks: Iterable[Awaitable[Any]]) -> None:
    for coro in asyncio.as_completed(callbacks):
        try:
            _ = await coro
        except Exception:
            _LOGGER.exception("Exception from subscriber")
