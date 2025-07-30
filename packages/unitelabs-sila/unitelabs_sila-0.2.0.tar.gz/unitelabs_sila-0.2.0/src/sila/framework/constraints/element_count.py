import collections.abc
import dataclasses

import typing_extensions as typing

from ..data_types.list import List
from ..fdl import Deserializer, Serializer
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType


@dataclasses.dataclass
class ElementCount(Constraint[list]):
    """
    A constraint that enforces an exact element count for a list.

    This constraint ensures that a given list contains exactly the
    specified number of elements. It raises errors if the input is
    not a list or if the list contains a number of elements different
    from the expected count.

    Args:
      value: The exact number of elements the list must contain. Must
        be a non-negative integer and less than 2⁶³.

    Raises:
      ValueError: If `value` is negative or exceeds 2⁶³.
    """

    value: int
    """
    The exact number of elements the list must contain. Must be a
    non-negative integer and less than 2⁶³.
    """

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"Element count must be a non-negative integer, received '{self.value}'.")
        if self.value >= 2**63:
            raise ValueError(f"Element count must be less than 2⁶³, received '{self.value}'.")

    async def validate(self, value: list) -> bool:
        if not isinstance(value, list):
            raise TypeError(f"Expected value of type 'list', received '{type(value).__name__}'.")

        if len(value) != self.value:
            raise ValueError(f"Expected list with element count '{self.value}', received '{value}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.write_int("ElementCount", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, List):
            raise ValueError(f"Expected constraint's data type to be 'List', received '{data_type.__name__}'.")

        yield from deserializer.read_start_element(name="ElementCount")
        value = yield from deserializer.read_int()
        yield from deserializer.read_end_element(name="ElementCount")

        return cls(value)
