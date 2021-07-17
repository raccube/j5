"""Classes for supporting toggleable power output channels."""

from abc import abstractmethod
from typing import Iterator, Mapping, Type, TypeVar

from j5.components.component import Component, Interface


class PowerOutputInterface(Interface):
    """An interface containing the methods required to control a power output channel."""

    @abstractmethod
    def get_power_output_enabled(self, identifier: int) -> bool:
        """Get whether a power output is enabled."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """Set whether a power output is enabled."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_power_output_current(self, identifier: int) -> float:
        """Get the current being drawn on a power output, in amperes."""
        raise NotImplementedError  # pragma: no cover


class PowerOutput(Component):
    """
    A power output channel.

    It can be enabled/disabled, and the current being drawn on this channel can be
    measured.
    """

    def __init__(
        self, identifier: int, backend: PowerOutputInterface,
    ) -> None:
        self._identifier = identifier
        self._backend = backend

    @classmethod
    def interface_class(cls) -> Type[PowerOutputInterface]:
        """Get the interface class that is required to use this component."""
        return PowerOutputInterface

    @property
    def identifier(self) -> int:
        """An integer to identify the component on a board."""
        return self._identifier

    @property
    def is_enabled(self) -> bool:
        """Get whether the output is enabled."""
        return self._backend.get_power_output_enabled(self._identifier)

    @is_enabled.setter
    def is_enabled(self, new_state: bool) -> None:
        """Set whether the output is enabled."""
        self._backend.set_power_output_enabled(self._identifier, new_state)

    @property
    def current(self) -> float:
        """Get the current being drawn on this power output, in amperes."""
        return self._backend.get_power_output_current(self._identifier)


T = TypeVar('T')


class PowerOutputGroup:
    """A group of PowerOutputs."""

    def __init__(self, outputs: Mapping[T, PowerOutput]):
        self._outputs = outputs

    def power_on(self) -> None:
        """Enable all outputs in the group."""
        for output in self._outputs.values():
            output.is_enabled = True

    def power_off(self) -> None:
        """Disable all outputs in the group."""
        for output in self._outputs.values():
            output.is_enabled = False

    def __getitem__(self, index: T) -> PowerOutput:
        """Get an output using list notation."""
        return self._outputs[index]

    def __iter__(self) -> Iterator[PowerOutput]:
        """
        Iterate over the outputs in the group.

        The outputs are in no particular order.
        """
        return iter(self._outputs.values())

    def __len__(self) -> int:
        """Get the number of outputs in the group."""
        return len(self._outputs)
