import collections.abc
import dataclasses
import enum

import typing_extensions as typing

from ..data_types.string import String
from ..fdl import Deserializer, Serializer
from ..identifiers import (
    CommandIdentifier,
    DataTypeIdentifier,
    ErrorIdentifier,
    FeatureIdentifier,
    IntermediateResponseIdentifier,
    MetadataIdentifier,
    ParameterIdentifier,
    PropertyIdentifier,
    ResponseIdentifier,
)
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List


class Identifier(str, enum.Enum):
    """
    Enum class representing various SiLA identifier types.
    """

    FEATURE_IDENTIFIER = "FeatureIdentifier"
    """Identifier for a feature."""

    COMMAND_IDENTIFIER = "CommandIdentifier"
    """Identifier for a command."""

    COMMAND_PARAMETER_IDENTIFIER = "ParameterIdentifier"
    """Identifier for a command parameter."""

    COMMAND_RESPONSE_IDENTIFIER = "ResponseIdentifier"
    """Identifier for a command response."""

    INTERMEDIATE_COMMAND_RESPONSE_IDENTIFIER = "IntermediateResponseIdentifier"
    """Identifier for an intermediate command response."""

    DEFINED_EXECUTION_ERROR_IDENTIFIER = "ErrorIdentifier"
    """Identifier for a defined execution error."""

    PROPERTY_IDENTIFIER = "PropertyIdentifier"
    """Identifier for a property."""

    DATA_TYPE_IDENTIFIER = "DataTypeIdentifier"
    """Identifier for a data type."""

    METADATA_IDENTIFIER = "MetadataIdentifier"
    """Identifier for metadata."""


@dataclasses.dataclass
class FullyQualifiedIdentifier(Constraint[str]):
    """
    A Fully Qualified Identifier Constraint specifies the content of
    the SiLA String Type to be a Fully Qualified Identifier and
    indicates the type of the identifier. Note that this is
    comparable to a Pattern Constraint; the content is not required
    to actually identify something, it just has to be a semantically
    correct Fully Qualified Identifier.

    Args:
      value: The specific identifier type (e.g., 'FeatureIdentifier',
        'CommandIdentifier', etc.) that the string must match.
    """

    Type: typing.ClassVar[type[Identifier]] = Identifier
    """
    Enum class representing various SiLA identifier types.
    """

    value: typing.Literal[
        "FeatureIdentifier",
        "CommandIdentifier",
        "ParameterIdentifier",
        "ResponseIdentifier",
        "IntermediateResponseIdentifier",
        "ErrorIdentifier",
        "PropertyIdentifier",
        "DataTypeIdentifier",
        "MetadataIdentifier",
    ]
    """
    The specific identifier type (e.g., 'FeatureIdentifier',
    'CommandIdentifier', etc.) that the string must match.
    """

    def __post_init__(self):
        self.value = self.value.value if isinstance(self.value, Identifier) else self.value

        try:
            self.__validate = {
                Identifier.FEATURE_IDENTIFIER: FeatureIdentifier,
                Identifier.COMMAND_IDENTIFIER: CommandIdentifier,
                Identifier.COMMAND_PARAMETER_IDENTIFIER: ParameterIdentifier,
                Identifier.COMMAND_RESPONSE_IDENTIFIER: ResponseIdentifier,
                Identifier.INTERMEDIATE_COMMAND_RESPONSE_IDENTIFIER: IntermediateResponseIdentifier,
                Identifier.DEFINED_EXECUTION_ERROR_IDENTIFIER: ErrorIdentifier,
                Identifier.PROPERTY_IDENTIFIER: PropertyIdentifier,
                Identifier.DATA_TYPE_IDENTIFIER: DataTypeIdentifier,
                Identifier.METADATA_IDENTIFIER: MetadataIdentifier,
            }[Identifier(self.value)]
        except ValueError:
            raise ValueError(f"Identifier type must be valid type, received '{self.value}'.") from None

    async def validate(self, value: str) -> bool:
        if not isinstance(value, str):
            raise TypeError(f"Expected value of type 'str', received '{type(value).__name__}'.")

        try:
            self.__validate(value)
        except Exception:
            raise ValueError(f"Expected value with format for a '{self.value}', received '{value}'.") from None

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.write_str("FullyQualifiedIdentifier", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, String):
            raise ValueError(f"Expected constraint's data type to be 'String', received '{data_type.__name__}'.")

        yield from deserializer.read_start_element(name="FullyQualifiedIdentifier")
        value = yield from deserializer.read_str()
        try:
            value = Identifier(value).value
        except ValueError:
            raise ValueError(f"Expected a valid 'FullyQualifiedIdentifier' value, received '{value}'.") from None
        yield from deserializer.read_end_element(name="FullyQualifiedIdentifier")

        return cls(value)
