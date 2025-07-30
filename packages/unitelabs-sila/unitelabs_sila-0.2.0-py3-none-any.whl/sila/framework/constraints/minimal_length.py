import collections.abc
import dataclasses

import typing_extensions as typing

from ..data_types.binary import Binary
from ..data_types.string import String
from ..fdl import Deserializer, Serializer
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List

T = typing.TypeVar("T", str, bytes)


@dataclasses.dataclass
class MinimalLength(Constraint[T]):
    """
    A constraint that enforces a minimum length for a value of type
    String or Binary.

    This constraint is used to ensure that a value is not shorter
    than a specified minimum length. It raises errors if the value is
    not of the correct type or if the length is less than the defined
    limit. The minimum length must be a positive integer and less
    than 2⁶³.

    Args:
      value: The minimum allowed length for the value. Must be a
        non-negative integer and less than 2⁶³.

    Raises:
      ValueError: If `value` is negative or exceeds 2⁶³.
    """

    value: int
    """
    The minimum allowed length for the value. Must be a
    non-negative integer and less than 2⁶³.
    """

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"Minimal length must be a non-negative integer, received '{self.value}'.")
        if self.value >= 2**63:
            raise ValueError(f"Minimal length must be less than 2⁶³, received '{self.value}'.")

    async def validate(self, value: T) -> bool:
        if not isinstance(value, (str, bytes)):
            raise TypeError(f"Expected value of type 'str' or 'bytes', received '{type(value).__name__}'.")

        if len(value) < self.value:
            raise ValueError(f"Expected value with minimal length '{self.value}', received '{value}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.write_int("MinimalLength", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (String, Binary)):
            raise ValueError(
                f"Expected constraint's data type to be 'String' or 'Binary', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="MinimalLength")
        value = yield from deserializer.read_int()
        yield from deserializer.read_end_element(name="MinimalLength")

        return cls(value)
