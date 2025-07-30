"""An API for interfacing with the Polyaire AirTouch AC controllers.

Uesrs would typically use the ``discover()`` function as the main entrypoint to
automatically discover any AirTouch consoles on the network.

Example:
    To start a connection to an automatically discovered AirTouch::

        import pyairtouch

        discovered = await pyairtouch.discover()
        airtouch = discovered[0] # Using the first discovered AirTouch

        await airtouch.init()

    To start a connection to a specific AirTouch instance::

        from pyairtouch import AirTouchVersion, connect
        airtouch = connect(AirTouchVersion.VERSION_5, "192.168.0.100", 9005)
"""

from pyairtouch.api import (
    AcFanSpeed,
    AcMode,
    AcPowerControl,
    AcPowerState,
    AcSpillState,
    AcTimerType,
    AirConditioner,
    AirTouch,
    AirTouchModel,
    AirTouchSubscriber,
    SensorBatteryStatus,
    UpdateSubscriber,
    Zone,
    ZoneControlMethod,
    ZonePowerState,
)
from pyairtouch.factory import connect, discover

# Explicitly export the public API to satisfy mypy strict type checking.
# fmt: off
__all__ = [
    # Factory functions
    "connect", "discover",

    # API Enumerations
    "AirTouchModel",
    "AcPowerState", "AcPowerControl", "AcMode", "AcFanSpeed", "AcSpillState",
    "AcTimerType",
    "ZonePowerState", "ZoneControlMethod", "SensorBatteryStatus",

    # API Interfaces
    "AirTouchSubscriber", "UpdateSubscriber",
    "Zone", "AirConditioner", "AirTouch"
]
# fmt: on
