import collections.abc
import dataclasses

import typing_extensions as typing

from ..data_types.list import List
from ..fdl import Deserializer, Serializer
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType


@dataclasses.dataclass
class MaximalElementCount(Constraint[list]):
    """
    A constraint that enforces a maximum number of elements in a
    list.

    This constraint ensures that the size of a list does not exceed
    the specified maximum element count. It raises errors if the
    provided list exceeds the defined limit, or if the input is not a
    list. The maximum element count must be a non-negative integer
    and less than 2⁶³.

    Args:
      value: The maximum number of elements allowed in the list. It
        must be a non-negative integer and less than 2⁶³.

    Raises:
      ValueError: If `value` is negative or greater than or equal to
        2⁶³.
    """

    value: int
    """
    The maximum number of elements allowed in the list. It must
    be a non-negative integer and less than 2⁶³.
    """

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"Maximal element count must be a non-negative integer, received '{self.value}'.")
        if self.value >= 2**63:
            raise ValueError(f"Maximal element count must be less than 2⁶³, received '{self.value}'.")

    async def validate(self, value: list) -> bool:
        if not isinstance(value, list):
            raise TypeError(f"Expected value of type 'list', received '{type(value).__name__}'.")

        if len(value) > self.value:
            raise ValueError(f"Expected list with maximal element count '{self.value}', received '{value}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.write_int("MaximalElementCount", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, List):
            raise ValueError(f"Expected constraint's data type to be 'List', received '{data_type.__name__}'.")

        yield from deserializer.read_start_element(name="MaximalElementCount")
        value = yield from deserializer.read_int()
        yield from deserializer.read_end_element(name="MaximalElementCount")

        return cls(value)
