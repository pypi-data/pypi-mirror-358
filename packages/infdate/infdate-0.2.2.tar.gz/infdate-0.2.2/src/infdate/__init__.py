# -*- coding: utf-8 -*-

"""
infdate: a wrapper around standard library’s datetime.date objects,
capable of representing positive and negative infinity
"""

from datetime import date, datetime
from math import inf, trunc
from typing import final, overload, Any, Final, TypeVar


# -----------------------------------------------------------------------------
# Public module constants:
# display definitions, format strings, upper and loer ordinal boundaries
# -----------------------------------------------------------------------------

INFINITE_DATE_DISPLAY: Final[str] = "<inf>"
NEGATIVE_INFINITE_DATE_DISPLAY: Final[str] = "<-inf>"

INFINITY_SYMBOL: Final[str] = "∝"
UP_TO_SYMBOL: Final[str] = "⤒"
FROM_ON_SYMBOL: Final[str] = "↥"

ISO_DATE_FORMAT: Final[str] = "%Y-%m-%d"
ISO_DATETIME_FORMAT_UTC: Final[str] = f"{ISO_DATE_FORMAT}T%H:%M:%S.%fZ"

MIN_ORDINAL: Final[int] = date.min.toordinal()
MAX_ORDINAL: Final[int] = date.max.toordinal()

RESOLUTION: Final[int] = 1


# -----------------------------------------------------------------------------
# Internal module constants:
# TypeVar for GenericDate
# -----------------------------------------------------------------------------

_GD = TypeVar("_GD", bound="GenericDate")


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class GenericDate:
    """Base Date object derived from an ordinal"""

    def __init__(self, ordinal: int | float, /) -> None:
        """Create a date-like object"""
        if ordinal in (-inf, inf):
            self.__ordinal = ordinal
        else:
            self.__ordinal = trunc(ordinal)
        #

    def toordinal(self: _GD) -> int | float:
        """to ordinal (almost like date.toordinal())"""
        return self.__ordinal

    def __lt__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: less"""
        return self.__ordinal < other.toordinal()

    def __le__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: less or equal"""
        return self < other or self == other

    def __gt__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: greater"""
        return self.__ordinal > other.toordinal()

    def __ge__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: greater or equal"""
        return self > other or self == other

    def __eq__(self: _GD, other, /) -> bool:
        """Rich comparison: equals"""
        return self.__ordinal == other.toordinal()

    def __ne__(self: _GD, other, /) -> bool:
        """Rich comparison: does not equal"""
        return self.__ordinal != other.toordinal()

    def __bool__(self: _GD, /) -> bool:
        """True only if a real date is wrapped"""
        return False

    def __hash__(self: _GD, /) -> int:
        """hash value"""
        return hash(f"date with ordinal {self.__ordinal}")

    def _add_days(self: _GD, delta: int | float, /):
        """Add other, respecting maybe-nondeterministic values"""
        # Check for infinity in either self or delta,
        # and return a matching InfinityDate if found.
        # Re-use existing objects if possible.
        for observed_item in (delta, self.__ordinal):
            for infinity_form in (inf, -inf):
                if observed_item == infinity_form:
                    if observed_item == self.__ordinal:
                        return self
                    #
                    return fromordinal(observed_item)
                #
            #
        #
        # +/- 0 corner case
        if not delta:
            return self
        #
        # Return a RealDate instance if possible
        return fromordinal(self.__ordinal + trunc(delta))

    def __add__(self: _GD, delta: int | float, /) -> _GD:
        """gd_instance1 + number capability"""
        return self._add_days(delta)

    __radd__ = __add__

    @overload
    def __sub__(self: _GD, other: int | float, /) -> _GD: ...
    @overload
    def __sub__(self: _GD, other: _GD | date, /) -> int | float: ...
    @final
    def __sub__(self: _GD, other: _GD | date | int | float, /) -> _GD | int | float:
        """subtract other, respecting possibly nondeterministic values"""
        if isinstance(other, (int, float)):
            return self._add_days(-other)
        #
        return self.__ordinal - other.toordinal()

    def __rsub__(self: _GD, other: _GD | date, /) -> int | float:
        """subtract from other, respecting possibly nondeterministic values"""
        return other.toordinal() - self.__ordinal

    def __repr__(self: _GD, /) -> str:
        """String representation of the object"""
        return f"{self.__class__.__name__}({repr(self.__ordinal)})"

    def __str__(self: _GD, /) -> str:
        """String display of the object"""
        return self.isoformat()

    def isoformat(self: _GD, /) -> str:
        """Date representation in ISO format"""
        return self.strftime(ISO_DATE_FORMAT)

    def strftime(self: _GD, fmt: str, /) -> str:
        """String representation of the date"""
        raise NotImplementedError

    def replace(self: _GD, /, year: int = 0, month: int = 0, day: int = 0) -> _GD:
        """Return a copy with year, month, and/or date replaced"""
        raise NotImplementedError


class InfinityDate(GenericDate):
    """Infinity Date object"""

    def __init__(self, /, *, past_bound: bool = False) -> None:
        """Store -inf or inf"""
        ordinal = -inf if past_bound else inf
        super().__init__(ordinal)

    def __repr__(self, /) -> str:
        """String representation of the object"""
        return f"{self.__class__.__name__}(past_bound={self.toordinal() == -inf})"

    def strftime(self, fmt: str, /) -> str:
        """String representation of the date"""
        if self.toordinal() == inf:
            return INFINITE_DATE_DISPLAY
        #
        return NEGATIVE_INFINITE_DATE_DISPLAY

    __format__ = strftime

    def replace(self, /, year: int = 0, month: int = 0, day: int = 0):
        """Not supported in this class"""
        raise TypeError(
            f"{self.__class__.__name__} instances do not support .replace()"
        )


# pylint: disable=too-many-instance-attributes
class RealDate(GenericDate):
    """Real (deterministic) Date object based on date"""

    def __init__(self, year: int, month: int, day: int) -> None:
        """Create a date-like object"""
        self._wrapped_date_object = date(year, month, day)
        self.year = year
        self.month = month
        self.day = day
        super().__init__(self._wrapped_date_object.toordinal())
        self.timetuple = self._wrapped_date_object.timetuple
        self.weekday = self._wrapped_date_object.weekday
        self.isoweekday = self._wrapped_date_object.isoweekday
        self.isocalendar = self._wrapped_date_object.isocalendar
        self.ctime = self._wrapped_date_object.ctime

    def __bool__(self, /) -> bool:
        """True if a real date is wrapped"""
        return True

    def __repr__(self, /) -> str:
        """String representation of the object"""
        return f"{self.__class__.__name__}({self.year}, {self.month}, {self.day})"

    def strftime(self, fmt: str, /) -> str:
        """String representation of the date"""
        return self._wrapped_date_object.strftime(fmt or ISO_DATE_FORMAT)

    __format__ = strftime

    def replace(self, /, year: int = 0, month: int = 0, day: int = 0):
        """Return a copy with year, month, and/or date replaced"""
        internal_object = self._wrapped_date_object
        return from_datetime_object(
            internal_object.replace(
                year=year or internal_object.year,
                month=month or internal_object.month,
                day=day or internal_object.day,
            )
        )


# -----------------------------------------------------------------------------
# Public module constants continued:
# absolute minimum and maximum dates
# -----------------------------------------------------------------------------

MIN: Final[GenericDate] = InfinityDate(past_bound=True)
MAX: Final[GenericDate] = InfinityDate(past_bound=False)


# -----------------------------------------------------------------------------
# Module-level factory functions
# -----------------------------------------------------------------------------


def from_datetime_object(source: date | datetime, /) -> GenericDate:
    """Create a new RealDate instance from a
    date or datetime object
    """
    return RealDate(source.year, source.month, source.day)


def from_native_type(
    source: Any,
    /,
    *,
    fmt: str = ISO_DATETIME_FORMAT_UTC,
    past_bound: bool = False,
) -> GenericDate:
    """Create an InfinityDate or RealDate instance from string or another type,
    assuming infinity in the latter case
    """
    if isinstance(source, str):
        return from_datetime_object(datetime.strptime(source, fmt))
    #
    if source == -inf or source is None and past_bound:
        return MIN
    #
    if source == inf or source is None and not past_bound:
        return MAX
    #
    raise ValueError(f"Don’t know how to convert {source!r} into a date")


def fromtimestamp(timestamp: float) -> GenericDate:
    """Create an InfinityDate or RealDate instance from the provided timestamp"""
    if timestamp == -inf:
        return MIN
    #
    if timestamp == inf:
        return MAX
    #
    stdlib_date_object = date.fromtimestamp(timestamp)
    return from_datetime_object(stdlib_date_object)


def fromordinal(ordinal: int | float) -> GenericDate:
    """Create an InfinityDate or RealDate instance from the provided ordinal"""
    if ordinal == -inf:
        return MIN
    #
    if ordinal == inf:
        return MAX
    #
    new_ordinal = trunc(ordinal)
    if not MIN_ORDINAL <= new_ordinal <= MAX_ORDINAL:
        raise OverflowError("RealDate value out of range")
    #
    stdlib_date_object = date.fromordinal(new_ordinal)
    return from_datetime_object(stdlib_date_object)


# -----------------------------------------------------------------------------
# Public module constants continued:
# minimum and maximum real dates
# -----------------------------------------------------------------------------

REAL_MIN: Final[GenericDate] = fromordinal(MIN_ORDINAL)
REAL_MAX: Final[GenericDate] = fromordinal(MAX_ORDINAL)


# -----------------------------------------------------------------------------
# Module-level factory functions continued
# -----------------------------------------------------------------------------


def fromisoformat(source: str, /) -> GenericDate:
    """Create an InfinityDate or RealDate instance from an iso format representation"""
    lower_source_stripped = source.strip().lower()
    if lower_source_stripped == INFINITE_DATE_DISPLAY:
        return MAX
    #
    if lower_source_stripped == NEGATIVE_INFINITE_DATE_DISPLAY:
        return MIN
    #
    return from_datetime_object(date.fromisoformat(source))


def fromisocalendar(year: int, week: int, weekday: int) -> GenericDate:
    """Create a RealDate instance from an iso calendar date"""
    return from_datetime_object(date.fromisocalendar(year, week, weekday))


def today() -> GenericDate:
    """Today as RealDate object"""
    return from_datetime_object(date.today())
