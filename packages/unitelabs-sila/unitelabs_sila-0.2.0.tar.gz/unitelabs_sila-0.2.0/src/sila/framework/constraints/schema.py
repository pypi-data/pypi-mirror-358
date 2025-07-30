import builtins
import collections.abc
import dataclasses
import enum

import typing_extensions as typing

from ..data_types.binary import Binary
from ..data_types.string import String
from ..fdl import Characters, Deserializer, EndElement, Serializer, StartElement
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List

T = typing.TypeVar("T", str, bytes)


class SchemaType(str, enum.Enum):
    """
    Enumeration of schema types used in the Schema constraint.

    This enumeration defines the types of schemas that can be used
    for validation. It currently supports XML and JSON.
    """

    XML = "Xml"
    """Represents the XML schema type."""

    JSON = "Json"
    """Represents the JSON schema type."""


@dataclasses.dataclass
class Schema(Constraint[T]):
    """
    A constraint that enforces the structure of a value to match a
    specific schema, either XML or JSON.

    This class allows validation of a string or bytes object against
    a specific schema type (XML or JSON). The schema can either be
    provided via a URL or inline content.

    Args:
      type: The schema type, either 'Xml' or 'Json'.
      url: An optional URL pointing to the schema.
      inline: Optional inline content representing the schema.
    """

    Type: typing.ClassVar[builtins.type[SchemaType]] = SchemaType
    """
    Enumeration of schema types used in the Schema constraint.
    """

    type: typing.Literal["Xml", "Json"]
    """
    The schema type, either 'Xml' or 'Json'.
    """

    url: typing.Optional[str] = None
    """
    An optional URL pointing to the schema.
    """

    inline: typing.Optional[str] = None
    """
    Optional inline content representing the schema.
    """

    def __post_init__(self):
        if self.url is None and self.inline is None:
            raise ValueError("Either 'url' or 'inline' must be provided.")

        if self.url is not None and self.inline is not None:
            raise ValueError("'url' and 'inline' cannot both be provided.")

        self.type = self.type.value if isinstance(self.type, SchemaType) else self.type

    async def validate(self, value: T) -> bool:
        if not isinstance(value, (str, bytes)):
            raise TypeError(f"Expected value of type 'str' or 'bytes', received '{type(value).__name__}'.")

        # TODO: Load xml or json schema to validate whether `value` follows that schema

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.start_element("Schema")
        serializer.write_str("Type", self.type)
        if self.url is not None:
            serializer.write_str("Url", self.url)
        if self.inline is not None:
            serializer.write_str("Inline", self.inline)
        serializer.end_element("Schema")

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[builtins.type["BasicType"], builtins.type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (String, Binary)):
            raise ValueError(
                f"Expected constraint's data type to be 'String' or 'Binary', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="Schema")

        # Type
        yield from deserializer.read_start_element(name="Type")
        type = yield from deserializer.read_str()
        try:
            type = SchemaType(type).value
        except ValueError:
            raise ValueError(f"Expected a valid 'Type' value, received '{type}'.") from None
        yield from deserializer.read_end_element(name="Type")

        url: typing.Optional[str] = None
        inline: typing.Optional[str] = None

        token = yield
        if isinstance(token, StartElement):
            if token.name == "Url":
                # Url
                url = yield from deserializer.read_str()
                yield from deserializer.read_end_element(name="Url")
            elif token.name == "Inline":
                # Inline
                inline = yield from deserializer.read_str()
                yield from deserializer.read_end_element(name="Inline")
            else:
                raise ValueError(
                    f"Expected start element with name 'Url' or 'Inline', received start element with name '{token.name}'."
                )
        elif isinstance(token, Characters):
            raise ValueError(
                f"Expected start element with name 'Url' or 'Inline', received characters '{token.value}'."
            )
        elif isinstance(token, EndElement):
            raise ValueError(
                f"Expected start element with name 'Url' or 'Inline', received end element with name '{token.name}'."
            )

        yield from deserializer.read_end_element(name="Schema")

        return cls(type, url=url, inline=inline)
