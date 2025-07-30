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
class MaximalLength(Constraint[T]):
    """
    A constraint that enforces a maximum length for a value of type
    String or Binary.

    This constraint is used to ensure that a value does not exceed a
    specified maximum length. It raises errors if the value is not of
    the correct type or if the length exceeds the defined limit. The
    maximum length must be a positive integer and less than 2⁶³.

    Args:
      maximal_length: The maximum allowed length for the value. It
        must be a non-negative integer and less than 2⁶³.

    Raises:
      ValueError: If the maximum length (`value`) is negative or
        exceeds 2⁶³.
    """

    value: int
    """
    The maximum allowed length for the value. It must be a
    non-negative integer and less than 2⁶³.
    """

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"Maximal length must be a non-negative integer, received '{self.value}'.")
        if self.value >= 2**63:
            raise ValueError(f"Maximal length must be less than 2⁶³, received '{self.value}'.")

    async def validate(self, value: T) -> bool:
        if not isinstance(value, (str, bytes)):
            raise TypeError(f"Expected value of type 'str' or 'bytes', received '{type(value).__name__}'.")

        if len(value) > self.value:
            raise ValueError(f"Expected value with maximal length '{self.value}', received '{value}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.write_int("MaximalLength", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (String, Binary)):
            raise ValueError(
                f"Expected constraint's data type to be 'String' or 'Binary', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="MaximalLength")
        value = yield from deserializer.read_int()
        yield from deserializer.read_end_element(name="MaximalLength")

        return cls(value)
