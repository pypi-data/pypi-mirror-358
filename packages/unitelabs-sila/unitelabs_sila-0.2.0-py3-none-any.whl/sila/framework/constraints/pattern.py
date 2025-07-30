import collections.abc
import dataclasses
import re

import typing_extensions as typing

from ..data_types.string import String
from ..fdl import Deserializer, Serializer
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List


@dataclasses.dataclass
class Pattern(Constraint[str]):
    """
    A constraint that enforces a specific regular expression pattern
    for a string value.

    This constraint ensures that a given string matches a specified
    regular expression pattern. It raises errors if the input value
    is not a string or if the string does not match the defined
    pattern.

    Args:
      value: The regular expression pattern that the string value
        must match.
    """

    value: str
    """
    The regular expression pattern that the string value must
    match.
    """

    async def validate(self, value: str) -> bool:
        if not isinstance(value, str):
            raise TypeError(f"Expected value of type 'str', received '{type(value).__name__}'.")

        if not re.fullmatch(self.value, value):
            raise ValueError(f"Value '{value}' does not match the pattern: '{self.value}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.write_str("Pattern", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, String):
            raise ValueError(f"Expected constraint's data type to be 'String', received '{data_type.__name__}'.")

        yield from deserializer.read_start_element(name="Pattern")
        value = yield from deserializer.read_str()
        yield from deserializer.read_end_element(name="Pattern")

        return cls(value)
