import collections.abc
import dataclasses

import typing_extensions as typing

from sila import datetime

from ..data_types.date import Date
from ..data_types.integer import Integer
from ..data_types.real import Real
from ..data_types.time import Time
from ..data_types.timestamp import Timestamp
from ..fdl import Deserializer, Serializer
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List

T = typing.TypeVar("T", int, float, datetime.date, datetime.time, datetime.datetime)


@dataclasses.dataclass
class MinimalInclusive(Constraint[T]):
    """
    A constraint that enforces a lower inclusive bound on a value.

    This constraint ensures that a given value is greater than or
    equal to the specified minimum inclusive bound. It can be applied
    to various types, including Integer, Real, Date, Time, and
    Timestamp. The constraint raises errors if the input value is
    less than the bound or if the input is of an incorrect type.

    Args:
      value: The lower inclusive limit for the value. The value must
        be of the same type as this attribute and must be greater
        than or equal to this limit.
    """

    value: T
    """
    The lower inclusive limit for the value. The value must be of
    the same type as this attribute and must be greater than or
    equal to this limit.
    """

    async def validate(self, value: T) -> bool:
        if not isinstance(value, type(self.value)):
            raise TypeError(f"Expected value of type '{type(self.value).__name__}', received '{type(value).__name__}'.")

        if not value >= self.value:
            raise ValueError(
                f"Value '{value}' must be greater than or equal to the minimal inclusive limit of '{self.value}'."
            )

        return True

    def serialize(self, serializer: Serializer) -> None:
        if isinstance(self.value, int):
            serializer.write_int("MinimalInclusive", self.value)
        elif isinstance(self.value, float):
            serializer.write_float("MinimalInclusive", self.value)
        elif isinstance(self.value, datetime.date):
            serializer.write_date("MinimalInclusive", self.value)
        elif isinstance(self.value, datetime.time):
            serializer.write_time("MinimalInclusive", self.value)
        elif isinstance(self.value, datetime.datetime):
            serializer.write_datetime("MinimalInclusive", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (Integer, Real, Date, Time, Timestamp)):
            raise ValueError(
                f"Expected constraint's data type to be 'Integer', 'Real', 'Date', 'Time' or 'Timestamp', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="MinimalInclusive")
        if issubclass(data_type, Integer):
            value = yield from deserializer.read_int()
        elif issubclass(data_type, Real):
            value = yield from deserializer.read_float()
        elif issubclass(data_type, Date):
            value = yield from deserializer.read_date()
        elif issubclass(data_type, Time):
            value = yield from deserializer.read_time()
        elif issubclass(data_type, Timestamp):
            value = yield from deserializer.read_datetime()
        yield from deserializer.read_end_element(name="MinimalInclusive")

        return cls(typing.cast(T, value))
