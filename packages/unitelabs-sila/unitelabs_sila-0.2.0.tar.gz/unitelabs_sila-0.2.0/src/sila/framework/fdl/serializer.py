import decimal
import io
import textwrap

import typing_extensions as typing

from sila import datetime
from sila.datetime.date import _format_offset


class Serializer:
    ctx: typing.ClassVar[decimal.Context] = decimal.Context(prec=20)

    def __init__(self, remove_whitespace: bool = False) -> None:
        self.indentation = 0
        self.buffer = io.StringIO()
        self.remove_whitespace = remove_whitespace

    @classmethod
    def float_to_str(cls, value: float) -> str:
        """
        Convert float to exact string representation, i.e. prevent
        scientific notation produced by float repr.

        Args:
          value: The float value to convert to string.

        Returns:
          The string representation.
        """

        return format(cls.ctx.create_decimal(repr(value)).normalize(), "f")

    @classmethod
    def serialize(cls, handler: typing.Callable[["Serializer"], None], remove_whitespace: bool = False) -> str:
        """
        Serialize an object using the given parsers into an XML string.

        Args:
          handler: The handler to serialize the root element
          remove_whitespace: Whether to omit whitespaces in the output.

        Returns:
          The string representation of the XML data.
        """

        serializer = Serializer(remove_whitespace)
        handler(serializer)

        return serializer.result()

    def result(self) -> str:
        """
        Return the result of the serializer.

        Returns:
          The serialized xml.
        """

        return self.buffer.getvalue()

    def start_element(self, name: str) -> typing.Self:
        """
        Write the start of an element with the given name.

        Args:
          name: the raw XML 1.0 name of the element type.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        self.write(f"<{name}>")
        self.indent()

        return self

    def end_element(self, name: str) -> typing.Self:
        """
        Write the end of an element with the given name.

        Args:
          name: the raw XML 1.0 name of the element type.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        self.dedent()
        self.write(f"</{name}>")

        return self

    def write_str(self, element: str, value: str, width: int = 88) -> typing.Self:
        """
        Write a string value surrounded by the given element.

        Args:
          element: The start and end element surrounding the string.
          value: The string value to write into the xml.
          width: The maximum length of characters per line. If the string
             exceeds this width, it is rendered in several lines.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        content = f"<{element}>"

        if len(value) > width:
            content += "\n"
            content += "\n".join(
                "\n".join(
                    textwrap.wrap(
                        line,
                        width,
                        initial_indent="  ",
                        subsequent_indent="  ",
                        break_long_words=False,
                        replace_whitespace=False,
                    )
                )
                for line in value.splitlines()
            )
            content += "\n"
        else:
            content += value

        content += f"</{element}>"

        return self.write(content)

    def write_bool(self, element: str, value: bool) -> typing.Self:
        """
        Write a boolean value surrounded by the given element.

        Args:
          element: The start and end element surrounding the boolean.
          value: The boolean value to write into the xml.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        return self.write(f"<{element}>{'Yes' if value else 'No'}</{element}>")

    def write_int(self, element: str, value: int) -> typing.Self:
        """
        Write an integer value surrounded by the given element.

        Args:
          element: The start and end element surrounding the integer.
          value: The integer value to write into the xml.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        return self.write(f"<{element}>{int(value)}</{element}>")

    def write_float(self, element: str, value: float) -> typing.Self:
        """
        Write a float value surrounded by the given element.

        Args:
          element: The start and end element surrounding the float.
          value: The float value to write into the xml.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        return self.write(f"<{element}>{self.float_to_str(value)}</{element}>")

    def write_date(self, element: str, value: datetime.date) -> typing.Self:
        """
        Write a date value surrounded by the given element.

        Args:
          element: The start and end element surrounding the date.
          value: The date value to write into the xml.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        isoformat = "{:04d}-{:02d}-{:02d}".format(value.year, value.month, value.day)

        if (tzinfo := getattr(value, "tzinfo", None)) and isinstance(tzinfo, datetime.tzinfo):
            isoformat += _format_offset(offset) if (offset := tzinfo.utcoffset(None)) else "Z"

        return self.write(f"<{element}>{isoformat}</{element}>")

    def write_time(self, element: str, value: datetime.time) -> typing.Self:
        """
        Write a time value surrounded by the given element.

        Args:
          element: The start and end element surrounding the time.
          value: The time value to write into the xml.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        isoformat = "{:02d}:{:02d}:{:02d}.{:03d}".format(
            value.hour, value.minute, value.second, value.microsecond // 1000
        )
        if (tzinfo := getattr(value, "tzinfo", None)) and isinstance(tzinfo, datetime.tzinfo):
            isoformat += _format_offset(offset) if (offset := tzinfo.utcoffset(None)) else "Z"

        return self.write(f"<{element}>{isoformat}</{element}>")

    def write_datetime(self, element: str, value: datetime.datetime) -> typing.Self:
        """
        Write a datetime value surrounded by the given element.

        Args:
          element: The start and end element surrounding the datetime.
          value: The datetime value to write into the xml.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        isoformat = "{:04d}-{:02d}-{:02d}".format(value.year, value.month, value.day)

        isoformat += "T"

        isoformat += "{:02d}:{:02d}:{:02d}.{:03d}".format(
            value.hour, value.minute, value.second, value.microsecond // 1000
        )

        if (tzinfo := getattr(value, "tzinfo", None)) and isinstance(tzinfo, datetime.tzinfo):
            isoformat += _format_offset(offset) if (offset := tzinfo.utcoffset(None)) else "Z"

        return self.write(f"<{element}>{isoformat}</{element}>")

    def write(self, value: str) -> typing.Self:
        """
        Writes the value as a new line with the current indentation.

        Args:
          value: The value to write into the xml.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        buffer = textwrap.indent(
            value + ("\n" if not self.remove_whitespace else ""),
            "  " * (self.indentation if not self.remove_whitespace else 0),
        )

        self.buffer.write(buffer)

        return self

    def indent(self, level: int = 1) -> typing.Self:
        """
        Indent the upcoming lines.

        Args:
          level: By how many tabs to indent.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        self.indentation += level

        return self

    def dedent(self, level: int = 1) -> typing.Self:
        """
        Dedent the upcoming lines.

        Args:
          level: By how many tabs to dedent.

        Returns:
          The Serializer instance, allowing for method chaining.
        """

        self.indentation -= level

        return self
