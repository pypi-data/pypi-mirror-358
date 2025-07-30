import collections.abc
import dataclasses

import typing_extensions as typing

from ..data_types.list import List
from ..fdl import Deserializer, Serializer
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType


@dataclasses.dataclass
class MinimalElementCount(Constraint[list]):
    """
    A constraint that enforces a minimum number of elements in a
    list.

    This constraint ensures that the size of a list is at least the
    specified minimum element count. It raises errors if the provided
    list contains fewer elements than required or if the input is not
    a list. The minimum element count must be a non-negative integer
    and less than 2⁶³.

    Args:
      value: The minimum number of elements that the list must
        contain. It must be a non-negative integer and less than 2⁶³.

    Raises:
      ValueError: If `value` is negative or greater than or equal to
        2⁶³.
    """

    value: int
    """
    The minimum number of elements that the list must contain. It
    must be a non-negative integer and less than 2⁶³.
    """

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"Minimal element count must be a non-negative integer, received '{self.value}'.")
        if self.value >= 2**63:
            raise ValueError(f"Minimal element count must be less than 2⁶³, received '{self.value}'.")

    async def validate(self, value: list) -> bool:
        if not isinstance(value, list):
            raise TypeError(f"Expected value of type 'list', received '{type(value).__name__}'.")

        if len(value) < self.value:
            raise ValueError(f"Expected list with minimal element count '{self.value}', received '{value}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.write_int("MinimalElementCount", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, List):
            raise ValueError(f"Expected constraint's data type to be 'List', received '{data_type.__name__}'.")

        yield from deserializer.read_start_element(name="MinimalElementCount")
        value = yield from deserializer.read_int()
        yield from deserializer.read_end_element(name="MinimalElementCount")

        return cls(value)
