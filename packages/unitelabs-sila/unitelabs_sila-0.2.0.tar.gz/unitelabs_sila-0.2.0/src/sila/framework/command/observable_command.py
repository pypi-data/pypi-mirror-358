import collections.abc
import dataclasses

import typing_extensions as typing

from .command import Command

if typing.TYPE_CHECKING:
    from ..data_types import Element
    from .command_confirmation import CommandConfirmation
    from .command_execution_info import CommandExecutionInfo


@dataclasses.dataclass
class ObservableCommand(Command):
    """Any command for which observing the progress of execution is possible or does make sense."""

    observable: bool = dataclasses.field(init=False, repr=False, default=True)
    """Whether the handler returns an observable stream or just a single value."""

    intermediate_responses: dict[str, "Element"] = dataclasses.field(default_factory=dict)
    """An intermediate response of the command execution."""

    async def initiate(self, request: bytes = b"", metadata: typing.Optional[dict] = None) -> "CommandConfirmation":
        """
        Initiate the execution of  the command.

        Args:
          request: Input parameters passed to the command.
          metadata: Additional metadata sent from client to server.

        Returns:
          Confirmation that the command execution has been accepted.

        Raises:
          NoMetadataAllowed: If providing metadata is not allowed.
          InvalidMetadata: If metadata is missing or invalid.
          CommandExecutionNotAccepted: If the server does not allow
            further command executions.
          ValidationError: If command parameters are missing or invalid.
          DefinedExecutionError: If metadata handling results in a
            defined execution error
        """

        raise NotImplementedError

    def subscribe_status(self, command_execution_uuid: str) -> collections.abc.AsyncIterator["CommandExecutionInfo"]:
        """
        Subscribe to status changes of the command execution.

        Args:
          command_execution_uuid: The unique identifier of the command
            execution.

        Yields:
          The current status of the command execution.

        Raises:
          InvalidCommandExecutionUUID: If the given identifier is invalid
            or not recognized.
        """

        raise NotImplementedError

    def subscribe_intermediate(self, command_execution_uuid: str) -> collections.abc.AsyncIterator[bytes]:
        """
        Subscribe to intermediate responses of the command execution.

        Args:
          command_execution_uuid: The unique identifier of the command
            execution.

        Yields:
          The current intermediate responses of the command execution.

        Raises:
          InvalidCommandExecutionUUID: If the given identifier is invalid
            or not recognized.
        """

        raise NotImplementedError

    async def get_result(self, command_execution_uuid: str) -> bytes:
        """
        Get the responses of the command execution.

        Args:
          command_execution_uuid: The unique identifier of the command
            execution.

        Returns:
          The resulting responses of the command execution.

        Raises:
          InvalidCommandExecutionUUID: If the given identifier is invalid
            or not recognized.
          CommandExecutionNotFinished: If the command execution has not
            been finished yet.
          DefinedExecutionError: If command execution resulted in a
            defined execution error
          UnefinedExecutionError: If command execution resulted in an
            undefined execution error.
        """

        raise NotImplementedError
