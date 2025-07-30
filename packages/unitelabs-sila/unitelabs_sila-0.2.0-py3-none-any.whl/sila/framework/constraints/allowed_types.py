import collections.abc
import dataclasses

import typing_extensions as typing

from ..data_types.data_type import DataType
from ..fdl import Deserializer, EndElement, Serializer, StartElement
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, DataType, List


@dataclasses.dataclass
class AllowedTypes(Constraint[typing.Any]):
    """
    A constraint that specifies a set of allowed data types for a
    value.

    This class defines a set of permissible data types and raises
    errors if the input value does not match one of the allowed
    types.

    Args:
      values: A sequence of allowed data types that the input value
        must match.
    """

    values: collections.abc.Sequence[type["DataType"]]
    """
    A sequence of allowed data types that the input value must match.
    """

    async def validate(self, value: typing.Any) -> bool:
        # TODO: Validate value is one of the given allowed_types

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.start_element("AllowedTypes")
        for value in self.values:
            value.serialize(serializer)
        serializer.end_element("AllowedTypes")

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        yield from deserializer.read_start_element(name="AllowedTypes")

        data_types: list[type[DataType]] = []
        while True:
            token = yield from deserializer.peek()

            if token == StartElement("DataType"):
                inner_data_type = yield from deserializer.read(DataType.deserialize(deserializer))
                data_types.append(inner_data_type)

            elif token == EndElement("AllowedTypes"):
                break

        yield from deserializer.read_end_element(name="AllowedTypes")

        return cls(data_types)
