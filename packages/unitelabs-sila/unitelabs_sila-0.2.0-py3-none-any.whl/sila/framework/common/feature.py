import collections.abc
import dataclasses
import functools

import typing_extensions as typing

from ..fdl import Serializable
from ..identifiers import FeatureIdentifier
from ..validators import check_display_name, check_identifier
from .context_proxy import ContextProxy

if typing.TYPE_CHECKING:
    from ..command import Command
    from ..data_types import Custom
    from ..errors import DefinedExecutionError
    from ..fdl import Deserializer, Serializer
    from ..metadata import Metadata
    from ..property import Property
    from .context import Context


@dataclasses.dataclass
class Feature(Serializable):
    """Describes a specific behavior of a SiLA server."""

    locale: str = dataclasses.field(default="en-us")
    sila2_version: str = dataclasses.field(default="1.1")
    version: str = dataclasses.field(default="1.0")
    maturity_level: typing.Literal["Draft", "Verified", "Normative"] = dataclasses.field(default="Draft")
    originator: str = dataclasses.field(default="org.silastandard")
    category: str = dataclasses.field(default="none")

    identifier: str = ""
    """
    A feature identifier is the identifier of a feature. Each feature must have a feature identifier. All features
    sharing the scope of the same originator and category must have unique feature identifiers. Uniqueness must be
    checked without taking lower and upper case into account.
    """

    display_name: str = ""
    """Human readable name of the SiLA feature."""

    description: str = dataclasses.field(default="")
    """
    A feature description is the description of a feature. A feature description must describe the behaviors /
    capabilities the feature models in human readable form and with as many details as possible.
    """

    commands: dict[str, "Command"] = dataclasses.field(default_factory=dict)

    properties: dict[str, "Property"] = dataclasses.field(default_factory=dict)

    metadata: dict[str, "Metadata"] = dataclasses.field(default_factory=dict)

    errors: dict[str, type["DefinedExecutionError"]] = dataclasses.field(default_factory=dict)

    data_type_definitions: dict[str, type["Custom"]] = dataclasses.field(default_factory=dict)

    context: "Context" = dataclasses.field(default_factory=ContextProxy)
    """The context (either client or server) this feature was registered with."""

    def __post_init__(self) -> None:
        check_identifier(self.identifier)
        check_display_name(self.display_name)

        for command in self.commands.values():
            command.feature = self

        for property_ in self.properties.values():
            property_.feature = self

        for metadata in self.metadata.values():
            metadata.add_to_feature(self)

    @functools.cached_property
    def fully_qualified_identifier(self) -> FeatureIdentifier:
        """Uniquely identifies the feature."""

        return FeatureIdentifier.create(
            self.originator, self.category, self.identifier, int(self.version.rpartition(".")[0])
        )

    @functools.cached_property
    def rpc_package(self) -> str:
        """The package specifier to namespace services and protobuf messages."""

        return ".".join(
            (
                "sila2",
                self.originator,
                self.category,
                str(self.identifier).lower(),
                f"v{self.version.rpartition('.')[0]}",
            )
        )

    @typing.override
    def serialize(self, serializer: "Serializer") -> None:
        serializer.write(
            '<?xml version="1.0" encoding="utf-8" ?>\n'
            f'<Feature Locale="{self.locale}" SiLA2Version="{self.sila2_version}" FeatureVersion="{self.version}" '
            f'MaturityLevel="{self.maturity_level}" Originator="{self.originator}" Category="{self.category}"\n'
            '         xmlns="http://www.sila-standard.org"\n'
            '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            '         xsi:schemaLocation="http://www.sila-standard.org https://gitlab.com/SiLA2/sila_base/raw/master/schema/FeatureDefinition.xsd">'
        )
        serializer.indent()
        serializer.write_str("Identifier", self.identifier)
        serializer.write_str("DisplayName", self.display_name)
        serializer.write_str("Description", self.description)

        defined_execution_errors: dict[str, type["DefinedExecutionError"]] = self.errors.copy()

        for command in self.commands.values():
            command.serialize(serializer)
            defined_execution_errors.update(command.errors)

        for property_ in self.properties.values():
            property_.serialize(serializer)
            defined_execution_errors.update(property_.errors)

        for metadata in self.metadata.values():
            metadata.serialize(serializer)
            defined_execution_errors.update(metadata.errors)

        for Error in defined_execution_errors.values():
            Error.serialize(serializer)

        for DataTypeDefinition in self.data_type_definitions.values():
            DataTypeDefinition.serialize(serializer, definition=True)

        serializer.end_element("Feature")

    @typing.override
    def deserialize(self, deserializer: "Deserializer") -> collections.abc.Generator[None, typing.Any, typing.Self]: ...

    @typing.override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Feature):
            return NotImplemented

        return other.fully_qualified_identifier == self.fully_qualified_identifier
