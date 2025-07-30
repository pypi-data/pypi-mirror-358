import abc
import collections
import collections.abc
import dataclasses
import io
import textwrap
import xml.parsers
import xml.sax
import xml.sax.xmlreader

import typing_extensions as typing

from sila import datetime

from .parse_error import ParseError

T = typing.TypeVar("T")
S = typing.TypeVar("S")


@dataclasses.dataclass
class Token(abc.ABC):
    pass


@dataclasses.dataclass
class StartElement(Token):
    name: str
    attrs: dict[str, str] = dataclasses.field(compare=False, default_factory=dict)


@dataclasses.dataclass
class EndElement(Token):
    name: str


@dataclasses.dataclass
class Characters(Token):
    value: list[str]


@dataclasses.dataclass
class EndDocument(Token):
    pass


class Deserializer(xml.sax.ContentHandler, xml.sax.ErrorHandler, typing.Generic[T]):
    def __init__(self):
        super().__init__()

        self.running = False
        self.content = ""
        self._names: list[str] = []
        self._result: typing.Optional[T] = None
        self._exception: typing.Optional[BaseException] = None
        self._locator: typing.Optional[xml.sax.xmlreader.Locator] = None
        self._tokens: list[Token] = []
        self._characters: list[str] = []
        self._handlers = collections.deque[collections.abc.Generator[None, typing.Any, typing.Any]]()

    @classmethod
    def deserialize(
        cls,
        content: str,
        handler: typing.Callable[["Deserializer"], collections.abc.Generator[None, typing.Any, T]],
    ) -> T:
        """
        Deserialize the given XML string using the given handler.

        Args:
          content: The string representation of the XML data.
          handler: The handler to deserialize the root element.

        Returns:
          The parsed object.

        Raises:
          ParsingError: If unexpected or invalid data is detected during
            parsing.
        """

        deserializer = cls()
        deserializer.register(handler(deserializer))
        deserializer.content = content
        parser = xml.sax.make_parser()
        parser.setContentHandler(deserializer)
        parser.setErrorHandler(deserializer)
        parser.forbid_dtd = True  # type: ignore
        parser.forbid_entities = True  # type: ignore
        parser.forbid_external = True  # type: ignore

        stream = io.StringIO(content.strip())
        parser.parse(stream)

        return deserializer.result()

    def done(self) -> bool:
        """Whether the deserializer has a result or an exception set."""

        return self._result is not None or self._exception is not None

    def result(self) -> T:
        """
        Return the result of the deserializer.

        Returns:
          The result value.

        Raises:
          RuntimeError: If the deserializer's result isn't yet available.
          BaseException: If the deserializer is done and has an exception
            set by the `set_exception()` method.
        """

        if self._exception is not None:
            raise self._exception

        if self._result is None:
            msg = "Result is not set."
            raise RuntimeError(msg)

        return self._result

    def set_result(self, result: T) -> None:
        """
        Mark the deserializer as done and set its result.

        Args:
          result: The result to set.
        """

        self._result = result

    def set_exception(self, exception: BaseException) -> None:
        """
        Mark the deserializer as done and set an exception.

        Args:
          exception: The exception to raise.
        """

        self._exception = exception

    def read_start_element(self, name: str) -> collections.abc.Generator[None, Token, StartElement]:
        """
        Expect the start of an element with the given name.

        Args:
          name: Contains the raw XML 1.0 name of the element type.

        Yields:
          The detected start element.

        Raises:
          ParsingError: If the expected and detected tokens differ.
        """

        if self._tokens:
            token = self._tokens.pop()
        else:
            token = yield

        if not isinstance(token, StartElement):
            if isinstance(token, EndElement):
                msg = f"Expected start element with name '{name}', received end element with name '{token.name}'."
                raise ValueError(msg)

            if isinstance(token, Characters):
                msg = f"Expected start element with name '{name}', received characters '{token.value}'."
                raise ValueError(msg)

            msg = f"Expected start element with name '{name}', received token '{token}'."
            raise ValueError(msg)

        if token.name != name:
            msg = f"Expected start element with name '{name}', received start element with name '{token.name}'."
            raise ValueError(msg)

        return token

    def read_end_element(self, name: str) -> collections.abc.Generator[None, Token, EndElement]:
        """
        Expect the end of an element with the given name.

        Args:
          name: Contains the raw XML 1.0 name of the element type.

        Yields:
          The detected end element.

        Raises:
          ParsingError: If the expected and detected tokens differ.
        """

        if self._tokens:
            token = self._tokens.pop()
        else:
            token = yield

        if not isinstance(token, EndElement):
            if isinstance(token, StartElement):
                msg = f"Expected end element with name '{name}', received start element with name '{token.name}'."
                raise ValueError(msg)

            if isinstance(token, Characters):
                msg = f"Expected end element with name '{name}', received characters '{token.value}'."
                raise ValueError(msg)

            msg = f"Expected end element with name '{name}', received token '{token}'."
            raise ValueError(msg)

        if token.name != name:
            msg = f"Expected end element with name '{name}', received end element with name '{token.name}'."
            raise ValueError(msg)

        return token

    def read_str(self) -> collections.abc.Generator[None, Token, str]:
        """
        Read a string value from the buffer.

        Returns:
          The string value read from the xml.
        """

        token = yield from self.read_characters()

        return textwrap.dedent("\n".join(token.value)).replace("\n", " ")

    def read_bool(self) -> collections.abc.Generator[None, Token, bool]:
        """
        Read a boolean value from the buffer.

        Returns:
          The boolean value read from the xml.
        """

        value = yield from self.read_str()

        if value not in ("Yes", "No"):
            msg = f"Could not convert '{self._names[-1]}' with value '{value}' to boolean."
            raise ValueError(msg)

        return value == "Yes"

    def read_int(self) -> collections.abc.Generator[None, Token, int]:
        """
        Read an integer value from the buffer.

        Returns:
          The integer value read from the xml.
        """

        value = yield from self.read_str()

        try:
            return int(float(value))
        except ValueError:
            msg = f"Could not convert '{self._names[-1]}' with value '{value}' to integer."
            raise ValueError(msg) from None

    def read_float(self) -> collections.abc.Generator[None, Token, float]:
        """
        Read a float value from the buffer.

        Returns:
          The float value read from the xml.
        """

        value = yield from self.read_str()

        try:
            return float(value)
        except ValueError:
            msg = f"Could not convert '{self._names[-1]}' with value '{value}' to float."
            raise ValueError(msg) from None

    def read_date(self) -> collections.abc.Generator[None, Token, datetime.date]:
        """
        Read a date value from the buffer.

        Returns:
          The date value read from the xml.
        """

        value = yield from self.read_str()

        try:
            date = datetime.date.fromisoformat(value[:10])

            if len(value) > 10:
                if value[10:] == "Z":
                    date = date.replace(tzinfo=datetime.timezone.utc)
                else:
                    tzsign = -1 if value[10] == "-" else 1
                    offset = datetime.timedelta(hours=int(value[11:13]), minutes=int(value[14:16]))
                    date = date.replace(tzinfo=datetime.timezone(tzsign * offset))

            return date
        except ValueError:
            msg = f"Could not convert '{self._names[-1]}' with value '{value}' to date."
            raise ValueError(msg) from None

    def read_time(self) -> collections.abc.Generator[None, Token, datetime.time]:
        """
        Read a time value from the buffer.

        Returns:
          The time value read from the xml.
        """

        value = yield from self.read_str()

        try:
            return datetime.time.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            msg = f"Could not convert '{self._names[-1]}' with value '{value}' to time."
            raise ValueError(msg) from None

    def read_datetime(self) -> collections.abc.Generator[None, Token, datetime.datetime]:
        """
        Read a datetime value from the buffer.

        Returns:
          The datetime value read from the xml.
        """

        value = yield from self.read_str()

        try:
            return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            msg = f"Could not convert '{self._names[-1]}' with value '{value}' to datetime."
            raise ValueError(msg) from None

    def read_characters(self) -> collections.abc.Generator[None, Token, Characters]:
        """
        Expect chunks of characters.

        Yields:
          The detected chunks of characters.

        Raises:
          ParsingError: If the expected and detected tokens differ.
        """

        if self._tokens:
            token = self._tokens.pop()
        else:
            token = yield

        if not isinstance(token, Characters):
            if isinstance(token, StartElement):
                msg = f"Expected characters, received start element with name '{token.name}'."
                raise ValueError(msg)
            if isinstance(token, EndElement):
                self._tokens.append(token)
                return Characters(value=[])

            msg = f"Expected characters, received token '{token}'."
            raise ValueError(msg)

        return token

    def peek(self) -> collections.abc.Generator[None, typing.Any, Token]:
        """
        Look ahead one item without advancing the iterator.

        Returns:
          The token that will be next returned from `read()`.
        """

        token = yield

        self._tokens.append(token)

        return token

    def read(
        self, generator: typing.Optional[collections.abc.Generator[None, typing.Any, S]] = None
    ) -> collections.abc.Generator[None, typing.Any, S]:
        """
        Expect to read elements in the order defined in the given handler.

        Args:
          generator: The handler used to continue deserialization.

        Returns:
          The deserialized object returned by the handler.

        Raises:
          ParsingError: If the expected and detected tokens differ.
        """

        if generator is not None:
            self.register(generator)

        token = yield

        return token

    @typing.override
    def startDocument(self) -> None:
        """Signals the beginning of a document."""

        self.running = True

    @typing.override
    def endDocument(self) -> None:
        """Signals the end of a document."""

        self.running = False
        while self._handlers:
            self.__handle_token(EndDocument())

    @typing.override
    def startElement(self, name: str, attrs: typing.Optional[xml.sax.xmlreader.AttributesImpl] = None) -> None:
        """
        Signals the start of an element in non-namespace mode.

        Args:
          name: Contains the raw XML 1.0 name of the element type.
          attrs: Contains the attributes of the element.
        """

        self._names.append(name)

        if not self._handlers:
            msg = f"Received start element with name '{name}', but no handler registered."
            raise ValueError(msg)

        self.__handle_token(StartElement(name, dict(attrs.items()) if attrs is not None else {}))

    @typing.override
    def endElement(self, name: str) -> None:
        """
        Signals the end of an element in non-namespace mode.

        Args:
          name: Contains the raw XML 1.0 name of the element type.
        """

        if not self._handlers:
            msg = f"Received end element with name '{name}', but no handler registered."
            raise ValueError(msg)

        if not self._names:
            msg = f"Did not expect an end element, received end element with name '{name}'."
            raise ValueError(msg)

        if self._names[-1] != name:
            msg = f"Expected end element with name '{self._names[-1]}', received end element with name '{name}'."
            raise ValueError(msg)

        self.__handle_token(EndElement(name))
        self._names.pop()

    @typing.override
    def characters(self, content: str) -> None:
        """
        Receive notification of character data.

        Args:
          content: A chunk of character data.
        """

        if content.strip():
            self._characters.append(content)

    @typing.override
    def setDocumentLocator(self, locator: xml.sax.xmlreader.Locator) -> None:
        """
        Receive access to a locator of document events.

        Args:
          locator: Allows for locating the origin of document events.
        """

        self._locator = locator

    @typing.override
    def error(self, exception: BaseException) -> typing.NoReturn:
        """
        Handle a recoverable error.

        Args:
          exception: The error to handle.
        """

        if not isinstance(exception, ParseError):
            exception = ParseError(
                exception.args[0],
                path=self._names,
                line=self._locator.getLineNumber() or 0 if self._locator is not None else 0,
                column=self._locator.getColumnNumber() or 0 if self._locator is not None else 0,
            )

        self.set_exception(exception)

        raise exception

    @typing.override
    def fatalError(self, exception: BaseException) -> typing.NoReturn:
        """
        Handle a non-recoverable error.

        Args:
          exception: The fatal error to handle.
        """

        self.error(exception)

    def register(self, handler: collections.abc.Generator[None, typing.Any, typing.Any]) -> None:
        """
        Register a handler and advance it to its first yield.

        Args:
          handler: A generator that receives and processes token through
            yield statements.
        """

        self._handlers.append(handler)

        try:
            next(handler)
        except Exception as error:  # noqa: BLE001
            self.error(error)

    def __handle_token(self, token: Token) -> None:
        if self._characters:
            characters = Characters(self._characters)
            self._characters = []

            self.__handle_token(characters)

        try:
            self._handlers[-1].send(token)
        except StopIteration as result:
            self._handlers.pop().close()

            if self._handlers:
                self.__handle_token(result.value)
            else:
                self.set_result(result.value)
        except Exception as error:  # noqa: BLE001
            self.error(error)
