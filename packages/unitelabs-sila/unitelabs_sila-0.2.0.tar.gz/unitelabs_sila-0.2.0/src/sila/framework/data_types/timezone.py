import dataclasses

import typing_extensions as typing

from sila import datetime

from ..protobuf import Message, Reader, WireType, Writer
from .convertable import Convertable

if typing.TYPE_CHECKING:
    from ..common import Context


@dataclasses.dataclass
class Timezone(Message, Convertable):
    """
    A signed, fixed-length span of time representing an offset from UTC.

    Attributes:
      hours: The hours of the timezone value in range [-12-14].
        Defaults to zero.
      minutes: The minutes of the timezone value in range [0-59].
        Defaults to zero.
    """

    hours: int = 0
    minutes: int = 0

    @typing.overload
    @classmethod
    async def from_native(
        cls, context: "Context", value: typing.Optional[datetime.timezone] = None, /
    ) -> typing.Self: ...

    @typing.overload
    @classmethod
    async def from_native(cls, context: "Context", /, *, hours: int = 0, minutes: int = 0) -> typing.Self: ...

    @typing.override
    @classmethod
    async def from_native(
        cls,
        context: "Context",
        value: typing.Optional[datetime.timezone] = None,
        /,
        *,
        hours: int = 0,
        minutes: int = 0,
    ) -> typing.Self:
        if value is None:
            return await cls(hours=hours, minutes=minutes).validate()

        offset = value.utcoffset(None)
        hour, minute = divmod(offset.total_seconds() // 60, 60)

        return await cls(hours=int(hour), minutes=int(minute)).validate()

    @typing.override
    async def to_native(self, context: "Context", /) -> datetime.timezone:
        await self.validate()

        return datetime.timezone(offset=datetime.timedelta(hours=self.hours, minutes=self.minutes))

    @typing.override
    async def validate(self) -> typing.Self:
        if not isinstance(self.hours, int):
            msg = f"Expected hours of type 'int', received '{type(self.hours).__name__}'."
            raise TypeError(msg)

        if not isinstance(self.minutes, int):
            msg = f"Expected minutes of type 'int', received '{type(self.minutes).__name__}'."
            raise TypeError(msg)

        if not (-12 <= self.hours <= 14):
            msg = f"Hours must be between -12 and 14, received '{self.hours}'."
            raise ValueError(msg)

        if not (0 <= self.minutes <= 59):
            msg = f"Minutes must be between 0 and 59, received '{self.minutes}'."
            raise ValueError(msg)

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
                reader.expect_type(tag, WireType.VARINT)
                message.hours = reader.read_int32()
            elif field_number == 2:
                reader.expect_type(tag, WireType.VARINT)
                message.minutes = reader.read_uint32()
            else:
                reader.skip_type(tag & 7)

        return message

    @typing.override
    def encode(self, writer: typing.Optional[Writer] = None, number: typing.Optional[int] = None) -> bytes:
        writer = writer or Writer()

        if number:
            writer.write_uint32((number << 3) | 2).fork()

        if self.hours:
            writer.write_uint32(8).write_int32(self.hours)
        if self.minutes:
            writer.write_uint32(16).write_uint32(self.minutes)

        if number:
            writer.ldelim()

        return writer.finish()
