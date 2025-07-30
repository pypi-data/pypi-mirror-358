import abc
import collections.abc

import typing_extensions as typing

from ..fdl import Deserializer, Serializer

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List, Native

T = typing.TypeVar("T", bound="Native", contravariant=True)


class Constraint(typing.Generic[T], metaclass=abc.ABCMeta):
    """
    This class serves as a generic super class for all constraints
    that enforce specific rules on the values they validate. Any
    subclass must implement the `validate` method to define the
    validation logic for the specific constraint.
    """

    @abc.abstractmethod
    async def validate(self, value: T) -> bool:
        """
        Validate the provided value against the constraint's rules.

        Args:
          value: The value to be validated.

        Returns:
          True if the value is valid according to the constraint.

        Raises:
          TypeError: If the provided value is not in the correct type.
          ValueError: If the provided value violates the constraints.
        """

    @abc.abstractmethod
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the SiLA constraint into the xml-based feature language
        definition.

        Args:
          serializer: The serializer instance used to write xml tokens.
        """

    @classmethod
    @abc.abstractmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        """
        Deserialize the xml-based feature language definition into SiLA
        constraints.

        Args:
          deserializer: The deserializer instance used to read xml
            tokens.

        Raises:
          ValueError: If an invalid or unexpected token is detected.
        """
