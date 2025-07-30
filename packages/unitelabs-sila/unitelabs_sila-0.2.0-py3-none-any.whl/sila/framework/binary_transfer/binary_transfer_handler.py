import typing_extensions as typing


@typing.runtime_checkable
class BinaryTransferHandler(typing.Protocol):
    """Handle the transfer of large binaries."""

    async def get_binary(self, binary_transfer_uuid: str) -> bytes:
        """
        Retrieve a large binary by its identifier.

        Args:
          binary_transfer_uuid: A unique identifier (UUID) for the binary
            transfer session from which the large binary was retrieved.

        Returns:
          The actual binary data retrieved from the transfer session.
        """
        ...

    async def set_binary(self, value: bytes) -> str:
        """
        Dispatch a large binary through a binary transfer session.

        Args:
          value: The actual binary data being dispatched through the
            binary transfer session.

        Returns:
          A unique identifier (UUID) for the binary transfer session to
          which the data was dispatched.
        """
        ...
