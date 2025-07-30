import dataclasses

import typing_extensions as typing

from .command import Command


@dataclasses.dataclass
class UnobservableCommand(Command):
    """Any command for which observing the progress of execution is not possible or does not make sense."""

    observable: bool = dataclasses.field(init=False, repr=False, default=False)

    async def execute(self, request: bytes = b"", metadata: typing.Optional[dict] = None) -> bytes:
        """
        Execute the command.

        Args:
          request: Input parameters passed to the command.
          metadata: Additional metadata sent from client to server.

        Returns:
          The resulting responses of the command execution.

        Raises:
          NoMetadataAllowed: If providing metadata is not allowed.
          InvalidMetadata: If metadata is missing or invalid.
          CommandExecutionNotAccepted: If the server does not allow
            further command executions.
          ValidationError: If command parameters are missing or invalid.
          DefinedExecutionError: If command execution results in a
            defined execution error
          UnefinedExecutionError: If command execution results in an
            undefined execution error.
        """

        raise NotImplementedError
