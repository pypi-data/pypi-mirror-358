import collections.abc
import dataclasses
import functools

import typing_extensions as typing

from ..common import Handler
from ..data_types.any import Any
from ..fdl import Serializable
from ..identifiers import PropertyIdentifier

if typing.TYPE_CHECKING:
    from ..common import Feature
    from ..data_types import DataType
    from ..fdl import Deserializer, Serializer


@dataclasses.dataclass
class Property(Handler, Serializable):
    """Describes certain aspects of a server that do not require an action on the server."""

    observable: bool = False
    """Whether the property returns an observable stream or just a single value."""

    data_type: type["DataType"] = Any
    """The SiLA data type of the property."""

    @functools.cached_property
    @typing.override
    def fully_qualified_identifier(self) -> PropertyIdentifier:
        """Uniquely identifies the property."""

        return PropertyIdentifier.create(**super().fully_qualified_identifier._data, property=self.identifier)

    @typing.override
    def add_to_feature(self, feature: "Feature") -> typing.Self:
        super().add_to_feature(feature)

        feature.properties[self.identifier] = self

        return self

    @typing.override
    def serialize(self, serializer: "Serializer") -> None:
        serializer.start_element("Property")
        serializer.write_str("Identifier", self.identifier)
        serializer.write_str("DisplayName", self.display_name)
        serializer.write_str("Description", self.description)
        serializer.write_bool("Observable", self.observable)
        self.data_type.serialize(serializer)
        if self.errors:
            serializer.start_element("DefinedExecutionErrors")
            for Error in self.errors.values():
                serializer.write_str("Identifier", Error.identifier)
            serializer.end_element("DefinedExecutionErrors")
        serializer.end_element("Property")

    @typing.override
    def deserialize(self, deserializer: "Deserializer") -> collections.abc.Generator[None, typing.Any, typing.Self]: ...
