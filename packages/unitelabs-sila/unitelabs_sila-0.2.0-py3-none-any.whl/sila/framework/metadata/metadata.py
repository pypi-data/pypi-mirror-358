import collections.abc
import dataclasses
import functools

import typing_extensions as typing

from ..common.handler import Handler
from ..data_types import Any
from ..fdl import Serializable
from ..identifiers import MetadataIdentifier

if typing.TYPE_CHECKING:
    from ..common.feature import Feature
    from ..data_types import DataType
    from ..fdl import Deserializer, Serializer


@dataclasses.dataclass
class Metadata(Handler, Serializable):
    """Aditional information the server expects to receive from a client."""

    affects: list[str] = dataclasses.field(default_factory=list)

    data_type: type["DataType"] = Any
    """The SiLA data type of the metadata."""

    @functools.cached_property
    @typing.override
    def fully_qualified_identifier(self) -> MetadataIdentifier:
        """Uniquely identifies the metadata."""

        return MetadataIdentifier.create(**super().fully_qualified_identifier._data, metadata=self.identifier)

    @functools.cached_property
    def rpc_header(self) -> str:
        """The gRPC header specifier used to identify metadata."""

        return f"sila-{self.fully_qualified_identifier.lower().replace('/', '-')}-bin"

    @typing.override
    def add_to_feature(self, feature: "Feature") -> typing.Self:
        super().add_to_feature(feature)

        feature.metadata[self.identifier] = self

        return self

    @typing.override
    def serialize(self, serializer: "Serializer") -> None:
        serializer.start_element("Metadata")
        serializer.write_str("Identifier", self.identifier)
        serializer.write_str("DisplayName", self.display_name)
        serializer.write_str("Description", self.description)
        self.data_type.serialize(serializer)
        if self.errors:
            serializer.start_element("DefinedExecutionErrors")
            for Error in self.errors.values():
                serializer.write_str("Identifier", Error.identifier)
            serializer.end_element("DefinedExecutionErrors")
        serializer.end_element("Metadata")

    @typing.override
    def deserialize(self, deserializer: "Deserializer") -> collections.abc.Generator[None, typing.Any, typing.Self]: ...
