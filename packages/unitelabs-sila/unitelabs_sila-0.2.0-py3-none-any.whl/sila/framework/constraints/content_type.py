import builtins
import collections.abc
import dataclasses

import typing_extensions as typing

from ..data_types.binary import Binary
from ..data_types.string import String
from ..fdl import Characters, Deserializer, EndElement, Serializer, StartElement
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List

T = typing.TypeVar("T", str, bytes)


class ContentTypeParameter(typing.NamedTuple):
    """
    Represents a parameter for the content type, consisting of an
    attribute and its corresponding value.

    Args:
      attribute: The name of the parameter attribute, e.g. 'charset'.
      value: The value of the parameter attribute, e.g. 'utf-8'.
    """

    attribute: str
    """The name of the parameter attribute, e.g. 'charset'."""

    value: str
    """The value of the parameter attribute, e.g. 'utf-8'."""


@dataclasses.dataclass(init=False)
class ContentType(Constraint[T]):
    """
    A constraint that defines a media type (content type) with
    optional parameters.

    This class defines the structure of a content type with its type,
    subtype, and optional parameters. It provides a property to
    generate the full media type string and validates that the input
    value is of the appropriate type (`String` or `Binary`).

    Args:
      type: The main type of the content (e.g., 'application',
        'text').
      subtype: The subtype of the content (e.g., 'json', 'html').
      parameters: A list of additional parameters for the content
         type (e.g., 'charset' or 'boundary').
    """

    Parameter: typing.ClassVar[builtins.type[ContentTypeParameter]] = ContentTypeParameter
    """
    Represents a parameter for the content type, consisting of an
    attribute and its corresponding value.
    """

    type: str
    """
    The main type of the content (e.g., 'application', 'text').
    """

    subtype: str
    """
    The subtype of the content (e.g., 'json', 'html').
    """

    parameters: list[ContentTypeParameter] = dataclasses.field(default_factory=list)
    """
    A list of additional parameters for the content type (e.g.,
    'charset' or 'boundary').
    """

    @property
    def media_type(self) -> str:
        """
        The full media type string, including the type, subtype, and any
        additional parameters in the format 'type/subtype; param=value'.
        """

        return f"{self.type}/{self.subtype}" + "".join(
            [f"; {parameter[0]}={parameter[1]}" for parameter in self.parameters]
        )

    def __init__(
        self,
        type: str,
        subtype: str,
        parameters: typing.Optional[
            collections.abc.Sequence[typing.Union[ContentTypeParameter, tuple[str, str]]]
        ] = None,
    ) -> None:
        self.type = type
        self.subtype = subtype
        self.parameters: list[ContentTypeParameter] = [
            parameter
            if isinstance(parameter, ContentTypeParameter)
            else ContentTypeParameter(parameter[0], parameter[1])
            for parameter in parameters or []
        ]

    async def validate(self, value: T) -> bool:
        if not isinstance(value, (str, bytes)):
            raise TypeError(f"Expected value of type 'str' or 'bytes', received '{type(value).__name__}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.start_element("ContentType")
        serializer.write_str("Type", self.type)
        serializer.write_str("Subtype", self.subtype)

        if len(self.parameters):
            serializer.start_element("Parameters")
            for parameter in self.parameters:
                serializer.start_element("Parameter")
                serializer.write_str("Attribute", parameter.attribute)
                serializer.write_str("Value", parameter.value)
                serializer.end_element("Parameter")
            serializer.end_element("Parameters")

        serializer.end_element("ContentType")

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[builtins.type["BasicType"], builtins.type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (String, Binary)):
            raise ValueError(
                f"Expected constraint's data type to be 'String' or 'Binary', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="ContentType")

        # Type
        yield from deserializer.read_start_element(name="Type")
        type = yield from deserializer.read_str()
        yield from deserializer.read_end_element(name="Type")

        # Subtype
        yield from deserializer.read_start_element(name="Subtype")
        subtype = yield from deserializer.read_str()
        yield from deserializer.read_end_element(name="Subtype")

        token = yield

        if isinstance(token, StartElement):
            if token.name != "Parameters":
                raise ValueError(
                    f"Expected start element with name 'Parameters', received start element with name '{token.name}'."
                )

        elif isinstance(token, Characters):
            raise ValueError(
                f"Expected start element with name 'Parameters' or end element with name 'ContentType', received characters '{token.value}'."
            )

        elif isinstance(token, EndElement) and token.name == "ContentType":
            return cls(type, subtype)

        parameters: list[ContentTypeParameter] = []
        while True:
            token = yield

            if isinstance(token, StartElement):
                if token.name == "Parameter":
                    # Attribute
                    yield from deserializer.read_start_element(name="Attribute")
                    attribute = yield from deserializer.read_str()
                    yield from deserializer.read_end_element(name="Attribute")

                    # Value
                    yield from deserializer.read_start_element(name="Value")
                    value = yield from deserializer.read_str()
                    yield from deserializer.read_end_element(name="Value")

                    parameters.append(ContentTypeParameter(attribute, value))

                else:
                    raise ValueError(
                        f"Expected start element with name 'Parameter', received start element with name '{token.name}'."
                    )

            elif isinstance(token, EndElement):
                if token.name == "Parameter":
                    continue
                else:
                    break  # pragma: no cover

            elif isinstance(token, Characters):
                raise ValueError(f"Expected start element with name 'Parameter', received characters '{token.value}'.")

        if not parameters:
            raise ValueError("Expected at least one 'Parameter' element inside the 'ContentType' element.")

        yield from deserializer.read_end_element(name="ContentType")

        return cls(type, subtype, parameters)
