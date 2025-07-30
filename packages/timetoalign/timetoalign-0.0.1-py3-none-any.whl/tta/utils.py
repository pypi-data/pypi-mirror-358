from __future__ import annotations

import hashlib
import itertools
import logging
import os.path as osp
from collections import defaultdict
from enum import Enum, StrEnum, auto
from fractions import Fraction
from functools import cache
from numbers import Number
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Optional,
    Type,
    TypeVar,
    overload,
)

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from processing.tta.conversions import Coordinate

logger = logging.getLogger(__name__)

# region NamedSources

S = TypeVar("S")


class NamedSources(Generic[S]):
    """Helper class that stores a particular type of things in a ._sources dictionary.
    The specialty is that you can optionally name things but still can retrieve each thing
    by its order of addition, whether it was named or not.
    """

    def __init__(self, **kwargs):
        self._sources: dict[int | str, S] = {}
        super().__init__(**kwargs)

    def _get_next_consecutive_integer(self) -> int:
        return len(self._sources)

    def _adapt_source(self, source: Any) -> S:
        return source

    def _add_source(self, source: S, name: Optional[str] = None) -> int | str:
        """Adds a 2d-array where one axis has shape 2, representing numerators and denominators of
        a sequence of fractions.
        If you assign a name you can retrieve it under that name, otherwise by the source's "name"
        attribute or, if unset or undefined, by the next consecutive integer that is not already
        used as a name.
        """
        source = self._adapt_source(source)
        self.validate_source(source)
        if name is None:
            name = getattr(source, "name", None)
        if name is None:
            name = self._get_next_consecutive_integer()
            if name in self._sources:
                raise ValueError(
                    f"The integer {name} that was assigned automatically is already taken. "
                    f"This should not have happened."
                )
        else:
            assert isinstance(
                name, str
            ), f"Name is expected to be a string, not a {type(name)!r}"
            if name in self._sources:
                raise ValueError(f"Name {name!r} is already taken.")
        self._sources[name] = source
        return name

    def get_key(self, key: str | int) -> int | str:
        """Get the key for a given source path or key. If the key is not found, it raises KeyError."""
        if key in self._sources:
            return key
        if isinstance(key, int):
            if key < 0:
                key += len(self._sources)
            if key < 0 or key >= len(self._sources):
                raise IndexError(
                    f"Index {key} is out of bounds for sources of length {len(self._sources)}"
                )
            return list(self._sources.keys())[key]
        raise KeyError(f"Source {key!r} not found in sources.")

    def resolve_keys(
        self, keys: Optional[str | int | Iterable[str | int]] = None
    ) -> tuple[str | int, ...]:
        """Process input arguments."""
        if keys is None:
            return tuple(self._sources.keys())
        keys = [self.get_key(key) for key in make_argument_iterable(keys)]
        assert len(keys) > 0, f"Resolved names have zero-length: {keys!r}"
        return tuple(keys)

    def get_source(self, key: str | int) -> S:
        """Retrieve one of the previous inputs by its name."""
        if key in self._sources:
            return self._sources[key]
        elif isinstance(key, int):
            if key < 0:
                key += len(self._sources)
            if key < 0 or key >= len(self._sources):
                raise IndexError(
                    f"Index {key} is out of bounds for sources of length {len(self._sources)}"
                )
            return list(self._sources.values())[key]
        raise KeyError(
            f"Name {key!r} is not found in the sources. "
            f"Available names: {tuple(self._sources.keys())}"
        )

    def get_sources(
        self, names: Optional[str | int | Iterable[str | int]] = None
    ) -> tuple[S]:
        if names is None:
            if len(self._sources) == 0:
                raise ValueError(
                    "No data has been added to this object. "
                    "Use the method ._add_source() first"
                )
            sources = tuple(self._sources.values())
        else:
            names = self.resolve_keys(names)
            sources = tuple(self.get_source(name) for name in names)
        return sources

    def validate_source(self, source: S):
        return

    @overload
    def __getitem__(self, names: str | int) -> S: ...

    @overload
    def __getitem__(self, names: Iterable[str | int]) -> tuple[S]: ...

    def __getitem__(self, names: str | int | Iterable[str | int]) -> S | tuple[S]:
        if isinstance(names, (str, int)):
            return self.get_source(names)
        return self.get_sources(names)

    def __iter__(self) -> Iterator[S]:
        yield from self.get_sources()


class DivMaker(NamedSources[np.ndarray[int]]):
    """This is a convenient object for turning sequences of fractions into commensurate divs.
    It is equivalent to concatenating all sequences, passing them to the function shown below, and splitting them again.

        def fractions2divs(fracs: Iterable[Fraction]) -> np.ndarray[int]:
            numerators, denominators = np.array([(item.numerator,item.denominator) for item in fracs]).T
            lcm = np.lcm.reduce(denominators) # least common multiple
            return (numerators * lcm / denominators).astype(int)

    Example:

        STAR_WARS = np.array([ # durations of the star wars theme
            (1, 12),
            (1, 12),
            (1, 12),
            (1, 2),
            (1, 2),
            (1, 12),
            (1, 12),
            (1, 12),
            (1, 2),
            (1, 4)
        ])
        div_maker = DivMaker(STAR_WARS)
        div_maker[0] # yields [1, 1, 1, 6, 6, 1, 1, 1, 6, 3]

        POSITIONS = [Fraction(1, 20), Fraction(1, 32)] # fractions that we need our durations to be commensurate with
        div_maker.add_iterable_of_fractions(POSITIONS)
        durations, pos = div_maker # object is iterable (iterates through sequences added without names)
        list(durations) # yields [40, 40, 40, 240, 240, 40, 40, 40, 240, 120]

        OTHER_VALUES = (Fraction(i, 7) for i in range(7))
        div_maker.add_iterable_or_array(OTHER_VALUES, "other") # add the other values with a name
        div_maker[(1, "other", 0)] # when retrieving we can mix assigned names and indices of nameless sequences
        # OUTPUT:
        # (array([168, 105]),
        #  array([   0,  480,  960, 1440, 1920, 2400, 2880]),
        #  array([ 280,  280,  280, 1680, 1680,  280,  280,  280, 1680,  840]))

        div_maker.lcm # yields 3360, the common denominator for all values (least common multiple)
    """

    def __init__(
        self,
        *iterable_or_array: Iterable[Fraction] | np.ndarray[int],
        **named_iterables_or_arrays: Iterable[Fraction] | np.ndarray[int],
    ):
        """Pass one or several 2d-arrays (where one axis has shape 2) or one or several iterables of fractions.
        By passing keyword arguments you can assign names which you can use to retrieve the respective div sequences.
        """
        self._sources: dict[int | str, np.ndarray[int]] = {}
        for ioa in iterable_or_array:
            _ = self.add_iterable_or_array(ioa)
        for name, ioa in named_iterables_or_arrays.items():
            _ = self.add_iterable_or_array(ioa, name)

    @staticmethod
    def iterable_of_fractions_to_array(
        iterable_of_fractions: Iterable[Fraction],
    ) -> np.ndarray[int]:
        """Returns a numpy array of shape (2,n) for a given iterable of n :obj:`Fraction` objects."""
        return np.array(
            [(frac.numerator, frac.denominator) for frac in iterable_of_fractions]
        ).T

    def add_iterable_of_fractions(
        self,
        iterable_of_fractions: Iterable[Fraction],
        name: Optional[str | int] = None,
    ) -> int | str:
        """Adds some iterable of :obj:`Fraction` objects that can then be retrieved as divs.
        If you assign a name you can retrieve it under that name, otherwise by the integer corresponding to the
        order in which it was added. Iteration over the object goes only through nameless objects in their adding
        order, meaning that you can assign an integer name that will not be taken into account when iterating
        through the object.
        """
        arr = self.iterable_of_fractions_to_array(iterable_of_fractions)
        return self.add_iterable_or_array(arr, name=name)

    def _adapt_source(self, arr: np.ndarray) -> np.ndarray:
        arr = np.asarray(arr)
        assert arr.ndim == 2, f"Expected a 2D numpy array, not {arr.ndim}D"
        assert (
            2 in arr.shape
        ), f"One of the 2 dimensions needs to have shape 2. Received shape: {arr.shape}"
        if arr.shape[0] == 2:
            return arr
        return arr.T

    def add_iterable_or_array(
        self,
        iterable_or_array: Iterable[Fraction] | np.ndarray[int],
        name: Optional[str | int] = None,
    ):
        """Convenience function for calling either .add_iterable_of_fractions() or .add_frac_array() based on the
        input.
        """
        if isinstance(iterable_or_array, np.ndarray):
            return self._add_source(iterable_or_array, name)
        return self.add_iterable_of_fractions(iterable_or_array, name)

    def concatenated_frac_arrays(
        self, names: Optional[str | int | Iterable[str | int]] = None
    ) -> np.ndarray:
        """Concatenate the requested arrays in order to compute their LCM. All arrays have shape (2, n) and so does
        their concatenation ("horizontal stacking").
        """
        arrays = self.get_sources(names)
        if len(arrays) == 1:
            return arrays[0]
        return np.hstack(arrays)

    def get_divs(self, name: str | int) -> np.ndarray[int]:
        """Retrieve one of the previous inputs as divs, based on the LCM computed for all inputs together.
        Name can be a number for retrieving nameless inputs based on their input order.
        """
        if name not in self._sources:
            raise KeyError(name)
        numerators, denominators = self._sources[name]
        lcm = self.least_common_multiple()
        return (numerators * lcm / denominators).astype(int)

    @cache
    def _least_common_multiple(self, names: tuple[str | int]) -> int:
        _, denominators = self.concatenated_frac_arrays(names)
        return np.lcm.reduce(denominators)

    def least_common_multiple(
        self, names: Optional[str | int | Iterable[str | int]] = None
    ) -> int:
        """By default, the LCM is computed based on all sequences of fractions that this object holds.
        When you retrieve divs, they are always commensurate between all sequences."""
        names = self.resolve_keys(names)
        return self._least_common_multiple(names)

    @property
    def lcm(self):
        """For convenience."""
        return self.least_common_multiple()

    @overload
    def __getitem__(self, names: str | int) -> np.ndarray: ...

    @overload
    def __getitem__(self, names: Iterable[str | int]) -> tuple[np.ndarray]: ...

    def __getitem__(
        self, names: str | int | Iterable[str | int]
    ) -> np.ndarray | tuple[np.ndarray]:
        if isinstance(names, (str, int)):
            return self.get_divs(names)
        names = tuple(names)
        return tuple(self.get_divs(name) for name in names)

    def __iter__(self):
        existing_consecutive_integers = itertools.takewhile(
            lambda x: x in self._sources, itertools.count()
        )
        for i in existing_consecutive_integers:
            yield self.get_divs(i)


# endregion NamedSources
# region Enums


class FancyStrEnum(StrEnum):
    """This enum is used to define closed vocabularies (e.g. for function arguments) allowing for abbreviation aliases.

    Features:

        * It can be instantiated from either value: FancyStrEnum("abbr") == FancyStrEnum.abbreviation.
        * list(FancyStrEnum) returns only non-aliases
        * FancyStrEnum.get_abbreviations() returns a mapping from names to abbreviations

    Example:

        class Vocabulary(FancyStrEnum):
            abbreviation = auto() # assigns the name as value (making it lowercase as per StrEnum's default)
            abbr = abbreviation   # alias 1
            abb  = abbreviation   # alias 2
    """

    @classmethod
    def _missing_(cls, value):
        """
        Initialization from values, including aliases.

        Args:
            value: The value or name string to look up.

        Returns:
            The corresponding TimeUnit enum member.

        Raises:
            ValueError: If the value or name does not match any member or alias.
        """
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in cls.__members__:
                name = cls.__members__[lower_value]
                return cls(name)
        abbrv = cls.get_abbreviations(string=True)
        raise ValueError(
            f"'{value}' is not a valid {cls.__name__}. Available units are: {abbrv}"
        )

    @classmethod
    def get_abbreviations(cls, string=False) -> dict[str, str | list[str]]:
        """Returns a mapping from enum names/values to abbreviated alias values."""
        name2values = defaultdict(list)
        for value, name in cls.__members__.items():
            name2values[name].append(value)
        abbreviations = {}
        for name, values in name2values.items():
            abbreviations[name] = sorted(values, key=lambda x: len(x), reverse=True)[1:]
        if not string:
            return abbreviations
        str_components = []
        for name, values in abbreviations.items():
            if not values:
                str_components.append(name)
                continue
            abbrev_str = ", ".join(values)
            str_components.append(f"{name} ({abbrev_str})")
        return ", ".join(str_components)

    def __repr__(self):
        return f'"{self.name}"'

    def __str__(self):
        return self.name


class Domain(FancyStrEnum):
    musical = auto()
    """Logical time domain, also called logical time."""
    mu = musical

    physical = auto()
    """Physical time domain, also called real time."""
    ph = physical

    graphical = auto()
    """Graphical time domain, also called space or visual time."""
    gr = graphical


class EventCategory(FancyStrEnum):
    """Enumeration for event categories."""

    segments = auto()
    segment = segments
    seg = segments
    events = auto()
    event = events
    evt = events
    instant_events = auto()
    instant_event = instant_events
    inst_evt = instant_events
    inst = instant_events
    interval_events = auto()
    interval_event = interval_events
    intv_evt = interval_events
    intv = interval_events


class InstantType(FancyStrEnum):
    """Enumeration for types of instants."""

    instants = auto()
    instant = instants
    inst = instant
    starts = auto()
    start = starts
    ends = auto()
    end = ends


class IndexType(FancyStrEnum):
    """Enumeration for types of indices."""

    intervals = auto()
    interval = intervals
    intv = intervals
    instants = auto()
    instant = instants
    inst = instants
    starts = auto()
    start = starts
    ends = auto()
    end = ends


class InterpolationType(FancyStrEnum):
    linear = auto()
    nearest = auto()
    nearest_up = "nearest-up"
    zero = auto()
    slinear = auto()
    quadratic = auto()
    cubic = auto()
    previous = auto()
    next = auto()


class Missing(FancyStrEnum):
    DATA_UNDEFINED = auto()
    FIELD_MISSING_FROM_EVENT_DATA = auto()
    FIELD_NAME_UNDEFINED = auto()


class NumberType(Enum):
    """Members can be instantiated both via NumberType("name") and NumberType(value).

    Example:
        NumberType(int) is NumberType("int")
        # True
        NumberType(int).value(1.4)
        # 1

    """

    int = int
    float = float
    fraction = Fraction

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.name == value:
                    return member
        try:
            converted_numpy = convert_numpy_type_to_python_type(value)
            return cls(converted_numpy)
        except Exception:
            pass
        return None

    @classmethod
    def from_number(cls, number: Number):
        return cls(type(number))


class PartMap(FancyStrEnum):
    time_signature_map = auto()
    ts_map = time_signature_map
    tsm = time_signature_map

    key_signature_map = auto()
    ks_map = key_signature_map
    ksm = key_signature_map

    clef_map = auto()
    cm = clef_map

    measure_map = auto()
    mc = measure_map

    measure_number_map = auto()
    mn = measure_number_map

    metrical_position_map = auto()
    mpm = metrical_position_map

    beat_map = auto()
    bm = beat_map

    inv_beat_map = auto()
    ibm = inv_beat_map

    quarter_map = auto()
    qm = quarter_map

    inv_quarter_map = auto()
    iqm = inv_quarter_map

    quarter_duration_map = auto()
    qdm = quarter_duration_map


class Quantization(FancyStrEnum):
    continuous = auto()
    """Accomodating arbitrarily precise coordinates."""

    discrete = auto()
    """Accomodating only integer coordinates."""


class TimeUnit(FancyStrEnum):
    """"""

    # generic
    number = auto()

    # musical
    beats = auto()
    """beats"""
    b = beats  # b is an alias for beats
    """beats"""

    measures = auto()
    """measures"""
    m = measures  # m is an alias for measures
    """measures"""

    quarters = auto()
    """quarter notes"""
    q = quarters  # q is an alias for quarters
    """quarter notes"""

    ticks = auto()
    """ticks (MIDI's time unit)"""
    pulses = ticks
    """ticks (MIDI's time unit)"""

    # physical
    milliseconds = auto()
    """milliseconds"""
    ms = milliseconds  # ms is an alias for milliseconds
    """milliseconds"""

    seconds = auto()
    """seconds"""
    s = seconds  # s is an alias for seconds
    """seconds"""

    minutes = auto()
    """minutes"""

    samples = auto()
    """samples"""

    # graphical
    pixels = auto()
    """pixels"""
    px = pixels  # px is an alias for pixels
    """pixels"""

    meters = auto()
    """meters"""
    centimeters = auto()
    """centimeters"""
    cm = centimeters  # cm is an alias for centimeters
    """centimeters"""
    millimeters = auto()
    """millimeters"""
    mm = millimeters  # mm is an alias for millimeters
    """millimeters"""

    inches = auto()
    """inches"""

    points = auto()
    """points"""
    pt = points  # pt is an alias for points
    """points"""


class TraversalOrder(FancyStrEnum):
    """Enumeration for traversal orders."""

    breadth_first = auto()
    depth_first = auto()
    sorted = auto()


# endregion Enums
# region helper functions


def convert_numpy_type_to_python_type(np_type) -> Type:
    """Turns a numpy dtype into a native Python type"""
    return type(np.zeros(1, np_type).tolist()[0])


def get_time_units(
    domain=Domain | Iterable[Domain], quantization=Quantization | Iterable[Quantization]
) -> tuple[TimeUnit]:
    result = []
    if isinstance(domain, str):
        domain = Domain(domain)
        domain_dicts = [LINEAR_TIME_UNITS[domain]]
    else:
        domains = [Domain(d) for d in domain]
        domain_dicts = [LINEAR_TIME_UNITS[d] for d in domains]
    if isinstance(quantization, str):
        quantization = Quantization(quantization)
        for dd in domain_dicts:
            result.extend(dd[quantization])
    else:
        quantizations = [Quantization(q) for q in quantization]
        for dd in domain_dicts:
            for q in quantizations:
                result.extend(dd[q])
    return tuple(result)


def calculate_file_checksum(
    filepath: Path | str,
    hash_algorithm: Literal["sha256", "md5", "sha1", "sha512"] = "sha256",
    chunk_size=8192,
):
    """
    Calculates a system-agnostic checksum of a file.

    Args:
        filepath: The path to the file.
        hash_algorithm: The hashing algorithm to use (e.g., 'md5', 'sha1', 'sha256', 'sha512').
                              Defaults to 'sha256'.
        chunk_size: The size of chunks (in bytes) to read the file.
                          Larger chunks can be faster but use more memory.

    Returns:
        str: The hexadecimal digest of the file's checksum, or None if the file is not found.
    """
    if not osp.isfile(filepath):
        logger.error(f"File not found at {filepath}")
        return None

    try:
        # Get the hash constructor from hashlib
        hasher = hashlib.new(hash_algorithm)
    except ValueError:
        logger.error(
            f"Error: Unsupported hash algorithm '{hash_algorithm}'. "
            f"Available algorithms: {hashlib.algorithms_available}"
        )
        return None

    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break  # End of file
                hasher.update(chunk)
        return hasher.hexdigest()
    except IOError as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None


@overload
def make_argument_iterable(arg: Iterable) -> Iterable: ...


@overload
def make_argument_iterable(arg: Any) -> tuple: ...


def make_argument_iterable(
    arg, make_iterable_singular: bool = False
) -> tuple | Iterable:
    """make_iterable_singular can be set to True for cases where the result is expected to be an
    iterable of length one, e.g. "one tuple", in which case any iterable of length > 1 will be wrapped.
    """
    if arg is None:
        return tuple()
    if isinstance(arg, str):
        return (arg,)
    if not isinstance(arg, Iterable):
        return (arg,)
    try:
        if make_iterable_singular and len(arg) > 1:
            return (arg,)
    except TypeError:
        # arg probably a generator
        pass
    return arg


def new_interval_index(
    iix: pd.IntervalIndex,
    mask: pd.Series,
    new_left: Optional[int | float] = None,
    new_right: Optional[int | float] = None,
    new_closed=None,
) -> pd.IntervalIndex:
    """New values that are of type Fraction will be converted to float."""
    closed = new_closed if new_closed else iix.closed
    if new_left is None and new_right is None:
        return pd.IntervalIndex(iix[mask], closed=closed)
    iv_list = iix.to_numpy().tolist()
    (update_positions,) = np.where(mask)
    for i in update_positions:
        interval = iv_list[i]
        if new_left is None:
            left = interval.left
        else:
            left = to_float_if_fraction(new_left)
        if new_right is None:
            right = interval.right
        else:
            right = to_float_if_fraction(new_right)
        iv_list[i] = pd.Interval(left, right, closed)
    return pd.IntervalIndex(iv_list, name=iix.name, closed=closed)


@overload
def to_float_if_fraction(shift_by: Number) -> Number: ...


@overload
def to_float_if_fraction(shift_by: Fraction) -> float: ...


def to_float_if_fraction(shift_by: Number) -> Number:
    if isinstance(shift_by, Fraction):
        shift_by = float(shift_by)
    return shift_by


def shift_interval_index(
    iix: pd.IntervalIndex, shift_by=int | float
) -> pd.IntervalIndex:
    shift_by = to_float_if_fraction(shift_by)
    new_left = iix.left + shift_by
    new_right = iix.right + shift_by
    return pd.IntervalIndex.from_arrays(
        new_left, new_right, name=iix.name, closed=iix.closed
    )


def longer_intervals_first(
    iix: pd.IntervalIndex,
) -> pd.Series:
    """Helper to be used in .sort_index(key=longer_intervals_first)."""
    return pd.Series(list(zip(iix.left.values, -iix.length.values)))


def sort_interval_index_longer_first(
    iix: pd.IntervalIndex,
) -> pd.IntervalIndex:
    return iix[longer_intervals_first(iix).argsort()]


def sort_instants(df):
    """
    Sorts instants according to index and 'instant_type' column such that end instants
    precede coinciding start instants.
    """
    sort_order = pd.Index(
        df.instant_type.items()
    ).argsort()  # sorting by (index, instant_type) tuples
    return df.iloc[sort_order]


def make_unbounded_interval_index(
    iix: pd.IntervalIndex,
    left_unbounded: bool = False,
    right_unbounded: bool = True,
):
    """Takes a monotonically increasing IntervalIndex and extends the first and the last interval
    to -inf and inf so that it returns the first or last value for out-of-bounds queries. By default,
    only the right interval is replaced with one right-bounded by inf. Set left_unbounded=True to also
    replace the first interval with one left-bounded by -inf.
    """
    assert iix.is_non_overlapping_monotonic
    intervals = iix.to_list()
    first, last = intervals[0], intervals[-1]
    assert first.left < last.right
    infinite = float("inf")
    if left_unbounded:
        intervals[0] = pd.Interval(-infinite, first.right, closed=first.closed)
    if right_unbounded:
        intervals[-1] = pd.Interval(last.left, infinite, closed=last.closed)
    return pd.IntervalIndex(intervals, name=iix.name, closed=iix.closed)


def replace_interval_index_with_unbounded_one(
    interval_map: pd.DataFrame | pd.Series,
    left_unbounded: bool = False,
    right_unbounded: bool = True,
):
    if not (left_unbounded or right_unbounded):
        return interval_map
    unbounded_index = make_unbounded_interval_index(
        interval_map.index,
        left_unbounded=left_unbounded,
        right_unbounded=right_unbounded,
    )
    return interval_map.set_axis(unbounded_index)


def validate_interval_args(
    start: Coordinate,
    end: Optional[Coordinate | Number] = None,
    length: Optional[Coordinate | Number] = None,
):
    assert not (
        end is None and length is None
    ), "At least one of 'end' or 'length' must be defined."
    if end is not None and length is not None:
        assert (
            end == start + length
        ), f"The given {end=} does not correspond to {start+length=}"


def python_type_to_numpy_dtype(py_type):
    if isinstance(py_type, np.dtype):
        return py_type
    if py_type is int:
        return np.dtype(int)
    elif py_type is float:
        return np.dtype(float)
    elif py_type is bool:
        return np.dtype(bool)
    elif py_type is str:
        return np.dtype(object)
    elif py_type is list:
        return np.dtype(object)
    elif py_type is tuple:
        return np.dtype(object)
    elif py_type is dict:
        return np.dtype(object)
    elif py_type is complex:
        return np.dtype(complex)
    elif py_type is bytes:
        return np.dtype(bytes)
    elif py_type is type(None):
        return np.dtype(object)
    else:
        return np.dtype(object)


def compute_active_intervals(df_or_s: pd.DataFrame | pd.Series) -> pd.Series:
    """Based on the column 'instant_type' consisting of the values 'starts', 'ends', and 'instants',
    return a column of integers that represents the number of active intervals at any given point.
    The function assumes that the events are chronologically ordered such that 'ends' precede any
    co-occurring 'starts'. This is what guarantees that 0 values mark those moments where no
    intervals are active. If no 0-values are returned, chances are that there are intervals covering
    the entire time range, such as event-category 'segments'.
    """
    if isinstance(df_or_s, pd.Series):
        ser = df_or_s
    elif "instant_type" in df_or_s.columns:
        ser = df_or_s.instant_type
    else:
        assert isinstance(
            df_or_s.index, pd.IntervalIndex
        ), "DataFrame needs to have an 'instant_type' column or a pd.IntervalIndex"
        raise NotImplementedError("pd.IntervalIndex needs a different function.")
    inst_types = set(INSTANT_TYPE_ACTIVITY_CHANGE.keys())
    assert all(
        val in inst_types for val in ser.unique()
    ), f"Series has values that are not instant types: {ser.unique()}"
    return ser.map(INSTANT_TYPE_ACTIVITY_CHANGE).cumsum()


def treat_variadic_argument(*args) -> list:
    """Catch cases where a single iterable was given accidentally without unpacking."""
    if len(args) == 1:
        elem = args[0]
        if isinstance(elem, Iterable) and not isinstance(elem, (str, bytes)):
            logger.debug(
                f"Variadic argument with a single {type(elem).__name__} has been unpacked."
            )
            return elem
    return args


def get_boolean_mask_for_intervals(
    values: np.ndarray, iix: pd.IntervalIndex
) -> np.ndarray:
    """
    Returns a boolean mask for a NumPy array where True indicates that the value of the
    array at that position falls within any interval in IntervalIndex J.
    """
    mask = np.full(values.shape, False, dtype=bool)
    for interval in iix:
        mask = mask | ((values >= interval.left) & (values <= interval.right))
    return mask


# endregion helper functions
# region globals

# this controls the outputs of get_time_units() which, in return, controls the
# _allowed_units class attributes of the various Timeline classes.
LINEAR_TIME_UNITS = dict(
    musical=dict(
        continuous=[TimeUnit.quarters],
        discrete=[TimeUnit.ticks],
    ),
    physical=dict(
        continuous=[TimeUnit.milliseconds, TimeUnit.seconds],
        discrete=[TimeUnit.samples],
    ),
    graphical=dict(
        continuous=[
            TimeUnit.meters,
            TimeUnit.centimeters,
            TimeUnit.millimeters,
            TimeUnit.inches,
            TimeUnit.points,
        ],
        discrete=[TimeUnit.pixels],
    ),
)

INSTANT_TYPE_ACTIVITY_CHANGE = dict(
    instants=0,
    starts=1,
    ends=-1,
)
# endregion globals
