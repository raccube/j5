"""Base backend for Arduino Uno and its derivatives."""

from abc import abstractmethod
from datetime import timedelta
from threading import Lock
from typing import Callable, List, Mapping, Optional, Set, Type

from serial import Serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from j5.backends.hardware.env import NotSupportedByHardwareError
from j5.backends.hardware.j5.serial import SerialHardwareBackend
from j5.boards import Board
from j5.boards.j5 import ArduinoUno
from j5.components import GPIOPinInterface, GPIOPinMode, LEDInterface

FIRST_ANALOGUE_PIN = 14


class DigitalPinData:
    """Contains data about a digital pin."""

    mode: GPIOPinMode
    state: bool

    def __init__(self, *, mode: GPIOPinMode, state: bool):
        self.mode = mode
        self.state = state


class ArduinoHardwareBackend(
    LEDInterface,
    GPIOPinInterface,
    SerialHardwareBackend,
):
    """An abstract class to create backends for different Arduinos."""

    board: Type[ArduinoUno]
    DEFAULT_TIMEOUT: timedelta = timedelta(milliseconds=1250)

    @staticmethod
    @abstractmethod
    def is_arduino(port: ListPortInfo) -> bool:
        """Check if a ListPortInfo represents a valid Arduino derivative."""
        raise NotImplementedError

    @classmethod
    def discover(
            cls,
            comports: Callable = comports,
            serial_class: Type[Serial] = Serial,
    ) -> Set[Board]:
        """Discover all connected arduino boards."""
        # Find all serial ports.
        ports: List[ListPortInfo] = comports()

        # Get a list of boards from the ports.
        boards: Set[Board] = set()
        for port in filter(cls.is_arduino, ports):
            boards.add(
                cls.board(
                    port.serial_number,
                    cls(port.device, serial_class),  # type: ignore
                ),
            )

        return boards

    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Serial] = Serial,
            baud: int = 115200,
            timeout: timedelta = DEFAULT_TIMEOUT,
    ) -> None:
        super(ArduinoHardwareBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
            baud=baud,
            timeout=timeout,
        )

        self.serial_port = serial_port

        self._lock = Lock()

        self._digital_pins: Mapping[int, DigitalPinData] = {
            i: DigitalPinData(mode=GPIOPinMode.DIGITAL_INPUT, state=False)
            for i in range(2, FIRST_ANALOGUE_PIN)
        }

        with self._lock:
            self._version_line = self._verify_boot()

        self._verify_firmware_version()

        for pin_number in self._digital_pins.keys():
            self.set_gpio_pin_mode(pin_number, GPIOPinMode.DIGITAL_INPUT)

    @abstractmethod
    def _verify_boot(self) -> str:
        """Verify that the Arduino has booted and return its version string."""
        raise NotImplementedError

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        raise NotImplementedError

    @abstractmethod
    def _verify_firmware_version(self) -> None:
        """Verify that the Arduino firmware meets or exceeds the minimum version."""
        raise NotImplementedError

    @abstractmethod
    def _update_digital_pin(self, identifier: int) -> None:
        """Write the stored value of a digital pin to the Arduino."""
        raise NotImplementedError

    @abstractmethod
    def _read_digital_pin(self, identifier: int) -> bool:
        """Read the value of a digital pin from the Arduino."""
        raise NotImplementedError

    @abstractmethod
    def _read_analogue_pin(self, identifier: int) -> float:
        """Read the value of an analogue pin from the Arduino."""
        raise NotImplementedError

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """Set the hardware mode of a GPIO pin."""
        digital_pin_modes = {
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
            GPIOPinMode.DIGITAL_OUTPUT,
        }
        if identifier < FIRST_ANALOGUE_PIN:
            # Digital pin
            if pin_mode in digital_pin_modes:
                self._digital_pins[identifier].mode = pin_mode
                self._update_digital_pin(identifier)
                return
        else:
            # Analogue pin
            if pin_mode is GPIOPinMode.ANALOGUE_INPUT:
                return
        raise NotSupportedByHardwareError(
            f"{self.board.name} does not support mode {pin_mode} on pin {identifier}.",
        )

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the hardware mode of a GPIO pin."""
        if identifier < FIRST_ANALOGUE_PIN:
            return self._digital_pins[identifier].mode
        else:
            return GPIOPinMode.ANALOGUE_INPUT

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """Write to the digital state of a GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT "
                             f"in order to set the digital state.")
        self._digital_pins[identifier].state = state
        self._update_digital_pin(identifier)

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Get the last written state of the GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins.",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT "
                             f"in order to read the digital state.")
        return self._digital_pins[identifier].state

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Read the digital state of the GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins.",
            )
        if self._digital_pins[identifier].mode not in (
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
        ):
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_INPUT_* "
                             f"in order to read the digital state.")
        return self._read_digital_pin(identifier)

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """Read the analogue voltage of the GPIO pin."""
        if identifier < FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Analogue functions not supported on digital pins.",
            )
        return self._read_analogue_pin(identifier)

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """Write a scaled analogue value to the DAC on the GPIO pin."""
        raise NotSupportedByHardwareError(f"{self.board.name} does not have a DAC.")

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """Write a scaled analogue value to the PWM on the GPIO pin."""
        raise NotSupportedByHardwareError(
            f"{self.board.name} firmware does not implement PWM output.",
        )

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        if identifier != 0:
            raise ValueError(f"{self.board.name} only has LED 0 (digital pin 13).")
        return self.get_gpio_pin_digital_state(13)

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        if identifier != 0:
            raise ValueError(f"{self.board.name} only has LED 0 (digital pin 13).")
        self.write_gpio_pin_digital_state(13, state)
