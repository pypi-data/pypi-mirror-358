import dataclasses
import inspect

import grpc
import grpc.aio
import typing_extensions as typing

from .. import framework
from ..framework import (
    ConversionError,
    DataType,
    DecodeError,
    DefinedExecutionError,
    Element,
    InvalidMetadata,
    Message,
    MetadataIdentifier,
    Native,
    Reader,
    Server,
    String,
    WireType,
    Writer,
)

if typing.TYPE_CHECKING:
    from ..framework import Feature, Handler


@dataclasses.dataclass
class Metadata(framework.Metadata, Message):
    """Aditional information the server expects to receive from a client."""

    function: typing.Callable = dataclasses.field(repr=False, default=lambda *args: ...)
    """The implementation which is executed by the RPC handler."""

    async def intercept(self, metadata: dict[str, bytes], target: "Handler") -> dict[MetadataIdentifier, Native]:
        """
        Intercept the current handler execution with this metadata.

        Args:
          metadata: Additional metadata sent from client to server.
          target: The affected target.

        Returns:
          The resulting responses of the command execution.

        Raises:
          NoMetadataAllowed: If providing metadata is not allowed.
          InvalidMetadata: If metadata is missing or invalid.
          DefinedExecutionError: If execution the metadata's interceptor
            results in a defined execution error
          UnefinedExecutionError: If execution the metadata's interceptor
            results in an undefined execution error.
        """

        assert self.feature is not None and isinstance(self.feature.context, Server)

        if self.rpc_header not in metadata:
            msg = f"Missing matadata '{self.identifier}' in {target.__class__.__name__} '{target.identifier}'."
            raise InvalidMetadata(msg)

        try:
            value = self.decode(metadata[self.rpc_header])
            if value is None:
                msg = f"Missing matadata '{self.identifier}' in {target.__class__.__name__} '{target.identifier}'."
                raise InvalidMetadata(msg)

            value = await value.to_native(self.feature.context)
        except (DecodeError, ConversionError) as error:
            msg = (
                f"Unable to decode matadata '{self.identifier}' in "
                f"{target.__class__.__name__} '{target.identifier}': {error.message}"
            )
            raise InvalidMetadata(msg) from None

        try:
            response = self.function(value, target)

            if inspect.isawaitable(response):
                await response
        except DefinedExecutionError as error:
            error = error.with_feature(self.feature.fully_qualified_identifier)
            raise error

        return {self.fully_qualified_identifier: value}

    async def rpc_handler(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        """
        Handle the gRPC call to get the list of affected identifiers.

        Args:
          request: The request payload in protobuf ecoding.
          context: The gRPC call context.

        Returns:
          The response payload in protobuf ecoding.
        """

        return self.encode()

    @typing.override
    def add_to_feature(self, feature: "Feature") -> typing.Self:
        super().add_to_feature(feature)

        feature.context.protobuf.register_message(
            name=f"Metadata_{self.identifier}",
            message={
                "key": Element(
                    identifier=self.identifier,
                    display_name=self.display_name,
                    description=self.description,
                    data_type=self.data_type,
                )
            },
        )

        feature.context.protobuf.register_service(
            feature.identifier,
            {f"Get_FCPAffectedByMetadata_{self.identifier}": grpc.unary_unary_rpc_method_handler(self.rpc_handler)},
            package=feature.rpc_package,
        )

        return self

    @typing.override
    def decode(
        self, reader: typing.Union["Reader", bytes], length: typing.Optional[int] = None
    ) -> typing.Optional[DataType]:
        reader = reader if isinstance(reader, Reader) else Reader(reader)

        end = reader.length if length is None else reader.cursor + length
        value: typing.Optional[DataType] = None

        while reader.cursor < end:
            tag = reader.read_uint32()
            field_number = tag >> 3

            if field_number == 1:
                reader.expect_type(tag, WireType.LEN)
                value = self.data_type.decode(reader, reader.read_uint32())
            else:
                reader.skip_type(tag & 7)

        return value

    @typing.override
    def encode(self, writer: typing.Optional[Writer] = None, number: typing.Optional[int] = None) -> bytes:
        writer = writer or Writer()

        if number:
            writer.write_uint32((number << 3) | 2).fork()

        for affected_call in self.affects:
            String(affected_call).encode(writer, number or 1)

        if number:
            writer.ldelim()

        return writer.finish()
