import collections.abc
import dataclasses
import functools

import typing_extensions as typing

from ..common import Handler
from ..fdl import Serializable
from ..identifiers import CommandIdentifier

if typing.TYPE_CHECKING:
    from ..common import Feature
    from ..data_types import Element
    from ..fdl import Deserializer, Serializer


@dataclasses.dataclass
class Command(Handler, Serializable):
    """Describes certain actions that can be performed on the server."""

    observable: bool = False
    """Whether the command execution is observable or not."""

    parameters: dict[str, "Element"] = dataclasses.field(default_factory=dict)
    """The parameters of the command."""

    responses: dict[str, "Element"] = dataclasses.field(default_factory=dict)
    """The responses of the command containing the result."""

    @functools.cached_property
    @typing.override
    def fully_qualified_identifier(self) -> CommandIdentifier:
        """Uniquely identifies the command."""

        return CommandIdentifier.create(**super().fully_qualified_identifier._data, command=self.identifier)

    @typing.override
    def add_to_feature(self, feature: "Feature") -> typing.Self:
        super().add_to_feature(feature)

        feature.commands[self.identifier] = self

        return self

    @typing.override
    def serialize(self, serializer: "Serializer") -> None:
        from .observable_command import ObservableCommand

        serializer.start_element("Command")
        serializer.write_str("Identifier", self.identifier)
        serializer.write_str("DisplayName", self.display_name)
        serializer.write_str("Description", self.description)
        serializer.write_bool("Observable", self.observable)

        for element in self.parameters.values():
            serializer.start_element("Parameter")
            serializer.write_str("Identifier", element.identifier)
            serializer.write_str("DisplayName", element.display_name)
            serializer.write_str("Description", element.description)
            element.data_type.serialize(serializer)
            serializer.end_element("Parameter")

        for element in self.responses.values():
            serializer.start_element("Response")
            serializer.write_str("Identifier", element.identifier)
            serializer.write_str("DisplayName", element.display_name)
            serializer.write_str("Description", element.description)
            element.data_type.serialize(serializer)
            serializer.end_element("Response")

        if isinstance(self, ObservableCommand):
            for element in self.intermediate_responses.values():
                serializer.start_element("IntermediateResponse")
                serializer.write_str("Identifier", element.identifier)
                serializer.write_str("DisplayName", element.display_name)
                serializer.write_str("Description", element.description)
                element.data_type.serialize(serializer)
                serializer.end_element("IntermediateResponse")

        if self.errors:
            serializer.start_element("DefinedExecutionErrors")
            for Error in self.errors.values():
                serializer.write_str("Identifier", Error.identifier)
            serializer.end_element("DefinedExecutionErrors")

        serializer.end_element("Command")

    @typing.override
    def deserialize(self, deserializer: "Deserializer") -> collections.abc.Generator[None, typing.Any, typing.Self]: ...
