import collections.abc
import dataclasses

import typing_extensions as typing

from sila import datetime

from ..data_types.date import Date
from ..data_types.integer import Integer
from ..data_types.real import Real
from ..data_types.string import String
from ..data_types.time import Time
from ..data_types.timestamp import Timestamp
from ..fdl import Characters, Deserializer, EndElement, Serializer, StartElement
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List

T = typing.TypeVar("T", str, int, float, datetime.date, datetime.time, datetime.datetime)


@dataclasses.dataclass
class Set(Constraint[T]):
    """
    A constraint that enforces that a value is part of a defined set
    of values.

    This class checks if a given value is one of the allowed values
    defined in the `values` attribute. The values can be of various
    types, including String, Integer, Real, Date, Time and Timestamp.

    Args:
      values: A sequence of allowed values. The value to be validated
        must be included in this sequence.

    Raises:
      ValueError: If the list of allowed values is empty.
    """

    values: collections.abc.Sequence[T]
    """
    A sequence of allowed values. The value to be validated
    must be included in this sequence.
    """

    def __post_init__(self):
        if not self.values:
            raise ValueError("The list of allowed values must not be empty.")

        self.__type = type(self.values[0])

        if any(type(value) is not self.__type for value in self.values):
            raise TypeError("The list of allowed values must all have the same type.")

    async def validate(self, value: T) -> bool:
        if not isinstance(value, self.__type):
            raise TypeError(f"Expected value of type '{self.__type.__name__}', received '{type(value).__name__}'.")

        if value not in self.values:
            raise ValueError(f"Value '{value}' is not in the set of allowed values.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.start_element("Set")
        for value in self.values:
            if isinstance(value, str):
                serializer.write_str("Value", value)
            elif isinstance(value, int):
                serializer.write_int("Value", value)
            elif isinstance(value, float):
                serializer.write_float("Value", value)
            elif isinstance(value, datetime.date):
                serializer.write_date("Value", value)
            elif isinstance(value, datetime.time):
                serializer.write_time("Value", value)
            elif isinstance(value, datetime.datetime):
                serializer.write_datetime("Value", value)

        serializer.end_element("Set")

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (String, Integer, Real, Date, Time, Timestamp)):
            raise ValueError(
                f"Expected constraint's data type to be 'String', 'Integer', 'Real', 'Date', 'Time' or 'Timestamp', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="Set")

        values: list[T] = []
        while True:
            token = yield

            if isinstance(token, StartElement):
                if token.name == "Value":
                    if issubclass(data_type, String):
                        value = yield from deserializer.read_str()
                    elif issubclass(data_type, Integer):
                        value = yield from deserializer.read_int()
                    elif issubclass(data_type, Real):
                        value = yield from deserializer.read_float()
                    elif issubclass(data_type, Date):
                        value = yield from deserializer.read_date()
                    elif issubclass(data_type, Time):
                        value = yield from deserializer.read_time()
                    elif issubclass(data_type, Timestamp):
                        value = yield from deserializer.read_datetime()

                    values.append(typing.cast(T, value))
                else:
                    raise ValueError(
                        f"Expected start element with name 'Value', received start element with name '{token.name}'."
                    )

            elif isinstance(token, EndElement):
                if token.name == "Value":
                    continue
                else:
                    break  # pragma: no cover

            elif isinstance(token, Characters):
                raise ValueError(f"Expected start element with name 'Value', received characters '{token.value}'.")

        if not values:
            raise ValueError("Expected at least one 'Value' element inside the 'Set' element.")

        return cls(values)
