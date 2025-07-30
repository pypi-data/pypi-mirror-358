import collections.abc
import contextlib

import typing_extensions as typing

from ..fdl import Serializable
from ..identifiers import ErrorIdentifier, FeatureIdentifier
from ..protobuf import Reader, WireType, Writer
from ..validators import check_display_name, check_identifier
from .sila_error import SiLAError

if typing.TYPE_CHECKING:
    from ..fdl import Deserializer, Serializer


class DefinedExecutionError(SiLAError, Serializable):
    """
    Expected error that occurs during command execution.

    Attributes:
      identifier: Uniquely identifies the defined execution error
        within the scope of the same feature.
      display_name: Human readable name of the defined execution
        error.
      description: Describes the use and purpose of the defined
        execution error.

    Args:
      message: An error message providing additional context or
        details about the error and how to resolve it.
    """

    identifier: typing.ClassVar[str] = ""
    display_name: typing.ClassVar[str] = ""
    description: typing.ClassVar[str] = ""

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.description)

        self._identifier: typing.Optional[ErrorIdentifier] = None

    @property
    def fully_qualified_identifier(self) -> ErrorIdentifier:
        """Uniquely identifies the defined execution error."""

        if self._identifier is None:
            msg = (
                f"Unable to get fully qualified identifier for DefinedExecutionError "
                f"'{self.identifier}' without feature association."
            )
            raise RuntimeError(msg)

        return self._identifier

    def with_feature(self, feature_identifier: str, /) -> typing.Self:
        """
        Assign the defined execution error to the given feature.

        Args:
          feature_identifier: The fully qualified feature identifier this
            error is assigned to.

        Returns:
          The Error instance, allowing for method chaining.
        """

        feature_identifier = FeatureIdentifier(feature_identifier)
        self._identifier = ErrorIdentifier.create(**feature_identifier.feature_identifier._data, error=self.identifier)

        return self

    @typing.override
    @classmethod
    def decode(cls, reader: typing.Union[Reader, bytes], length: typing.Optional[int] = None) -> typing.Self:
        reader = reader if isinstance(reader, Reader) else Reader(reader)

        message = ""
        identifier = ""
        end = reader.length if length is None else reader.cursor + length

        while reader.cursor < end:
            tag = reader.read_uint32()
            field_number = tag >> 3

            if field_number == 1:
                reader.expect_type(tag, WireType.LEN)
                identifier = reader.read_string()
            elif field_number == 2:
                reader.expect_type(tag, WireType.LEN)
                message = reader.read_string()
            else:
                reader.skip_type(tag & 7)

        error = cls(message)
        with contextlib.suppress(ValueError):
            error._identifier = ErrorIdentifier(identifier)

        return error

    @typing.override
    def encode(self, writer: typing.Optional[Writer] = None, number: typing.Optional[int] = None) -> bytes:
        writer = writer or Writer()

        if number:
            writer.write_uint32((number << 3) | 2).fork()

        writer.write_uint32(18).fork()

        if self._identifier:
            writer.write_uint32(10).write_string(self._identifier)
        if self.message:
            writer.write_uint32(18).write_string(self.message)

        writer.ldelim()

        if number:
            writer.ldelim()

        return writer.finish()

    @classmethod
    def create(
        cls,
        identifier: str,
        display_name: str,
        description: str = "",
    ) -> type[typing.Self]:
        """
        Create a new SiLA `DefinedExecutionError` class.

        Args:
          identifier: Uniquely identifies the defined execution error
            within the scope of the same feature.
          display_name: Human readable name of the defined execution
            error.
          description: Describes the use and purpose of the defined
            execution error.

        Returns:
          A new `DefinedExecutionError` class with the specified info.
        """

        check_identifier(identifier)
        check_display_name(display_name)

        return typing.cast(
            type[typing.Self],
            type(
                identifier or cls.__name__,
                (cls,),
                {
                    "__doc__": description,
                    "identifier": identifier,
                    "display_name": display_name,
                    "description": description,
                },
            ),
        )

    @typing.override
    @classmethod
    def serialize(cls, serializer: "Serializer") -> None:
        serializer.start_element("DefinedExecutionError")
        serializer.write_str("Identifier", cls.identifier)
        serializer.write_str("DisplayName", cls.display_name)
        serializer.write_str("Description", cls.description)
        serializer.end_element("DefinedExecutionError")

    @typing.override
    @classmethod
    def deserialize(
        cls, deserializer: "Deserializer"
    ) -> collections.abc.Generator[None, typing.Any, type[typing.Self]]: ...
