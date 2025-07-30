import datetime

import typing_extensions as typing


def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def _format_offset(off):
    s = ""
    if off is not None:
        if off.days < 0:
            sign = "-"
            off = -off
        else:
            sign = "+"
        hh, mm = divmod(off, datetime.timedelta(hours=1))
        mm, ss = divmod(mm, datetime.timedelta(minutes=1))
        s += "%s%02d:%02d" % (sign, hh, mm)
        if ss or ss.microseconds:
            s += ":%02d" % ss.seconds

            if ss.microseconds:
                s += ".%06d" % ss.microseconds
    return s


class date(datetime.date):
    """Date with time zone."""

    __slots__ = "_year", "_month", "_day", "_hashcode", "_tzinfo"

    def __new__(
        cls,
        year,
        month: typing.Optional[int] = None,
        day: typing.Optional[int] = None,
        tzinfo: typing.Optional[datetime.tzinfo] = None,
    ):
        """Constructor.

        Arguments:

        year, month, day, tzinfo (required, base 1)
        """
        if isinstance(year, bytes) and len(year) == 4 and 1 <= ord(year[2:3]) <= 12:
            self = datetime.date.__new__(cls, year)  # type: ignore
            self._setstate(year, month)
            self._hashcode = -1
            return self

        self = datetime.date.__new__(cls, year=year, month=month, day=day)  # type: ignore
        self._year = year
        self._month = month
        self._day = day
        self._hashcode = -1
        _check_tzinfo_arg(tzinfo)
        self._tzinfo = tzinfo
        return self

    def replace(
        self,
        year: typing.Optional[int] = None,
        month: typing.Optional[int] = None,
        day: typing.Optional[int] = None,
        tzinfo: typing.Union[None, bool, datetime.tzinfo] = True,
    ):
        """Return a new date with new values for the specified fields."""
        if year is None:
            year = self._year
        if month is None:
            month = self._month
        if day is None:
            day = self._day

        _tzinfo: typing.Optional[datetime.tzinfo] = None
        if tzinfo is True:
            _tzinfo = self.tzinfo
        elif isinstance(tzinfo, datetime.tzinfo):
            _tzinfo = tzinfo

        return type(self)(year, month, day, _tzinfo)

    # Read-only field accessors

    @property
    def tzinfo(self) -> typing.Optional[datetime.tzinfo]:
        """timezone info object"""
        return self._tzinfo

    def utcoffset(self):
        """Return the timezone offset as timedelta positive east of UTC (negative west of
        UTC)."""
        if self._tzinfo is None:
            return None
        offset = self._tzinfo.utcoffset(datetime.datetime(self._year, self._month, self._day, tzinfo=self._tzinfo))
        return offset

    # Comparisons of date objects with other.

    def __eq__(self, other):
        if isinstance(other, date):
            return self._cmp(other) == 0
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, date):
            return self._cmp(other) != 0
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, date):
            return self._cmp(other) <= 0
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, date):
            return self._cmp(other) < 0
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, date):
            return self._cmp(other) >= 0
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, date):
            return self._cmp(other) > 0
        return NotImplemented

    def _cmp(self, other):
        assert isinstance(other, date)
        y, m, d, tz = self.year, self.month, self.day, self.tzinfo
        y2, m2, d2, tz2 = other.year, other.month, other.day, other.tzinfo

        offset1 = (tz or datetime.timezone.utc).utcoffset(None) or datetime.timedelta(0)
        offset2 = (tz2 or datetime.timezone.utc).utcoffset(None) or datetime.timedelta(0)

        return _cmp((y, m, d, -offset1), (y2, m2, d2, -offset2))

    # Pickle support.

    def _getstate(self):
        yhi, ylo = divmod(self._year, 256)
        basestate = bytes([yhi, ylo, self._month, self._day])
        if self._tzinfo is None:
            return (basestate,)
        else:
            return (basestate, self._tzinfo)

    def _setstate(self, string, tzinfo):
        if tzinfo is not None and not isinstance(tzinfo, datetime.tzinfo):
            raise TypeError("bad tzinfo state arg")

        yhi, ylo, self._month, self._day = string
        self._year = yhi * 256 + ylo
        # pylint: disable=attribute-defined-outside-init
        self._tzinfo = tzinfo

    def __reduce__(self):
        return (self.__class__, self._getstate())

    def __repr__(self):
        """Convert to formal string, for repr().

        >>> dt = datetime(2010, 1, 1)
        >>> repr(dt)
        'datetime.datetime(2010, 1, 1, 0, 0)'

        >>> dt = datetime(2010, 1, 1, tzinfo=timezone.utc)
        >>> repr(dt)
        'datetime.datetime(2010, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)'
        """
        return "%s.%s(%d, %d, %d, tzinfo=%r)" % (
            self.__class__.__module__,
            self.__class__.__qualname__,
            self._year,
            self._month,
            self._day,
            self._tzinfo,
        )

    def isoformat(self):
        s = "%04d-%02d-%02d" % (self._year, self._month, self._day)

        off = self.utcoffset()
        tz = _format_offset(off)
        if tz:
            s += tz

        return s

    __str__ = isoformat


def _check_tzinfo_arg(tz):
    if tz is not None and not isinstance(tz, datetime.tzinfo):
        raise TypeError("tzinfo argument must be None or of a tzinfo subclass")
