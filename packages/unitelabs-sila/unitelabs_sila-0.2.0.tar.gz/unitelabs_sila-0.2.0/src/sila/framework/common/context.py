import weakref

import typing_extensions as typing

from ..errors import InvalidCommandExecutionUUID
from ..protobuf import Protobuf

if typing.TYPE_CHECKING:
    from ..binary_transfer import BinaryTransferHandler
    from ..command import CommandExecution
    from ..identifiers import FeatureIdentifier
    from ..protobuf import Protobuf
    from .feature import Feature


class Context:
    """Mediates access to various functionalities within the library."""

    def __init__(self) -> None:
        self._protobuf: Protobuf = Protobuf(self)
        self._features: dict["FeatureIdentifier", "Feature"] = {}
        self._command_executions: dict[str, "CommandExecution"] = {}
        self._binary_transfer_handler: "BinaryTransferHandler"

    @property
    def protobuf(self) -> "Protobuf":
        """A collection of protobuf messages and services."""

        return self._protobuf

    @property
    def features(self) -> dict["FeatureIdentifier", "Feature"]:
        """A collection of registered features."""

        return self._features

    @property
    def command_executions(self) -> dict[str, "CommandExecution"]:
        """A collection of currently executed commands."""

        return self._command_executions

    @property
    def binary_transfer_handler(self) -> "BinaryTransferHandler":
        """Upload and download large binaries in chunks."""

        return self._binary_transfer_handler

    def register_feature(self, feature: "Feature") -> None:
        """
        Register a feature to the context.

        Args:
          feature: The feature to register.
        """

        self.protobuf.merge(feature.context.protobuf)
        self.features[feature.fully_qualified_identifier] = feature
        feature.context = weakref.proxy(self)

    def add_command_execution(self, command_execution: "CommandExecution") -> None:
        """
        Add a command execution to the context.

        Args:
          command_execution: The command execution to add.

        Raises:
          InvalidCommandExecutionUUID: If the uuid is already registered
            with a command execution.
        """

        if command_execution.command_execution_uuid in self.command_executions:
            msg = f"Command execution with uuid '{command_execution.command_execution_uuid}' already exists."
            raise InvalidCommandExecutionUUID(msg)

        self.command_executions[command_execution.command_execution_uuid] = command_execution

    def get_command_execution(self, command_execution_uuid: str) -> "CommandExecution":
        """
        Get a command execution by its UUID.

        Args:
          command_execution_uuid: The UUID of the command execution.

        Returns:
          The command execution with the given uuid.

        Raises:
          InvalidCommandExecutionUUID: If no command execution is
            available for the uuid.
        """

        if command_execution_uuid not in self.command_executions:
            msg = f"Requested unknown command execution uuid '{command_execution_uuid}'."
            raise InvalidCommandExecutionUUID(msg)

        return self.command_executions[command_execution_uuid]
