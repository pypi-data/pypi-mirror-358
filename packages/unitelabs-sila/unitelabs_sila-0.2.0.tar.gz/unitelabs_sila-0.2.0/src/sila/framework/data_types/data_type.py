import abc
import collections.abc

import typing_extensions as typing

from ..fdl import Deserializer, Serializable, Serializer, StartElement
from ..protobuf import Message
from .convertable import Convertable, T

if typing.TYPE_CHECKING:
    from ..common import Context


class DataType(Message, Convertable[T], Serializable, typing.Generic[T], metaclass=abc.ABCMeta):
    """The data type of any information exchanged between SiLA server and client."""

    @typing.override
    @classmethod
    @abc.abstractmethod
    async def from_native(cls, context: "Context", value: typing.Optional[T] = None, /) -> typing.Self: ...

    @typing.override
    @abc.abstractmethod
    async def to_native(self, context: "Context", /) -> T: ...

    @typing.override
    @abc.abstractmethod
    async def validate(self) -> typing.Self: ...

    @typing.override
    @classmethod
    @abc.abstractmethod
    def serialize(cls, serializer: Serializer) -> None: ...

    @typing.override
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> collections.abc.Generator[None, typing.Any, type["DataType"]]:
        from ..data_types import Constrained, Custom, List, Structure

        yield from deserializer.read_start_element(name="DataType")

        token = yield from deserializer.peek()

        if isinstance(token, StartElement) and token.name == "Basic":
            data_type = yield from deserializer.read(BasicType.deserialize(deserializer))
        elif isinstance(token, StartElement) and token.name == "List":
            data_type = yield from deserializer.read(List.deserialize(deserializer))
        elif isinstance(token, StartElement) and token.name == "Structure":
            data_type = yield from deserializer.read(Structure.deserialize(deserializer))
        elif isinstance(token, StartElement) and token.name == "Constrained":
            data_type = yield from deserializer.read(Constrained.deserialize(deserializer))
        elif isinstance(token, StartElement) and token.name == "DataTypeIdentifier":
            data_type = yield from deserializer.read(Custom.deserialize(deserializer))

        yield from deserializer.read_end_element(name="DataType")

        return data_type


class BasicType(typing.Generic[T], DataType[T]):
    """A predefined collection of SiLA data types without any child data type items."""

    @typing.override
    @classmethod
    def serialize(cls, serializer: Serializer) -> None:
        serializer.start_element("DataType")
        serializer.write_str("Basic", cls.__name__)
        serializer.end_element("DataType")

    @typing.override
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> collections.abc.Generator[None, typing.Any, type["BasicType"]]:
        from ..data_types import Any, Binary, Boolean, Date, Integer, Real, String, Time, Timestamp

        yield from deserializer.read_start_element("Basic")

        basic_type = yield from deserializer.read_str()

        yield from deserializer.read_end_element("Basic")

        if basic_type == "String":
            return String
        elif basic_type == "Integer":
            return Integer
        elif basic_type == "Real":
            return Real
        elif basic_type == "Boolean":
            return Boolean
        elif basic_type == "Binary":
            return Binary
        elif basic_type == "Date":
            return Date
        elif basic_type == "Time":
            return Time
        elif basic_type == "Timestamp":
            return Timestamp
        elif basic_type == "Any":
            return Any
        else:
            msg = f"Expected basic type value, received '{basic_type}'."
            raise ValueError(msg)
