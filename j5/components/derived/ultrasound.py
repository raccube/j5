"""
Ultrasonic distance sensor.

A sensor that utilises the reflection of ultrasound to calculate the distance
to a nearby object.
"""

from abc import abstractmethod
from datetime import timedelta
from typing import Optional, Type

from j5.components import NotSupportedByComponentError
from j5.components.component import DerivedComponent, Interface
from j5.components.gpio_pin import GPIOPin


class UltrasoundInterface(Interface):
    """An interface containing the methods required for an UltrasoundSensor."""

    @abstractmethod
    def get_ultrasound_pulse(
            self,
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> Optional[timedelta]:
        """
        Get a timedelta for the ultrasound time.

        Returns None if the sensor times out.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_ultrasound_distance(
            self,
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> Optional[float]:
        """Get a distance in metres."""
        raise NotImplementedError  # pragma: no cover


class UltrasoundSensor(DerivedComponent):
    """
    Ultrasonic distance sensor.

    A sensor that utilises the reflection of ultrasound to calculate the distance
    to a nearby object.
    """

    def __init__(
        self,
        gpio_trigger: GPIOPin,
        gpio_echo: GPIOPin,
        backend: UltrasoundInterface,
        *,
        distance_mode: bool = True,
    ) -> None:

        if self.__class__ not in gpio_trigger.firmware_modes or \
                self.__class__ not in gpio_echo.firmware_modes:
            raise NotSupportedByComponentError(
                f"Pins {gpio_trigger.identifier} and {gpio_echo.identifier}"
                f" must support Ultrasound.",
            )

        self._gpio_trigger = gpio_trigger
        self._gpio_echo = gpio_echo
        self._backend = backend
        self._distance_mode = distance_mode

    @classmethod
    def interface_class(cls) -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        return UltrasoundInterface

    def pulse(self) -> Optional[timedelta]:
        """
        Send a pulse and return the time taken.

        Returns None if timeout occurred.
        """
        return self._backend.get_ultrasound_pulse(
            self._gpio_trigger.identifier,
            self._gpio_echo.identifier,
        )

    def distance(self) -> Optional[float]:
        """
        Send a pulse and return the distance to the object.

        Returns none if a timeout occurred.
        """
        if not self._distance_mode:
            raise Exception("Distance mode is disabled. Use pulse() to get the time.")

        return self._backend.get_ultrasound_distance(
            self._gpio_trigger.identifier,
            self._gpio_echo.identifier,
        )
