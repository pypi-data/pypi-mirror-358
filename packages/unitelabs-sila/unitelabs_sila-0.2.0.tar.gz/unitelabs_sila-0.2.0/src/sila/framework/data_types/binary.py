import dataclasses

import typing_extensions as typing

from ..protobuf import Reader, WireType, Writer
from .data_type import BasicType

if typing.TYPE_CHECKING:
    from ..common import Context


@dataclasses.dataclass
class Binary(BasicType[bytes]):
    """
    Represents arbitrary binary data of any size such as images, flat files, etc.

    If the SiLA binary type is used for character data, e.g. plain
    text, XML or JSON, the character encoding must be UTF-8. It is
    recommended to specify constraints, e.g. a content-type or schema
    constraint for the SiLA binary type in order to make the binary
    content type safe.

    Attributes:
      value: The encapsulated `bytes` value. Defaults to an empty
        bytes.
      binary_transfer_uuid: When the value is too large, the binary
        is transferred via the SiLA binary transfer feature,
        identified with this uuid.
    """

    value: bytes = b""
    binary_transfer_uuid: typing.Optional[str] = None

    @typing.override
    @classmethod
    async def from_native(cls, context: "Context", value: typing.Optional[bytes] = None, /) -> typing.Self:
        if value is None:
            return await cls().validate()

        try:
            size = len(value)
        except TypeError:
            size = 0

        if size <= 2**21:
            return await cls(value=value).validate()

        binary_transfer_uuid = await context.binary_transfer_handler.set_binary(value)

        return await cls(binary_transfer_uuid=binary_transfer_uuid).validate()

    @typing.override
    async def to_native(self, context: "Context", /) -> bytes:
        await self.validate()

        if self.binary_transfer_uuid is not None:
            return await context.binary_transfer_handler.get_binary(self.binary_transfer_uuid)

        return self.value

    @typing.override
    async def validate(self) -> typing.Self:
        if not isinstance(self.value, bytes):
            msg = f"Expected value of type 'bytes', received '{type(self.value).__name__}'."
            raise TypeError(msg)

        return self

    @typing.override
    @classmethod
    def decode(cls, reader: typing.Union[Reader, bytes], length: typing.Optional[int] = None) -> typing.Self:
        reader = reader if isinstance(reader, Reader) else Reader(reader)

        message = cls()
        end = reader.length if length is None else reader.cursor + length

        while reader.cursor < end:
            tag = reader.read_uint32()
            field_number = tag >> 3

            if field_number == 1:
                reader.expect_type(tag, WireType.LEN)
                message.value = reader.read_bytes()
                message.binary_transfer_uuid = None
            elif field_number == 2:
                reader.expect_type(tag, WireType.LEN)
                message.value = b""
                message.binary_transfer_uuid = reader.read_string()
            else:
                reader.skip_type(tag & 7)

        return message

    @typing.override
    def encode(self, writer: typing.Optional[Writer] = None, number: typing.Optional[int] = None) -> bytes:
        writer = writer or Writer()

        if number:
            writer.write_uint32((number << 3) | 2).fork()

        if self.binary_transfer_uuid:
            writer.write_uint32(18).write_string(self.binary_transfer_uuid)
        else:
            writer.write_uint32(10).write_bytes(self.value)

        if number:
            writer.ldelim()

        return writer.finish()
