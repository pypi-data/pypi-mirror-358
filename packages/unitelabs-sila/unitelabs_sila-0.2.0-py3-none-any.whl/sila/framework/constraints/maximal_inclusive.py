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
class MaximalInclusive(Constraint[T]):
    """
    A constraint that enforces an upper inclusive bound on a value.

    This constraint ensures that a given value does not exceed a
    specified maximum inclusive bound. It can be applied to various
    types, including Integer, Real, Date, Time, and Timestamp. The
    constraint raises errors if the input value exceeds the defined
    upper bound or is of an incorrect type.

    Args:
      value: The upper inclusive limit for the value. The value must
        be of the same type as this attribute and must not exceed
        this limit.
    """

    value: T
    """
    The upper inclusive limit for the value. The value must be of
    the same type as this attribute and must not exceed this
    limit.
    """

    async def validate(self, value: T) -> bool:
        if not isinstance(value, type(self.value)):
            raise TypeError(f"Expected value of type '{type(self.value).__name__}', received '{type(value).__name__}'.")

        if not value <= self.value:
            raise ValueError(
                f"Value '{value}' must be less than or equal to the maximal inclusive limit of '{self.value}'."
            )

        return True

    def serialize(self, serializer: Serializer) -> None:
        if isinstance(self.value, int):
            serializer.write_int("MaximalInclusive", self.value)
        elif isinstance(self.value, float):
            serializer.write_float("MaximalInclusive", self.value)
        elif isinstance(self.value, datetime.date):
            serializer.write_date("MaximalInclusive", self.value)
        elif isinstance(self.value, datetime.time):
            serializer.write_time("MaximalInclusive", self.value)
        elif isinstance(self.value, datetime.datetime):
            serializer.write_datetime("MaximalInclusive", self.value)

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (Integer, Real, Date, Time, Timestamp)):
            raise ValueError(
                f"Expected constraint's data type to be 'Integer', 'Real', 'Date', 'Time' or 'Timestamp', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="MaximalInclusive")
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
        yield from deserializer.read_end_element(name="MaximalInclusive")

        return cls(typing.cast(T, value))
