from __future__ import annotations

import logging
import sys
import warnings
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from itertools import product
from numbers import Number
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Literal,
    Optional,
    Self,
    Sequence,
    Type,
    TypeAlias,
    Union,
)

import numpy as np
import pandas as pd
from pandas.core.dtypes.inference import is_scalar
from partitura.utils.generic import interp1d as pt_interp1d
from typing_extensions import TypeVar

from processing.metaframes import DF, DS, Meta, pd_concat
from processing.tta import utils
from processing.tta.common import D, RegisteredObject
from processing.tta.registry import ID_str, get_cmap, get_object_by_id, register_cmap
from processing.tta.utils import NumberType, TimeUnit, make_argument_iterable

logger = logging.getLogger(__name__)


# region Coordinates
@dataclass(frozen=True)
class CoordinateType:
    """Represents a specific type of coordinate, defined by a unit and a number type.

    Attributes:
        unit: The time unit of the coordinate.
        number_type: The numerical type of the coordinate's value.
    """

    unit: TimeUnit | str
    number_type: NumberType

    def __post_init__(self):
        object.__setattr__(self, "unit", TimeUnit(self.unit))
        object.__setattr__(self, "number_type", NumberType(self.number_type))

    @property
    def key(self):
        """A unique string key for this coordinate type."""
        return get_key(self.unit, self.number_type)


class CoordinateTypeFactory:
    """
    This Flyweight Factory creates and manages the CoordinateType objects. It ensures
    that flyweights are shared correctly. When the client requests a CoordinateType,
    the factory either returns an existing instance or creates a new one, if it
    doesn't exist yet.
    """

    _coordinate_types: Dict[str, CoordinateType] = {}

    def __init__(self, initial_types: Iterable[tuple[TimeUnit, NumberType]]) -> None:
        """Initializes the factory with a set of predefined coordinate types.

        Args:
            initial_types: An iterable of (TimeUnit, NumberType) tuples.
        """
        for dtype in initial_types:
            self._coordinate_types[self.get_key(*dtype)] = CoordinateType(*dtype)

    def get_key(self, unit: TimeUnit | str, number_type: NumberType) -> str:
        """Generates a unique string key for a given unit and number type.

        Args:
            unit: The TimeUnit or its string representation.
            number_type: The NumberType.

        Returns:
            A string key.
        """
        number_type = NumberType(number_type)
        return f"{unit}_{number_type.name}"

    def get_coordinate_type(
        self, dtype: tuple[TimeUnit, NumberType] | str
    ) -> CoordinateType:
        """Retrieves or creates a CoordinateType instance.

        Args:
            dtype: A (TimeUnit, NumberType) tuple, a string key, or a CoordinateType instance.

        Returns:
            The corresponding CoordinateType instance.

        Raises:
            ValueError: If dtype is None.
        """
        if dtype is None:
            raise ValueError("dtype cannot be None")
        if isinstance(dtype, CoordinateType):
            return dtype
        if isinstance(dtype, str):
            if coord_type := self._coordinate_types.get(dtype):
                return coord_type
            unit, number_type = dtype.split("_")
            return CoordinateType(unit, number_type)

        key = self.get_key(*dtype)
        if coord_type := self._coordinate_types.get(key):
            return coord_type
        new_coord_type = CoordinateType(*dtype)
        self._coordinate_types[key] = new_coord_type
        return new_coord_type

    def list_dtypes(self, as_string=False) -> list[str] | str:
        """Lists all managed coordinate type keys.

        Args:
            as_string: If True, returns a comma-separated string; otherwise, a list.

        Returns:
            A list of coordinate type keys or a single string.
        """
        dtypes = list(self._coordinate_types.keys())
        if as_string:
            return ", ".join(dtypes)
        return dtypes


unit_dtype_pairs = product(TimeUnit, NumberType)
COORDINATE_TYPES = CoordinateTypeFactory(unit_dtype_pairs)


def get_coordinate_type(dtype):
    """Retrieves a CoordinateType instance from the global factory.

    Args:
        dtype: The coordinate type identifier.

    Returns:
        A CoordinateType instance.
    """
    global COORDINATE_TYPES
    return COORDINATE_TYPES.get_coordinate_type(dtype)


def get_coordinate_value(coordinate: Coordinate | Number) -> Number:
    """Extracts the numerical value from a Coordinate or returns the number itself.

    Args:
        coordinate: The coordinate or number.

    Returns:
        The numerical value.
    """
    if isinstance(coordinate, Coordinate):
        return coordinate.value
    return coordinate


def treat_instants_argument(
    instants: Iterable[Coord] | Coord, ensure_unit: Optional[TimeUnit | str] = None
):
    """This is a combination of make_argument_iterable with get_coordinate_value.
    If `ensure_unit` is specified and any of the input values are Coordinates, the function raises
    a ValueError if they have different units or if their unit differs from the given ensure_unit.
    """
    if ensure_unit is None:
        return [get_coordinate_value(n) for n in utils.make_argument_iterable(instants)]
    result, units = [], set()
    for inst in utils.make_argument_iterable(instants):
        if isinstance(inst, Coordinate):
            result.append(inst.value)
            units.add(inst.unit)
        else:
            result.append(inst)
    if len(units) > 1:
        raise ValueError(f"Coordinates need to have unit {ensure_unit}; got: {units}")
    if len(units) == 1:
        coordinate_unit = units.pop()
        if ensure_unit != coordinate_unit:
            raise ValueError(
                f"Coordinates need to have unit {ensure_unit}; got: {coordinate_unit}"
            )
    return result


def treat_intervals_argument(
    intervals: (
        pd.IntervalIndex
        | Iterable[tuple[Coord, Coord]]
        | tuple[Coord, Coord]
        | pd.Interval
    ),
    ensure_unit: Optional[TimeUnit | str] = None,
    make_iterable_singular: bool = False,
) -> pd.IntervalIndex:
    if isinstance(intervals, pd.IntervalIndex):
        if intervals.closed != "left":
            warnings.warn(
                f"Received a pd.IntervalIndex whose intervals are not 'left'- but "
                f"{intervals.closed!r}-closed. Assuming this is on purpose."
            )
        return intervals
    intervals = utils.make_argument_iterable(
        intervals, make_iterable_singular=make_iterable_singular
    )
    intervals_are_pd = [isinstance(iv, pd.Interval) for iv in intervals]
    if all(intervals_are_pd):
        iix = pd.IntervalIndex(intervals, closed="left")
    else:
        if any(intervals_are_pd):
            intervals = [
                (iv.left, iv.right) if isinstance(iv, pd.Interval) else iv
                for iv in intervals
            ]
        lefts, rights = zip(*intervals)
        lefts = treat_instants_argument(lefts, ensure_unit=ensure_unit)
        rights = treat_instants_argument(rights, ensure_unit=ensure_unit)
        iix = pd.IntervalIndex.from_arrays(lefts, rights, closed="left")
    return iix


def get_key(unit: TimeUnit | str, number_type: NumberType) -> str:
    """Generates a unique string key for a unit and number type using the global factory.

    Args:
        unit: The TimeUnit or its string representation.
        number_type: The NumberType.

    Returns:
        A string key.
    """
    global COORDINATE_TYPES
    return COORDINATE_TYPES.get_key(unit, number_type)


def _safely_get_dtype_from_number_type(number_type: NumberType | Type) -> Type:
    dtype = number_type
    try:
        return dtype.value
    except AttributeError:
        return dtype


@dataclass(frozen=True)
class Coordinate:
    """Represents a numerical value associated with a specific CoordinateType.

    The numerical value is automatically converted to the specified number type upon instantiation.

    Attributes:
        value: The numerical value of the coordinate.
        dtype: The CoordinateType, (TimeUnit, NumberType) tuple, or string key defining the coordinate's type.
    """

    value: Number
    dtype: CoordinateType | tuple[TimeUnit, NumberType] | str

    def __post_init__(self):
        object.__setattr__(self, "dtype", get_coordinate_type(self.dtype))
        object.__setattr__(self, "value", self.number_type.value(self.value))

    @property
    def unit(self):
        """The TimeUnit of the coordinate."""
        return self.dtype.unit

    @property
    def number_type(self) -> NumberType:
        """The NumberType of the coordinate's value."""
        return self.dtype.number_type

    @property
    def coordinate_type(self) -> str:
        """The string key representing the coordinate's type."""
        return get_key(self.unit, self.number_type)

    def _check_unit(self, other: Any, operation_name: str):
        """Validates unit compatibility for an operation.

        Args:
            other: The other operand.
            operation_name: Name of the operation for error messages.

        Returns:
            The numerical value of the other operand.

        Raises:
            TypeError: If units are incompatible.
            NotImplementedError: If the other operand type is unsupported.
        """
        if isinstance(other, Coordinate):
            if self.unit != other.unit:
                raise TypeError(
                    f"Cannot perform {operation_name} on Coordinates with different units: "
                    f"{self.unit} and {other.unit}"
                )
            value = other.value
        elif isinstance(other, Number):
            value = other
        else:
            raise NotImplementedError(
                f"Cannot perform {operation_name} between Coordinate and {other!r} ("
                f"{type(other)})"
            )

        return value

    def __repr__(self):
        return f"C({self.value} {self.unit})"

    def __str__(self):
        return f"{self.value} {self.unit}"

    def __add__(self, other: Any) -> Self:
        other_value = self._check_unit(other, "addition")
        return Coordinate(self.value + other_value, self.coordinate_type)

    def __radd__(self, other: Any) -> Self:
        return self.__add__(other)

    def __sub__(self, other: Any) -> Self:
        other_value = self._check_unit(other, "subtraction")
        return Coordinate(self.value - other_value, self.coordinate_type)

    def __rsub__(self, other: Any) -> Any:
        other_value = self._check_unit(other, "subtraction")
        return Coordinate(other_value - self.value, self.coordinate_type)

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, Number):
            return Coordinate(self.value * other, self.coordinate_type)
        raise NotImplementedError(f"Cannot multiply Coordinate with type {type(other)}")

    def __rmul__(self, other: Any) -> Any:
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> Any:
        if isinstance(other, Number):
            if other == 0:
                raise ZeroDivisionError("division by zero")
            return Coordinate(self.value / other, self.coordinate_type)
        raise NotImplementedError(f"Cannot divide Coordinate by type {type(other)}")

    def __rtruediv__(self, other: Any) -> Any:
        if isinstance(other, Number):
            if other == 0:
                raise ZeroDivisionError("division by zero")
            return Coordinate(other / self.value, self.coordinate_type)
        raise NotImplementedError(f"Cannot divide Coordinate by type {type(other)}")

    def __floordiv__(self, other: Any) -> Any:
        if isinstance(other, Number):
            if other == 0:
                raise ZeroDivisionError("integer division by zero")
            return Coordinate(self.value // other, self.coordinate_type)
        raise NotImplementedError(f"Cannot divide Coordinate by type {type(other)}")

    def __rfloordiv__(self, other: Any) -> Any:
        raise NotImplementedError(
            "Cannot divide by Coordinate (you could use its .value instead)."
        )

    def __mod__(self, other: Any) -> Any:
        if isinstance(other, Number):
            if other == 0:
                raise ZeroDivisionError("modulo by zero")
            return Coordinate(self.value % other, self.coordinate_type)
        raise NotImplementedError(f"Cannot divide Coordinate by type {type(other)}")

    def __rmod__(self, other: Any) -> Any:
        raise NotImplementedError(
            "Cannot divide by Coordinate (you could use its .value instead)."
        )

    def __pow__(self, other: Any) -> Any:
        other_value = self._check_unit(other, "exponentiation")
        return Coordinate(self.value**other_value, self.coordinate_type)

    def __rpow__(self, other: Any) -> Any:
        raise NotImplementedError(
            "Cannot perform exponentiation with a Coordinate (you could use its .value instead)."
        )

    def __neg__(self) -> Self:
        return Coordinate(-self.value, self.coordinate_type)

    def __pos__(self) -> Self:
        return Coordinate(+self.value, self.coordinate_type)

    def __abs__(self) -> Self:
        return Coordinate(abs(self.value), self.coordinate_type)

    def __eq__(self, other: Any) -> bool:
        other_value = self._check_unit(other, "== comparison")
        return self.value == other_value

    def _compare(self, other: Any, op: str) -> bool:
        """Helper for comparison operations."""
        other_value = self._check_unit(other, f"{op} comparison")

        if op == "<":
            return self.value < other_value
        if op == "<=":
            return self.value <= other_value
        if op == ">":
            return self.value > other_value
        if op == ">=":
            return self.value >= other_value

    def __lt__(self, other: Any) -> bool:
        return self._compare(other, "<")

    def __le__(self, other: Any) -> bool:
        return self._compare(other, "<=")

    def __gt__(self, other: Any) -> bool:
        return self._compare(other, ">")

    def __ge__(self, other: Any) -> bool:
        return self._compare(other, ">=")


C = Coordinate  # alias
Coord: TypeAlias = Union[Number, Coordinate]


def convert_coordinate(
    coordinate: Coord,
    dtype: CoordinateType | tuple[TimeUnit, NumberType] | str,
) -> Coordinate:
    """Converts a numerical value or an existing Coordinate to a new Coordinate of the specified dtype.

    If the input is a Coordinate, its original unit and number type are ignored,
    and only its numerical value is used for creating the new Coordinate.

    Args:
        coordinate: The numerical value or Coordinate instance to convert.
        dtype: The target CoordinateType, (TimeUnit, NumberType) tuple, or string key.

    Returns:
        A new Coordinate object of the specified dtype.
    """
    coordinate_type = get_coordinate_type(dtype)
    value = coordinate.value if isinstance(coordinate, Coordinate) else coordinate
    return Coordinate(value, coordinate_type)


def make_coordinate(
    value: Coord,
    dtype: Optional[tuple[TimeUnit, NumberType] | str | CoordinateType] = None,
    unit: Optional[TimeUnit] = None,
    number_type: Optional[NumberType | Type[Number]] = None,
    default_unit: Optional[TimeUnit] = None,
    default_number_type: Optional[NumberType] = None,
) -> Coordinate:
    """Creates a Coordinate instance with flexible input options.

    Prioritizes `dtype` if provided. Otherwise, combines `unit` and `number_type`.
    Uses `default_unit` and `default_number_type` if `value` is a raw number and
    specific types are not given. If `value` is already a Coordinate, its properties
    can be overridden by explicit `unit` or `number_type` arguments.

    Args:
        value: The numerical value or an existing Coordinate.
        dtype: Optional target CoordinateType, (TimeUnit, NumberType) tuple, or string key.
        unit: Optional target TimeUnit or its string representation.
        number_type: Optional target NumberType or Python numeric type.
        default_unit: Default TimeUnit if `value` is a number and `unit` is not set.
        default_number_type: Default NumberType if `value` is a number and `number_type` is not set.

    Returns:
        A new Coordinate object.

    Raises:
        AssertionError: If final unit or number type cannot be determined.
    """
    unit_final, number_type_final = default_unit, default_number_type
    if isinstance(value, Coordinate):
        value_final = value.value
        unit_final, number_type_final = value.unit, value.number_type
    else:
        value_final = value
    if dtype is not None:
        dtype_resolved = get_coordinate_type(dtype)
        unit_final, number_type_final = dtype_resolved.unit, dtype_resolved.number_type
    if unit is not None:
        unit_final = unit
    if number_type is not None:
        number_type_final = number_type
    assert (
        unit_final is not None and number_type_final is not None
    ), f"Both unit and number type need to be specified for value {value}"
    try:
        return Coordinate(value_final, (unit_final, number_type_final))
    except TypeError as e:
        msg = f"{e}. Got: {type(value)}."
        if value_final != value:
            msg += f" Type after conversion: {type(value_final)}"
        raise TypeError(msg)


# endregion Coordinates
# region ConversionMap base class


def add_offset_arguments(
    offset_a: Optional[Number], offset_b: Optional[Number]
) -> Optional[Number]:
    """Adds two optional offset numbers.

    Args:
        offset_a: First offset.
        offset_b: Second offset.

    Returns:
        The sum of offsets, or one if the other is None, or None if both are None.
    """
    no_a = offset_a is None
    no_b = offset_b is None
    if no_a and no_b:
        return
    if no_a:
        return offset_b
    if no_b:
        return offset_a
    return offset_a + offset_b


MT = TypeVar(
    "MT"
)  # atomic data type that a map outputs; can be a tuple of atomic times for CombinationMaps


class ConversionMap(ABC, RegisteredObject[MT], Generic[MT]):
    _default_column_name: Optional[str] = None
    _cmap_category: str = None
    """The superclasses grouping classes which behave in the same way in concatenation name
    themselves in the _cmap_category class attribute so that their children inherit the info.
    This is used by the ConcatenationMap to see whether all maps have the same type.
    """
    targets_relative_to_origin: Optional[bool] = None
    """Currently not in use. This is meant to distinguish LinearMaps mapping to values that are relative
    to the same origin as the source values, from those that map to "absolute" values. Currently,
    when LinearMaps are concatenated, the former meaning is assumed, meaning that the scalar map

        [0, 2)  0.5
        [2, 3)  1.5

    will map the value 2.5 to 1.75: the converted length of the first region (2 * 0.5 = 1) plus the
    relative offset from the second region (0.5 * 1.5 = 0.75). If the scalar map was created from
    "absolute" LinearMaps, it would simply convert to 2.5 * 1.5 = 3.75. Instead of using a class
    attribute, there should probably be two different subclasses for the two behaviours.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        try:
            # register those conversion maps that can be instantiated with just the default arguments
            register_cmap(cls())
        except Exception:
            pass

    def __init__(
        self,
        target_unit: Optional[str] = None,
        column_name: Optional[str] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(id_prefix=id_prefix, uid=uid, **kwargs)
        self._target_unit = None
        self.target_unit = target_unit
        self._custom_conversion_function = conversion_function
        self._column_name = None
        self.column_name = column_name

    def get_meta(self) -> Meta:
        """Generates metadata for converted timestamp Series/DataFrames.

        Returns:
            A Meta object.
        """
        return Meta(
            map_id=self.id,
            map_type=self.class_name,
            target_unit=self.target_unit,
            column_name=self.column_name,
        )

    def __call__(self, data: Any, **kwargs) -> Any:
        return self.convert(data, **kwargs)

    @property
    def column_name(self) -> str:
        if self._column_name is not None:
            return self._column_name
        return self.id

    @column_name.setter
    def column_name(self, name: Optional[str]):
        if not (name is None or isinstance(name, str)):
            raise ValueError(f"Invalid column name {name} ({type(name)}).")
        if name is None:
            if self._default_column_name is None:
                self._column_name = None
                return
            self._column_name = f"{self.id}_{self._default_column_name}"
            return
        if not name.startswith(self.id):
            name = f"{self.id}_{name}"
        self._column_name = name

    @property
    def source_unit(self) -> None:
        """For compatibility. None means any source unit is acceptable."""
        return

    @property
    def target_unit(self) -> Optional[str]:
        return self._target_unit

    @target_unit.setter
    def target_unit(self, unit: Optional[str]):
        self._target_unit = unit

    def conversion_function(
        self, data: Number | np.ndarray, *args, **kwargs
    ) -> MT | np.ndarray[MT]:
        """Retrieves the appropriate conversion function and applies it after inferring
        and setting :attr:`source_type` from the data.

        Args:
            data: Input data to infer source number type from.
            *args: Positional arguments for the conversion function.
            **kwargs: Keyword arguments for the conversion function.

        Returns:
            The converted value as a number or a numpy array according to the input.
        """
        if self._custom_conversion_function:
            func = self._custom_conversion_function
        else:
            func = self.default_conversion_function
        return func(data, *args, **kwargs)

    def convert(
        self, data: pd.Series | np.ndarray | Sequence[Coord] | Coord, **kwargs
    ) -> DF | np.ndarray[MT] | pd.Series[MT] | tuple[MT, ...]:
        """Converts data from the source to the target coordinate types of each of the combined maps.

        Args:
            data: The data to convert.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            The converted data, type matching input (Series, ndarray, or Coordinate).

        Raises:
            TypeError: For unsupported input data types.
        """
        if isinstance(data, Coordinate):
            if data.unit != self.source_unit:
                raise ValueError(
                    f"Input Coordinate unit '{data.unit}' does not match "
                    f"CoordinatesMap source unit '{self.source_unit}'."
                )
            return self.convert_number(data.value, **kwargs)
        elif isinstance(data, Number):
            return self.convert_number(data, **kwargs)
        elif isinstance(data, pd.Series):
            return self.convert_series(data, **kwargs)
        elif isinstance(data, pd.Index):
            return self.convert_index(data, **kwargs)
        elif isinstance(data, pd.DataFrame):
            return self.convert_dataframe(data, **kwargs)
        elif isinstance(data, np.ndarray):
            return self.convert_array(data, **kwargs)
        elif isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            return [self.convert_number(elem, **kwargs) for elem in data]
        else:
            raise TypeError(f"Unsupported data type for conversion: {type(data)}")

    def _convert_array(self, data: np.ndarray, **kwargs) -> np.ndarray[MT]:
        return self.conversion_function(data, **kwargs)

    def convert_array(self, data: np.ndarray, **kwargs) -> np.ndarray[MT]:
        return self._convert_array(data, **kwargs)

    def convert_number(self, data: Number, **kwargs) -> MT:
        return self.conversion_function(data, **kwargs)

    def convert_index(self, data: pd.Index, **kwargs) -> pd.Index:
        """Converts a pandas Index.

        Args:
            data: The pandas Index to convert.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            A converted Index.
        """
        if data.size == 0:
            return pd.Index([])
        converted = self.convert_array(data.values)
        return pd.Index(converted)

    def convert_series(
        self,
        data: pd.Series,
        name: Optional[str] = None,
        as_dataframe: bool | dict[str, Literal] = False,
        **kwargs,
    ) -> DS | DF:
        """Converts a pandas Series.

        Args:
            data: The pandas Series to convert.
            name: Optional name for the resulting Series.
            as_dataframe: If True, returns a 1-column DataFrame.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            A converted pandas Series or DataFrame.
        """
        if data.size == 0:
            return pd.Series()
        converted = self.convert_array(data.values, **kwargs)
        result = DF(converted, index=data.index).iloc[
            :, 0
        ]  # creating series right away would fail for
        # structured arrays
        if name is None:
            result = result.rename(self.column_name)
        else:
            result = result.rename(name)
        if as_dataframe:
            return result.to_frame()
        return result

    def convert_dataframe(self, data: pd.DataFrame, **kwargs) -> DF:
        """Converts a pandas DataFrame."""
        converted_series = [
            self.convert_series(column, name=kwargs.pop("column_name", name), **kwargs)
            for name, column in data.items()
        ]
        return pd_concat(converted_series, axis=1)

    def _make_inverse_column_name(
        self,
    ):
        if "_" not in self.column_name:
            return self.column_name
        id_part, name_part = self.column_name.split("_", maxsplit=1)
        if not name_part:
            return id_part
        try:
            # if the name is a unit, replace it with the new target unit
            _ = TimeUnit(name_part)
            return f"{id_part}_{self.source_unit}"
        except ValueError:
            # otherwise, leave as is
            return self.column_name

    @abstractmethod
    def get_inverse(self) -> Self:
        # ToDo: factor out calling ConversionMap._make_inverse_column_name() and assigning
        # id_prefix="imap"
        raise NotImplementedError

    @abstractmethod
    def default_conversion_function(self, value, kwargs):
        """Default conversion logic, to be implemented by subclasses.

        Args:
            value: The numerical value or array to convert.
            **kwargs: Additional arguments.

        Raises:
            NotImplementedError: If not overridden by a subclass or provided via `conversion_function`.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement default_conversion_function "
            "or be instantiated with a conversion_function."
        )

    def _repr_additional_properties(self) -> list[str]:
        return [
            f"id={self.id!r}",
            f"target_unit={self.target_unit}",
            f"column_name={self.column_name!r}",
        ]

    def __repr__(self):
        repr_string = f"{self.__class__.__name__}("
        additional_properties = self._repr_additional_properties()
        if additional_properties:
            repr_string += "\n\t"
            repr_string += ",\n\t".join(additional_properties)
            repr_string += "\n"
        repr_string += ")"
        return repr_string


class _TargetTypeMixin:
    """Mixin for composing ConversionMaps that have a target type.
    Adds methods and properties for getting the type in multiple ways.
    """

    _default_target_type: Optional[NumberType] = None

    def __init__(self, target_type=None, *args, **kwargs):
        self._target_type = None
        self.target_type = target_type
        super().__init__(*args, **kwargs)

    @property
    def target_type(self) -> Type[CT]:
        return self._target_type

    @target_type.setter
    def target_type(self, target_type: Optional[Type]):
        if target_type is None:
            self._target_type = self._default_target_type
        else:
            try:
                target_type = NumberType(target_type)
            except ValueError:
                pass
            self._target_type = target_type

    @property
    def target_dtype(self) -> np.dtype:
        """For constructing numpy arrays."""
        return utils.python_type_to_numpy_dtype(self._target_type)

    @property
    def target_fields(self) -> list[tuple[str, np.dtype | str]]:
        return [(self.column_name, self.target_dtype)]

    def convert_array(self, data: np.ndarray, **kwargs) -> np.ndarray[MT]:
        """Returns a structured array based on column_name and target type.
        To obtain a plain numpy array, use the _convert_array() method.
        """
        converted_array = super().convert_array(data, **kwargs)
        return np.array(converted_array, dtype=self.target_fields)


class _SourceTypeMixin:

    def __init__(self, *args, **kwargs):
        self._source_type = None
        super().__init__(*args, **kwargs)

    @property
    def source_type(self) -> NumberType:
        """The NumberType of the source values (inferred at conversion time)."""
        if self._source_type is None:
            raise ValueError(
                f"source_type for {self.id} is not yet inferred (call convert first)."
            )
        return self._source_type

    def conversion_function(
        self, data: Number | np.ndarray, *args, **kwargs
    ) -> Number | np.ndarray:
        self._infer_source_type(data)
        self.logger.debug(
            f"Source type after inferring from {data.__class__.__name__}: {self.source_type}"
        )
        return super().conversion_function(data, *args, **kwargs)

    def _infer_source_type(
        self, data: pd.Series | np.ndarray | Sequence[Coord] | Number | Coordinate
    ) -> None:
        """Infers and sets the :attr:`source_type` based on the input data.

        Args:
            data: The input data.
        """
        if isinstance(data, (pd.Series, pd.Index, np.ndarray, Sequence)):
            try:
                item = data[0]
            except KeyError:
                # the error appears (hopefully) because it's a Series
                item = data.iloc[0]
        else:
            item = data
        if isinstance(item, Coordinate):
            self._source_type = item.number_type
        else:
            self._source_type = NumberType(item.__class__)


# endregion ConversionMap base class
# region ConstantMap

CT = TypeVar(
    "CT", bound=Union[int, float, complex, bool, str, bytes, list, tuple, type(None)]
)


class ConstantMap(_TargetTypeMixin, ConversionMap[CT], Generic[CT]):
    """
    A CoordinatesMap that maps any input value to a single constant value (coordinate or other).

    """

    _cmap_category: str = "ConstantMap"

    targets_relative_to_origin: Optional[bool] = False

    def __init__(
        self,
        constant: CT,
        target_type: Optional[Type] = None,
        target_unit: Optional[str] = None,
        column_name: Optional[str] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        """
        Initializes a ConstantMap.

        Args:
            constant:
                The target constant that all inputs will map to. It could be a string, e.g. a filename,
                or a coordinate.
            target_type:
                The type of the constant. Will typically not be specified because it can be inferred.
                If specified, the constant value will be converted accordingly.
            id_prefix: Prefix for the map's ID.
            uid: Unique identifier for the map.
        """
        super().__init__(
            target_type=target_type,
            target_unit=target_unit,
            column_name=column_name,
            conversion_function=conversion_function,
            id_prefix=id_prefix,
            uid=uid,
            **kwargs,
        )
        self._constant: CT = None
        self.constant = constant

    def get_meta(self) -> Meta:
        """Generates metadata for converted timestamp Series/DataFrames.

        Returns:
            A Meta object.
        """
        return Meta(
            map_id=self.id,
            map_type=self.class_name,
            constant=self.constant,
            target_unit=self.target_unit,
            column_name=self.column_name,
        )

    @property
    def constant(self) -> CT:
        return self._constant

    @constant.setter
    def constant(self, constant: CT):
        if self._target_type is None:
            self._target_type = type(constant)
        else:
            if isinstance(self._target_type, NumberType):
                tt = self._target_type.value
            else:
                tt = self._target_type
            if not isinstance(constant, tt):
                constant = self._target_type(constant)
        self._constant = constant

    def default_conversion_function(
        self, value: Union[Number, np.ndarray], **kwargs
    ) -> Union[Number, np.ndarray]:
        """
        Returns the constant value, ignoring the input `value`.

        If the input `value` is an array-like structure, an array of the constant
        value with the same shape/size as the input `value` is returned, using
        the number type of the `constant` Coordinate.

        Args:
            value: The input numerical value or array. This is used to determine
                   the shape of the output if it's an array, but its content is ignored.
            **kwargs: Additional arguments (not used by this function).

        Returns:
            The constant value, or an array filled with the constant value.
        """
        constant_value = self.constant
        if is_scalar(value):
            return constant_value
        else:
            dtype = self.target_dtype
            return np.full_like(value, constant_value, dtype=dtype)

    def get_inverse(self) -> Optional[CoordinatesMap]:
        """
        Inverse CoordinatesMap is not defined for ConstantMap.

        Raises:
            NotImplementedError: Always, as inverse is not meaningful for ConstantMap.
        """
        raise NotImplementedError("Cannot map from a constant to the original values.")

    def _repr_additional_properties(self) -> list[str]:
        """
        Provides additional properties for the __repr__ string.

        Returns:
            A list of formatted property strings.
        """
        result = super()._repr_additional_properties()
        result.append(f"constant={self._constant!r}")
        return result


# endregion ConstantMap
# region RegionMap


class RegionMap(_TargetTypeMixin, ConversionMap[CT], Generic[CT]):
    """This the equivalent of a :class:`ConstantMap` but with different constants for different regions.
    It is also equivalent to a :class:`ConcatenationMap` of :class:`ConstantMap` instances but
    without the need to create individual instances.

    The conversion is defined by a pandas Series with an IntervalIndex mapping
    coordinate ranges (accourding to the source) to constants.
    """

    @classmethod
    def from_breaks(
        cls, breaks: Iterable[Number], constants: Iterable[Any], **kwargs
    ) -> Self:
        """Creates the intervals for the given cmaps using pd.IntervalIndex.from_breaks().
        This requires n+1 breaks for n constants. E.g.: breaks [0,8,15] => [[0,8), [8,15]).
        """
        iix = pd.IntervalIndex.from_breaks(breaks, closed="left")
        series = pd.Series(constants, index=iix, dtype=object)
        return cls(series, **kwargs)

    @classmethod
    def from_arrays(
        cls,
        left: Iterable[Number],
        right: Iterable[Number],
        constants: Iterable[Any],
        **kwargs,
    ) -> Self:
        """Creates the intervals for the given cmaps using pd.IntervalIndex.from_arrays().
        left, right, and constants need to have the same number of elements.
        """
        iix = pd.IntervalIndex.from_arrays(left, right, closed="left")
        series = pd.Series(constants, index=iix, dtype=object)
        return cls(series, **kwargs)

    def __init__(
        self,
        region_map: pd.Series,
        offset_source_map: Optional[pd.Series] = None,
        offset_target_map: Optional[pd.Series] = None,
        **kwargs,
    ):
        """Initializes a MultiScalarCoordinatesMap.

        Args:
            region_map: Series with IntervalIndex mapping source ranges to scalars.
            offset_source_map: Optional Series mapping source ranges to source offsets.
            offset_target_map: Optional Series mapping source ranges to target offsets.
            **kwargs: Arguments for CoordinatesMap.
        """
        super().__init__(**kwargs)
        self._region_map = None
        self.region_map = region_map
        self._offset_source_map = None
        self._offset_target_map = None
        if offset_source_map is not None:
            self.offset_source_map = offset_source_map
        if offset_target_map is not None:
            self.offset_target_map = offset_target_map

    @property
    def offset_source_map(self):
        """Series mapping source coordinate ranges to source offsets."""
        return self._offset_source_map

    @offset_source_map.setter
    def offset_source_map(self, offset_source_map: pd.Series):
        self.validate_input_series(offset_source_map, "offset_source_map", self.length)
        self._offset_source_map = offset_source_map

    @property
    def offset_target_map(self):
        """Series mapping source coordinate ranges to target offsets."""
        return self._offset_target_map

    @offset_target_map.setter
    def offset_target_map(self, offset_target_map: pd.Series):
        # Target offset map's length isn't directly tied to source length like scalar/source_offset maps
        self.validate_input_series(offset_target_map, "offset_target_map")
        self._offset_target_map = offset_target_map

    @property
    def region_map(self):
        """Series with IntervalIndex mapping source ranges to scalar values."""
        return self._region_map

    @region_map.setter
    def region_map(self, scalar_map: pd.Series):
        self.validate_input_series(scalar_map, "scalar_map")
        self._region_map = scalar_map
        self.length = scalar_map.index.right.max()

    def default_conversion_function(
        self,
        value: Union[Number, np.ndarray],
        left_unbounded: bool = False,
        right_unbounded: bool = True,
        **kwargs,
    ) -> Union[Number, np.ndarray]:
        """Applies interval-based offsets and scalar multiplication.

        Args:
            value: Input value(s).
            left_unbounded: If True, first interval of maps is left-unbounded.
            right_unbounded: If True, last interval of maps is right-unbounded.
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        self.logger.debug(
            f"{self.class_name}.default_conversion_function({left_unbounded=}, {right_unbounded=}, "
            f"{kwargs=})"
        )
        converted_value = value
        osm = self.get_offset_source_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        if osm is not None:
            offset_source = get_values_from_interval_map(osm, value)
            converted_value = converted_value + offset_source
        sc = self.get_region_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        converted_value = get_values_from_interval_map(sc, converted_value)
        otm = self.get_offset_target_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        if otm is not None:
            offset_target = get_values_from_interval_map(otm, value)
            converted_value = converted_value + offset_target
        return converted_value

    def get_region_map(
        self, left_unbounded: bool = False, right_unbounded: bool = True
    ) -> pd.Series:
        """Retrieves the scalar map, optionally with unbounded intervals.

        Args:
            left_unbounded: If True, makes the first interval left-unbounded.
            right_unbounded: If True, makes the last interval right-unbounded.

        Returns:
            The scalar map Series.
        """
        sm = self._region_map
        if sm is None or not (right_unbounded or left_unbounded):
            return sm
        return utils.replace_interval_index_with_unbounded_one(
            sm, left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )

    def get_offset_source_map(
        self, left_unbounded: bool = False, right_unbounded: bool = True
    ) -> Optional[pd.Series]:
        """Retrieves the source offset map, optionally with unbounded intervals.

        Args:
            left_unbounded: If True, makes the first interval left-unbounded.
            right_unbounded: If True, makes the last interval right-unbounded.

        Returns:
            The source offset map Series, or None.
        """
        osm = self._offset_source_map
        if osm is None or not (right_unbounded or left_unbounded):
            return osm
        return utils.replace_interval_index_with_unbounded_one(
            osm, left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )

    def get_offset_target_map(
        self, left_unbounded: bool = False, right_unbounded: bool = True
    ) -> Optional[pd.Series]:
        """Retrieves the target offset map, optionally with unbounded intervals.

        Args:
            left_unbounded: If True, makes the first interval left-unbounded.
            right_unbounded: If True, makes the last interval right-unbounded.

        Returns:
            The target offset map Series, or None.
        """
        otm = self._offset_target_map
        if otm is None or not (right_unbounded or left_unbounded):
            return otm
        return utils.replace_interval_index_with_unbounded_one(
            otm, left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )

    def validate_input_series(
        self, s_map: pd.Series, arg_name: str, target_length: Optional[Number] = None
    ):
        """Validates an input Series for use in this map.

        Args:
            s_map: The Series to validate.
            arg_name: Name of the argument for error messages.
            target_length: Expected maximum right boundary of the IntervalIndex.

        Raises:
            ValueError: If Series is empty.
            AssertionError: If index is not IntervalIndex, not non-overlapping/monotonic, or length mismatches.
        """
        if s_map.size == 0:
            raise ValueError(f"{arg_name} cannot be empty")
        assert isinstance(
            s_map.index, pd.IntervalIndex
        ), f"The index of a {arg_name} needs to be an IntervalIndex."
        assert s_map.index.is_non_overlapping_monotonic, (
            f"The IntervalIndex of a {arg_name} needs to be "
            f"non-overlapping and monotonic."
        )
        if target_length is not None:
            this_length = s_map.index.right.max()
            assert this_length == target_length, (
                f"The index of the {arg_name} has length {this_length} "
                f"{self.source_unit} but should have {target_length}, "
                f"like the scalar_map."
            )

    def get_inverse(self) -> Optional["CoordinatesMap"]:
        raise NotImplementedError("Cannot get inverse for constants.")

    def _repr_additional_properties(self):
        result = super()._repr_additional_properties()
        region_map_str = self._region_map.to_string(max_rows=3, length=True)
        region_map_str = "\t" + "\n\t".join(region_map_str.split("\n"))
        result.append(f"region_map=\n{region_map_str}\n")
        return result


# endregion RegionMap
# region CoordinatesMap


class CoordinatesMap(_TargetTypeMixin, _SourceTypeMixin, ConversionMap[Coordinate]):
    """Converts coordinate values of a :class:`timeline` to another representation.

    Instantiated maps are callable as a shorthand for their .convert() method.
    Subclasses can define default units, number types, and inverse converters.
    """

    _default_source_unit: TimeUnit = TimeUnit.number
    _default_target_unit: TimeUnit = TimeUnit.number
    _default_target_type: Optional[NumberType] = None
    _default_inverse_class: Optional[Type["CoordinatesMap"]] = None
    targets_relative_to_origin: Optional[bool] = None

    @classmethod
    def from_conversion_map(
        cls,
        cmap: CoordinatesMap,
        source_unit: Optional[TimeUnit | str] = None,
        target_unit: Optional[TimeUnit | str] = None,
        target_type: Optional[NumberType] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        column_name: Optional[str] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        """Creates a new CoordinatesMap instance, inheriting properties from an existing one.

        Args:
            cls: The class to instantiate.
            cmap: The existing CoordinatesMap to base properties on.
            source_unit: Overrides source unit.
            target_unit: Overrides target unit.
            target_type: Overrides target number type.
            conversion_function: Overrides conversion function.
            id_prefix: ID prefix for the new map.
            uid: UID for the new map.
            **kwargs: Additional arguments for the new map's __init__.

        Returns:
            A new CoordinatesMap instance.
        """
        args = dict(locals())
        del args["cls"]
        del args["cmap"]
        del args["kwargs"]
        init_args = {}
        for arg, val in args.items():
            init_args[arg] = getattr(cmap, arg, val) if val is None else val
        init_args.update(kwargs)
        return cls(**init_args)

    def __init__(
        self,
        source_unit: Optional[TimeUnit | str] = None,
        target_type: Optional[Type] = None,
        target_unit: Optional[str] = None,
        column_name: Optional[str] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        """Initializes a CoordinatesMap.

        Args:
            source_unit: The unit of the source coordinates. Defaults to `_default_source_unit`.
            target_unit: The unit of the target coordinates. Defaults to `_default_target_unit`.
            target_type: The number type of the target coordinates. Defaults to `_default_target_type`.
                                If None, the source number type is preserved.
            conversion_function: Custom function for conversion logic.
            id_prefix: Prefix for the map's ID.
            uid: Unique identifier for the map.
        """
        super().__init__(
            target_type=target_type,
            target_unit=target_unit,
            column_name=column_name,
            conversion_function=conversion_function,
            id_prefix=id_prefix,
            uid=uid,
            **kwargs,
        )
        self._length = None
        self._source_unit = None
        self.source_unit = source_unit
        register_cmap(self)

    def get_meta(self) -> Meta:
        """Generates metadata for converted timestamp Series/DataFrames.

        Returns:
            A Meta object.
        """
        return Meta(
            map_id=self.id,
            map_type=self.class_name,
            source_unit=self.source_unit,
            target_unit=self.target_unit,
            column_name=self.column_name,
        )

    @property
    def length(self) -> Coordinate:
        """The length associated with this conversion map, in source units."""
        return self._length

    @length.setter
    def length(self, length: Coord):
        if self._source_type is None:
            if isinstance(length, Coordinate):
                self._source_type = length.number_type
                log_msg_detail = "length coordinate"
            else:
                self._source_type = NumberType.from_number(length)
                log_msg_detail = "length value"
            log_msg = (
                f"_source_type has been set to {self._source_type} "
                f"for {self.class_name} {self.id!r} based on the given {log_msg_detail}."
            )
            self.logger.debug(log_msg)
        self._length = self.make_coordinate(length)

    @property
    def target_length(self) -> Coordinate:
        """The length converted to the target unit."""
        return self.convert(self.length, right_unbounded=True)

    @property
    def source_coordinate_type(self) -> CoordinateType:
        """The full CoordinateType of the source."""
        if self._source_unit is None:
            raise ValueError(f"source_unit is None for {self.id}")
        if self._source_type is None:
            raise ValueError(
                f"source_type is None for {self.id} (inferred at conversion time)"
            )
        return get_coordinate_type((self._source_unit, self._source_type))

    @property
    def source_unit(self) -> TimeUnit:
        """The TimeUnit of the source values."""
        return self._source_unit

    @source_unit.setter
    def source_unit(self, source_unit: Optional[TimeUnit | str]):
        if source_unit is None:
            self._source_unit = TimeUnit(self._default_source_unit)
        else:
            self._source_unit = TimeUnit(source_unit)

    @property
    def target_coordinate_type(self) -> CoordinateType:
        """The full CoordinateType of the target."""
        if self._target_unit is None:
            raise ValueError(f"target_unit is None for {self.id}")
        effective_target_num_type = self.effective_target_type
        if effective_target_num_type is None:
            raise ValueError(f"Cannot determine effective target_type for {self.id}")
        return get_coordinate_type((self._target_unit, effective_target_num_type))

    @property
    def effective_target_type(self) -> NumberType:
        """The NumberType used for the output. Uses target_type if set, else source_type."""
        if self._target_type is not None:
            return self._target_type
        if self._source_type is None:
            raise ValueError(
                f"Cannot determine effective target number type for {self.id} as source_type is not inferred."
            )
        return self.source_type

    @property
    def target_unit(self) -> TimeUnit:
        """The TimeUnit of the target values."""
        return self._target_unit

    @target_unit.setter
    def target_unit(self, target_unit: Optional[TimeUnit | str]):
        if target_unit is None:
            self._target_unit = TimeUnit(self._default_target_unit)
        else:
            self._target_unit = TimeUnit(target_unit)

    def get_inverse_class(self) -> Optional[Type["CoordinatesMap"]]:
        """Retrieves the class designated as the inverse of this map.

        Returns:
            The inverse CoordinatesMap class, or None.
        """
        if self._default_inverse_class is None:
            return
        if isinstance(self._default_inverse_class, str):
            current_module = sys.modules[self.__class__.__module__]
            return getattr(current_module, self._default_inverse_class)
        return self._default_inverse_class

    def get_inverse(self) -> Optional["CoordinatesMap"]:
        """Creates an instance of the inverse conversion map.

        Returns:
            An inverse CoordinatesMap instance, or None.

        Raises:
            NotImplementedError: If no inverse is defined.
        """
        if cls := self.get_inverse_class() is not None:
            return cls.from_conversion_map(
                self, column_name=self._make_inverse_column_name(), id_prefix="imap"
            )
        raise NotImplementedError(
            f"No inverse CoordinatesMap has been defined for {self.__class__.__name__}."
        )

    def make_coordinate(self, value: Coord) -> Coordinate:
        """Creates a Coordinate in the map's source unit and inferred source number type.

        Args:
            value: The numerical value or an existing Coordinate.

        Returns:
            A new Coordinate object.
        """
        return convert_coordinate(value, (self.source_unit, self.source_type))

    def make_target_coordinate(self, value: Coord) -> Coordinate:
        """Creates a Coordinate in the map's target unit and effective target number type.

        Args:
            value: The numerical value or an existing Coordinate.

        Returns:
            A new Coordinate object.
        """
        return convert_coordinate(value, (self.target_unit, self.effective_target_type))

    def get_values_from_coordinates(
        self, data: DS | pd.Series | np.ndarray
    ) -> np.ndarray:
        """Extracts numerical values from an array/series of Coordinates, ensuring unit consistency.

        Args:
            data: The input data containing Coordinate objects.

        Returns:
            A NumPy array of numerical values.

        Raises:
            ValueError: If coordinates have multiple units or mismatch the map's source unit.
        """

        def get_unit(coordinate: Coordinate):
            return coordinate.unit

        def get_value(coordinate: Coordinate):
            return coordinate.value

        units = np.vectorize(get_unit)(data)
        n_units = np.unique(units).size
        if n_units > 1:
            raise ValueError(f"The coordinates have more than one unit: {units}")
        if units[0] != self.source_unit and self.source_unit != TimeUnit.number:
            warnings.warn(
                f"Expecting {self.source_unit!r} coordinates but these are {units[0]!r} coordinates."
            )
        values = np.vectorize(get_value)(data)
        return values

    def _array_to_target_type(self, converted_values: np.ndarray) -> np.ndarray:
        """Casts a NumPy array to the effective target number type if necessary.

        Args:
            converted_values: The array after unit conversion.

        Returns:
            The array, potentially cast to a new dtype.
        """
        if self._target_type is not None and self._target_type != self.source_type:
            dtype = _safely_get_dtype_from_number_type(
                self.effective_target_type
            )  # Workaround for strings
            return converted_values.astype(dtype)
        return converted_values

    def conversion_function(
        self, data: Number | np.ndarray, *args, **kwargs
    ) -> Number | np.ndarray:
        self._infer_source_type(data)
        return super().conversion_function(data, *args, **kwargs)

    def convert_array(self, data: np.ndarray, **kwargs) -> np.ndarray:
        """Converts a NumPy array.

        Args:
            data: The NumPy array to convert.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            A new NumPy array with converted values.
        """
        if data.size == 0:
            return np.array([], dtype=self.effective_target_type.value)
        values = data
        if data.dtype == object and isinstance(data[0], Coordinate):
            values = self.get_values_from_coordinates(data)
        converted_values = self.conversion_function(values, **kwargs)
        return self._array_to_target_type(converted_values)

    def convert_number(self, data: Number, **kwargs) -> Coordinate:
        converted_value = self.conversion_function(data, **kwargs)
        return self.make_target_coordinate(converted_value)

    def convert_series(
        self,
        data: pd.Series,
        name: Optional[str] = None,
        as_dataframe: bool | dict[str, Literal] = False,
        **kwargs,
    ) -> DS | DF:
        """Converts a pandas Series.

        Args:
            data: The pandas Series to convert.
            name: Optional name for the resulting Series.
            as_dataframe: If True, returns a DataFrame. If a dict, adds columns from dict.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            A converted pandas Series or DataFrame.
        """
        if data.size == 0:
            return data
        converted = self.convert_array(data.values, **kwargs)
        meta = deepcopy(getattr(data, "_meta", {}))
        meta.update(self.get_meta())
        if "length" in meta:
            meta["source_length"] = meta["length"]
            meta["length"] = self.convert(meta["source_length"])
        try:
            dtype = _safely_get_dtype_from_number_type(self.effective_target_type)
            if dtype == int:
                dtype = "Int64"
            elif dtype == Fraction:
                dtype = "object"
                converted = [Fraction(val) for val in converted]
            elif dtype == str:
                dtype = "string"
            try:
                result = DS(converted, dtype=dtype, index=data.index, meta=meta)
            except TypeError:
                if dtype == "Int64":
                    result = DS(converted, dtype=int, index=data.index, meta=meta)
                else:
                    raise
        except AttributeError:
            result = DS(converted, index=data.index, meta=meta)
            self.logger.warning(
                f"{self.effective_target_type=}, conversion result has dtype {result.dtype}"
            )
        if name is None:
            result = result.rename(self.column_name)
        else:
            result = result.rename(name)
        if as_dataframe:
            df_data = dict({result.name: result.values}, **self.get_meta())
            if isinstance(as_dataframe, dict):
                df_data.update(**as_dataframe)
            result = DF(df_data, index=result.index)
        return result

    def convert_dataframe(self, data: pd.DataFrame, **kwargs) -> DF:
        """Converts a pandas DataFrame."""
        converted_series = [
            self.convert_series(column, **kwargs) for _, column in data.items()
        ]
        return pd_concat(converted_series, axis=1)

    def convert_index(self, data: pd.Index, **kwargs) -> pd.Index:
        """Converts a pandas Index.

        Args:
            data: The pandas Index to convert.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            A new pandas Index with converted values.
        """
        if data.size == 0:
            return data.__class__([])
        if isinstance(data, pd.IntervalIndex):
            converted_lefts = self.convert_array(data.left, **kwargs)
            converted_rights = self.convert_array(data.right, **kwargs)
            return pd.IntervalIndex.from_arrays(
                converted_lefts, converted_rights, closed=data.closed
            )
        converted = self.convert_array(data.values, **kwargs)
        return data.__class__(converted)

    def _repr_additional_properties(self) -> list[str]:
        """Provides additional properties for the __repr__ string.

        Returns:
            A list of formatted property strings.
        """
        result = super()._repr_additional_properties()
        result.extend(
            [f"source_unit={self.source_unit!r}", f"target_unit={self.target_unit!r}"]
        )
        if self._target_type is not None:
            result.append(f"target_type={self.target_type}")
        if self._custom_conversion_function:
            result.append(
                f"custom_conversion_function={self._custom_conversion_function.__name__}"
            )
        return result


class InterpolationMap(CoordinatesMap):
    _cmap_type: str = "InterpolationMap"

    @classmethod
    def from_scalar_map(cls, scalar_map: pd.Series, **kwargs) -> Self:
        """From a Series with a non-overlapping monotonically increasing pd.IntervalIndex mapping
        coordinate regions to scalars.
        """
        converted_segment_lengths = scalar_map.index.length * scalar_map
        converted_segment_ends = converted_segment_lengths.cumsum()
        left_breaks = scalar_map.index.left.tolist() + [scalar_map.index[-1].right]
        right_breaks = [0] + converted_segment_ends.tolist()
        coordinate_map = pd.Series(
            right_breaks,
            index=left_breaks,
        )
        return cls(coordinate_map, **kwargs)

    def __init__(
        self,
        coordinate_map: pd.Series,
        kind: utils.InterpolationType | str = "linear",
        fill_value: Optional[Number] = None,
        source_unit: Optional[TimeUnit | str] = None,
        target_type: Optional[Type] = None,
        target_unit: Optional[str] = None,
        column_name: Optional[str] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        """Initializes a ShiftMap.

        Args:
            offset_source: Offset applied before core conversion (in source units).
            offset_target: Offset applied after core conversion (in target units).
            **kwargs: Arguments for the base CoordinatesMap.
        """
        super().__init__(
            source_unit=source_unit,
            target_type=target_type,
            target_unit=target_unit,
            column_name=column_name,
            conversion_function=conversion_function,
            id_prefix=id_prefix,
            uid=uid,
            **kwargs,
        )
        self._coordinate_map = None
        self.coordinate_map = coordinate_map
        self._kind = None
        self.kind = kind
        self._fill_value = None
        self.fill_value = fill_value

    @property
    def coordinate_map(self) -> DS:
        return self._coordinate_map

    @coordinate_map.setter
    def coordinate_map(self, coordinate_map: pd.Series):
        if isinstance(coordinate_map, DS):
            new_value = coordinate_map
        else:
            new_value = DS(coordinate_map)
        self.validate_coordinate_map(coordinate_map)
        if self._target_type is None:
            self._infer_target_type(coordinate_map)
        else:
            new_value = new_value.astype(self.target_dtype)
        self._coordinate_map = new_value

    @property
    def kind(self) -> utils.InterpolationType:
        return self._kind

    @kind.setter
    def kind(self, kind: utils.InterpolationType | str):
        self._kind = utils.InterpolationType(kind)

    @property
    def fill_value(self) -> Optional[Number]:
        return self._fill_value

    @fill_value.setter
    def fill_value(self, fill_value: Optional[Number]):
        self._fill_value = fill_value

    def _infer_target_type(self, coordinate_map: pd.Series) -> None:
        """Infers and sets the :attr:`target_type` based on the coordinate_map.

        Args:
            coordinate_map: The coordinate_map.
        """
        self._target_type = utils.convert_numpy_type_to_python_type(
            coordinate_map.dtype
        )

    def validate_coordinate_map(self, coordinate_map):
        if not coordinate_map.index.is_monotonic_increasing:
            warnings.warn(
                f"The coordinate map index of a {self.id} is not monotonically increasing."
            )
        if not coordinate_map.is_monotonic_increasing:
            warnings.warn(
                f"The coordinate map values of {self.id} are not monotically increasing."
            )

    def get_interpolator(self, kind=None, fill_value=None):
        kind_arg = self.kind if kind is None else kind
        fill_value_arg = self.fill_value if fill_value is None else fill_value
        return pt_interp1d(
            x=self.coordinate_map.index.values,
            y=self.coordinate_map.values,
            dtype=self.target_dtype,
            kind=kind_arg,
            fill_value=fill_value_arg,
        )

    def default_conversion_function(
        self, value: Union[Number, np.ndarray], **kwargs
    ) -> Union[Number, np.ndarray]:
        """Applies source offset, then applies target offset.

        Args:
            value: Input value(s).
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        interpolator = self.get_interpolator(**kwargs)
        if isinstance(value, np.ndarray):
            if value.dtype == object:
                if self.target_dtype is None or self.target_dtype == object:
                    value = pd.to_numeric(value).values
                else:
                    value = value.astype(self.target_dtype)
            elif self.target_dtype != object and value.dtype != self.target_dtype:
                value = value.astype(self.target_dtype)
        return interpolator(value)


class ShiftMap(CoordinatesMap):
    """A CoordinatesMap that applies source and target offsets. This is useful because a ShiftMap
    can be combined with other maps and, depending on whether source and/or target offset is
    defined, coordinates can be either shifted before conversion (source unit) or after conversion
    (target unit).
    """

    targets_relative_to_origin: Optional[bool] = False
    _cmap_category = "ShiftMap"

    @classmethod
    def from_conversion_map(
        cls,
        cmap: CoordinatesMap,
        offset_source: Optional[Number] = None,
        offset_target: Optional[Number] = None,
        **kwargs,
    ):
        """Creates a ShiftMap from an existing CoordinatesMap, adding offsets.

        Args:
            cls: The ShiftMap class.
            cmap: The base CoordinatesMap.
            offset_source: Offset to apply to source values.
            offset_target: Offset to apply to target values.
            **kwargs: Additional arguments for ShiftMap initialization.

        Returns:
            A new ShiftMap instance.
        """
        init_args = {}
        if offset_source is None:
            init_args["offset_source"] = getattr(cmap, "source_unit", None)
        else:
            init_args["offset_source"] = offset_source
        if offset_target is None:
            init_args["offset_target"] = getattr(cmap, "target_unit", None)
        else:
            init_args["offset_target"] = offset_target
        init_args.update(kwargs)
        return super().from_conversion_map(cmap, **init_args)

    def __init__(
        self,
        offset_source: Optional[Number] = None,
        offset_target: Optional[Number] = None,
        source_unit: Optional[TimeUnit | str] = None,
        target_type: Optional[Type | NumberType | str] = None,
        target_unit: Optional[str] = None,
        column_name: Optional[str] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        """Initializes a ShiftMap.

        Args:
            offset_source: Offset applied before core conversion (in source units).
            offset_target: Offset applied after core conversion (in target units).
            **kwargs: Arguments for the base CoordinatesMap.
        """
        super().__init__(
            source_unit=source_unit,
            target_type=target_type,
            target_unit=target_unit,
            column_name=column_name,
            conversion_function=conversion_function,
            id_prefix=id_prefix,
            uid=uid,
            **kwargs,
        )
        self._offset_target = offset_target
        self._offset_source = offset_source

    @property
    def offset_source(self) -> Optional[Number]:
        """Offset applied to source values before the main conversion logic."""
        return self._offset_source

    @property
    def offset_target(self) -> Optional[Number]:
        """Offset applied to target values after the main conversion logic."""
        return self._offset_target

    def default_conversion_function(
        self, value: Union[Number, np.ndarray], **kwargs
    ) -> Union[Number, np.ndarray]:
        """Applies source offset, then applies target offset.

        Args:
            value: Input value(s).
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        if self._offset_source is not None:
            value = value + self._offset_source
        if self._offset_target is not None:
            value = value + self._offset_target
        return value

    def get_inverse(self) -> Optional["CoordinatesMap"]:
        """Calculates the inverse of this ShiftMap.

        Returns:
            An inverse CoordinatesMap instance.
        """
        # Ensure source_type is available for the inverse's target_type
        # This might require a dummy conversion if no conversion has happened yet.
        if self._source_type is None:
            self.logger.debug(
                f"Temporarily inferring source_type for {self.id} to create inverse."
            )
            self._infer_source_type(0)  # Infer with a dummy value

        cls = self.get_inverse_class()
        if cls is None:
            cls = self.__class__

        # Offsets are negated and swapped
        inv_offset_source = (
            None if self._offset_target is None else -self._offset_target
        )
        inv_offset_target = (
            None if self._offset_source is None else -self._offset_source
        )

        return cls(
            offset_source=inv_offset_source,
            offset_target=inv_offset_target,
            source_unit=self.target_unit,
            target_unit=self.source_unit,
            target_type=self.source_type,
            column_name=self._make_inverse_column_name(),
            id_prefix="imap",
        )

    def _repr_additional_properties(self):
        result = super()._repr_additional_properties()
        result.append(f"{self._offset_source=}, {self._offset_target=}")
        return result

    def __add__(self, other):
        if isinstance(other, ShiftMap):
            offset_source = add_offset_arguments(
                self._offset_source, other._offset_source
            )
            offset_target = add_offset_arguments(
                self._offset_target, other._offset_target
            )
            return self.__class__.from_conversion_map(
                self, offset_source=offset_source, offset_target=offset_target
            )
        return NotImplemented


class LinearMap(ShiftMap):
    """Base class for all conversions based on multiplication or division with a single scalar.
    Subclasses will give appropriate variable names to the init arg for usability.
    """

    targets_relative_to_origin: Optional[bool] = True
    _cmap_category: str = "LinearMap"

    @classmethod
    def from_conversion_map(cls, cmap: CoordinatesMap, scalar: Number = None, **kwargs):
        """Creates a ScalarCoordinatesMap from an existing map, adding/overriding the scalar.

        Args:
            cls: The ScalarCoordinatesMap class.
            cmap: The base CoordinatesMap.
            scalar: The scalar value for conversion.
            **kwargs: Additional arguments.

        Returns:
            A new ScalarCoordinatesMap instance.
        """
        init_args = {}
        init_args["scalar"] = (
            getattr(cmap, "scalar", None) if scalar is None else scalar
        )
        init_args.update(kwargs)
        return super().from_conversion_map(cmap, **init_args)

    def __init__(
        self,
        scalar: Number = 1,
        offset_source: Optional[Number] = None,
        offset_target: Optional[Number] = None,
        source_unit: Optional[TimeUnit | str] = None,
        target_unit: Optional[TimeUnit | str] = None,
        **kwargs,
    ):
        """Initializes a ScalarCoordinatesMap.

        Args:
            scalar: The scalar value for multiplication/division. Must be positive.
            offset_source: Source offset.
            offset_target: Target offset.
            **kwargs: Arguments for ShiftMap.

        Raises:
            ValueError: If scalar is not positive.
        """
        super().__init__(
            offset_source=offset_source,
            offset_target=offset_target,
            source_unit=source_unit,
            target_unit=target_unit,
            **kwargs,
        )
        self._scalar = None
        self.scalar = scalar

    def get_meta(self) -> Meta:
        """Generates metadata for converted timestamp Series/DataFrames.

        Returns:
            A Meta object.
        """
        return Meta(
            map_id=self.id,
            map_type=self.class_name,
            scalar=self._scalar,
            source_unit=self.source_unit,
            target_unit=self.target_unit,
            column_name=self.column_name,
        )

    def _validate_scalar(self, scalar: Number):
        if scalar is None:
            raise ValueError("scalar cannot be None")
        if not isinstance(scalar, Number):
            raise ValueError(f"scalar must be a number, not {type(scalar)}")
        if scalar == 0:
            raise ValueError("scalar must be a non-zero number.")

    @property
    def scalar(self):
        """The scalar value used for conversion."""
        return self._scalar

    @scalar.setter
    def scalar(self, scalar: Number):
        if isinstance(scalar, Coordinate):
            scalar = scalar.value
            if self._target_unit is None:
                self.target_unit = scalar.unit
            if self._target_type is None:
                self.target_type = scalar.number_type
        self._validate_scalar(scalar)
        self._scalar = scalar

    def get_inverse(self) -> Optional["CoordinatesMap"]:
        """Calculates the inverse of this ScalarCoordinatesMap.

        Returns:
            An inverse CoordinatesMap instance.
        """
        cls = self.get_inverse_class()
        scalar = self._scalar
        if cls is None:
            cls = self.__class__
            scalar = 1 / scalar
        offset_source = None if self._offset_target is None else -self._offset_target
        offset_target = None if self._offset_source is None else -self._offset_source
        return cls(
            scalar,
            offset_source=offset_source,
            offset_target=offset_target,
            source_unit=self.target_unit,
            target_unit=self.source_unit,
            target_type=self._source_type,
            column_name=self._make_inverse_column_name(),
            id_prefix="imap",
        )

    def _repr_additional_properties(self):
        result = super()._repr_additional_properties()
        result.append(f"{self._scalar=}")
        return result


class ScalarMultiplicationMap(LinearMap):
    """Converts by multiplying by a scalar, with optional offsets."""

    _default_inverse_class = "ScalarDivisionMap"

    def default_conversion_function(
        self, value: Union[Number, np.ndarray], **kwargs
    ) -> Union[Number, np.ndarray]:
        """Applies source offset, multiplies by scalar, then applies target offset.

        Args:
            value: Input value(s).
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        if self._offset_source is not None:
            value = value + self._offset_source
        result = value * self._scalar
        if self._offset_target is not None:
            result = result + self._offset_target
        return result


class ScalarDivisionMap(LinearMap):
    """Converts by dividing by a scalar, with optional offsets."""

    _default_inverse_class = "ScalarMultiplicationMap"

    def default_conversion_function(
        self, value: Union[Number, np.ndarray], **kwargs
    ) -> Union[Number, np.ndarray]:
        """Applies source offset, divides by scalar, then applies target offset.

        Args:
            value: Input value(s).
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        if self._offset_source is not None:
            value = value + self._offset_source
        result = value / self._scalar
        if self._offset_target is not None:
            result = result + self._offset_target
        return result


class SecondsToMilliseconds(ScalarMultiplicationMap):
    """Converts seconds to milliseconds."""

    _default_source_unit: TimeUnit = TimeUnit.seconds
    _default_target_unit: TimeUnit = TimeUnit.milliseconds
    _default_inverse_class = "MillisecondsToSeconds"
    targets_relative_to_origin: Optional[bool] = False

    def __init__(self, scalar: Number = 1000, **kwargs):
        """Initializes map for seconds to milliseconds.

        Args:
            scalar: Conversion factor (default 1000).
            **kwargs: Additional arguments.
        """
        super().__init__(scalar, **kwargs)


class MillisecondsToSeconds(ScalarDivisionMap):
    """Converts milliseconds to seconds."""

    _default_source_unit: TimeUnit = TimeUnit.milliseconds
    _default_target_unit: TimeUnit = TimeUnit.seconds
    _default_inverse_class = SecondsToMilliseconds
    targets_relative_to_origin: Optional[bool] = False

    def __init__(self, scalar: Number = 1000, **kwargs):
        """Initializes map for milliseconds to seconds.

        Args:
            scalar: Conversion factor (default 1000).
            **kwargs: Additional arguments.
        """
        super().__init__(scalar, **kwargs)


class SecondsToMinutes(ScalarDivisionMap):
    """Converts seconds to milliseconds."""

    _default_source_unit: TimeUnit = TimeUnit.seconds
    _default_target_unit: TimeUnit = TimeUnit.minutes
    _default_inverse_class = "MinutesToSeconds"
    targets_relative_to_origin: Optional[bool] = False

    def __init__(self, scalar: Number = 60, **kwargs):
        """Initializes map for seconds to minutes.

        Args:
            scalar: Conversion factor (default 60).
            **kwargs: Additional arguments.
        """
        super().__init__(scalar, **kwargs)


class MinutesToSeconds(ScalarDivisionMap):
    """Converts seconds to milliseconds."""

    _default_source_unit: TimeUnit = TimeUnit.minutes
    _default_target_unit: TimeUnit = TimeUnit.seconds
    _default_inverse_class = SecondsToMinutes
    targets_relative_to_origin: Optional[bool] = False

    def __init__(self, scalar: Number = 60, **kwargs):
        """Initializes map for minutes to seconds.

        Args:
            scalar: Conversion factor (default 60).
            **kwargs: Additional arguments.
        """
        super().__init__(scalar, **kwargs)


class SamplesToSeconds(ScalarDivisionMap):
    """Converts audio samples to seconds."""

    _default_source_unit: TimeUnit = TimeUnit.samples
    _default_target_unit: TimeUnit = TimeUnit.seconds
    _default_target_type = NumberType.float
    _default_inverse_class = "SecondsToSamples"

    def __init__(self, sample_rate: float, **kwargs):
        """Initializes map for samples to seconds.

        Args:
            sample_rate: The sample rate (samples per second).
            **kwargs: Additional arguments.
        """
        assert "scalar" not in kwargs
        super().__init__(sample_rate, **kwargs)

    @property
    def sample_rate(self):
        """The sample rate used for conversion."""
        return self._scalar


class SecondsToSamples(ScalarMultiplicationMap):
    """Converts seconds to audio samples."""

    _default_source_unit: TimeUnit = TimeUnit.seconds
    _default_target_unit: TimeUnit = TimeUnit.samples
    _default_target_type = NumberType.int
    _default_inverse_class = SamplesToSeconds

    def __init__(self, sample_rate: float, **kwargs):
        """Initializes map for seconds to samples.

        Args:
            sample_rate: The sample rate (samples per second).
            **kwargs: Additional arguments.
        """
        assert "scalar" not in kwargs
        super().__init__(sample_rate, **kwargs)

    @property
    def sample_rate(self):
        """The sample rate used for conversion."""
        return self._scalar


# endregion CoordinatesMap
# region MultiMap


class _CmapsMixin:
    """Can be composed with a class to include a self._cmaps dict
    and methods for managing it. Used in FixedCoordinateTypeObject (and thereby Timeline and Event)
    as well as MultiMap.
    """

    def __init__(self, *args, **kwargs):
        self._cmaps: Dict[
            tuple[TimeUnit, Optional[NumberType]] | TimeUnit, CoordinatesMap
        ] = {}
        super().__init__(*args, **kwargs)

    @property
    def n_maps(self):
        return len(self._cmaps)

    def add_conversion_maps(self, *cmaps: ConversionMap[MT]):
        cmaps = utils.treat_variadic_argument(*cmaps)
        for cmap in cmaps:
            self.validate_cmap(cmap)
            self._cmaps[cmap.id] = self._make_adapted_cmap(cmap)
            self.logger.debug(
                f"Added {cmap.class_name} {cmap.id} to {self.class_name} {self.id}"
            )

    def add_cmaps(self, *cmaps: ConversionMap[MT]):
        """Alias for :meth:`add_conversion_maps`."""
        return self.add_conversion_maps(*cmaps)

    def get_conversion_maps(
        self, target_units: Optional[Iterable[TimeUnit] | TimeUnit] = None
    ) -> list[ConversionMap]:
        """Retrieves :class:`ConversionMap` objects for one or several target types.

        Filters added maps and adds default maps from the global registry.

        Args:
            target_units: The target TimeUnits.

        Returns:
            A CoordinatesMap instance, or None if no suitable map is found and no custom function provided.
        """
        cmaps = {}
        if target_units is not None:
            target_units = utils.make_argument_iterable(target_units)
        for cmap_id, cmap in self._cmaps.items():
            if target_units is None or cmap.target_unit in target_units:
                cmaps[cmap_id] = cmap
        if target_units is not None:
            # add default cmap if defined
            for unit in target_units:
                if (
                    default_cmap := get_cmap(
                        self.unit,
                        unit,
                    )
                ) is not None and default_cmap.id not in cmaps:
                    cmaps[default_cmap.id] = default_cmap
        return list(cmaps.values())

    def get_cmaps(
        self, target_units: Iterable[TimeUnit] | TimeUnit
    ) -> list[ConversionMap]:
        """Alias for :meth:`get_conversion_maps`."""
        return self.get_conversion_maps(target_units=target_units)

    def get_inverse_maps(
        self, source_units: Optional[Iterable[TimeUnit] | TimeUnit] = None
    ) -> list[ConversionMap]:
        """Retrieves inverse :class:`ConversionMap` objects for converting a given source unit to this object's unit.

        Args:
            source_units: The source TimeUnit of external data.

        Returns:
            A CoordinatesMap instance, or None.
        """
        result = []
        for cmap in self.get_conversion_maps(target_units=source_units):
            inverted = cmap.get_inverse()
            result.append(inverted)
        return result

    def iter_cmaps(self):
        yield from self._cmaps.values()

    def validate_cmap(self, cmap: ConversionMap):
        """Stores a CoordinatesMap for this object which will be automatically included in any
        timestamps generated from it.

        Args:
            cmap: The CoordinatesMap to store.

        Raises:
            ValueError: If the cmap is incompatible with this object's unit.
        """
        if not isinstance(cmap, ConversionMap):
            raise ValueError(
                f"Cannot add {cmap.__class__.__name__!r}, expected a ConversionMap."
            )

    def _make_adapted_cmap(self, cmap: CoordinatesMap):
        """This method may create a cmap based on the one to be added. Typically, this could be
        an inverted cmap if the one to be added converts into the "wrong direction" ("correct"
        default: from the object's unit to another one).
        """
        return cmap


class MultiMap(_CmapsMixin, ConversionMap[MT], Generic[MT]):
    """Abstract superclass for all maps that are composed of multiple ConversionMaps."""

    _cmap_category: str = "MultiMap"

    def __init__(
        self,
        cmaps: Optional[Iterable[ConversionMap[MT]] | ConversionMap[MT]] = None,
        target_unit: Optional[str] = None,
        column_name: Optional[str] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            target_unit=target_unit,
            column_name=column_name,
            conversion_function=conversion_function,
            id_prefix=id_prefix,
            uid=uid,
            **kwargs,
        )
        if cmaps is not None:
            self.add_conversion_maps(*utils.make_argument_iterable(cmaps))

    @property
    @abstractmethod
    def target_unit(self) -> tuple[TimeUnit, ...]:
        """Subclasses need a mechanism to decide the target_unit based on their cmaps.
        Note that a setter needs to be implemented because TimeUnit.__init__() uses it.
        """
        raise NotImplementedError

    def get_inverse_class(self) -> Self:
        """Creates an inverse MultiMap by combining the inverse maps."""
        return self.__class__

    def get_inverse(self) -> Self:
        cls = self.get_inverse_class()
        if self.n_maps == 0:
            return cls()  # empty MultiMap
        cmaps = self.get_inverse_maps()
        return cls(
            cmaps, column_name=self._make_inverse_column_name(), id_prefix="imap"
        )

    def default_conversion_function(self, value, kwargs):
        raise NotImplementedError(
            "Combination map doesn't have its own conversion function."
        )

    def _repr_additional_properties(self):
        result = super()._repr_additional_properties()
        result.append(f"n_maps={self.n_maps}")
        return result


# endregion MultiMap
# region ConcatenationMap

# ToDo: MultiScalarCoordinatesMap should be generalized to ConcatenationMap
# Right now it is tailored to the special case TicksToSeconds

CMT = TypeVar("CMT", bound=ConversionMap)


class ConcatenationMap(MultiMap[CMT], Generic[CMT]):
    """
    A ConcatenationMap maps instants to :class:`ConversionMap` objects and converts them accordingly.
    Typically used for creating a cmap for a timeline based on cmaps of its segments, e.g. via a
    :class:`CmapLine`.

    In essence, a ConcatenationMap consists of a non-overlapping IntervalIndex associated with
    cmap IDs. By default, gaps in the IntervalIndex result in missing values and mean that no
    continuous target coordinate system can be computed which is based on a cumulative sum of
    target values. This can be addressed via interpolation.
    ToDo: Add functionality to fill gaps based on specially created interpolation maps.

    General case: Heterogeneous conversion maps
    -------------------------------------------

    This describes the case where different types of ConversionMaps (ScalarMultiplicationMaps,
    ConstantMaps, ChainMaps, etc.) convert to the same target unit. In other words,
    they cannot be combined into a simplified cmap and, instead, need to be applied individually
    for coordinates falling into the respective region(s).

    Since a cmap starting at coordinate c (i.e., which comes from a segment with origin c)
    assumes coordinates to originate at c for conversion, the respective c deltas need to be
    subtracted prior to conversion which is achieved by adding a offset_source_map.
    The converted coordinates then are relative to their respective origins, which is why a
    offset_target_map needs to be added which is computed as a cumulative sum of the
    converted offset_source_map (i.e., segment start coordinates). It is required for this
    computation that the region intervals are non-overlapping and monotonic.

    Special case: ConstantMaps only
    -------------------------------

    No shifts have to be applied for constant maps. If the region index has gaps, the conversion,
    appropriately, has the corresponding gaps which can be filled via a forward-, backward-, or
    value fill.

    Special case: InterpolationMaps only
    ------------------------------------

    If all cmaps are InterpolationMaps, this can be simplified to a single InterpolationMap
    at conversion time.

    """

    @classmethod
    def from_breaks(
        cls, breaks: Iterable[Number], cmaps: Iterable[ConversionMap], **kwargs
    ) -> Self:
        """Creates the intervals for the given cmaps using pd.IntervalIndex.from_breaks().
        This requires n+1 breaks for n cmaps. E.g.: breaks [0,8,15] => [[0,8), [8,15]).
        """
        iix = pd.IntervalIndex.from_breaks(breaks, closed="left")
        series = pd.Series(cmaps, index=iix, dtype=object)
        return cls(series, **kwargs)

    @classmethod
    def from_arrays(
        cls,
        left: Iterable[Number],
        right: Iterable[Number],
        cmaps: Iterable[ConversionMap],
        **kwargs,
    ) -> Self:
        """Creates the intervals for the given cmaps using pd.IntervalIndex.from_arrays().
        left, right, and cmaps need to have the same number of elements.
        """
        iix = pd.IntervalIndex.from_arrays(left, right, closed="left")
        series = pd.Series(cmaps, index=iix, dtype=object)
        return cls(series, **kwargs)

    def __init__(
        self,
        cmaps: (
            pd.Series | dict[pd.Interval | tuple[Coord, Coord], ID_str | ConversionMap]
        ),
        target_unit: Optional[str] = None,
        column_name: Optional[str] = None,
        conversion_function: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
        id_prefix: str = "cmap",
        uid: Optional[str] = None,
        **kwargs,
    ):
        """Initializes a ConcatenationMap.

        Args:
            cmaps:
                A mapping of left-closed, right-open intervals to :class:`ConversionMap` objects
                or IDs. Can be

                    - a Series with a pd.IntervalIndex and ID values which resolve to cmaps;
                    - a dict where the keys are pd.Intervals or pairs of numbers or coordinates and
                      the values are cmaps or cmap IDs.

        """
        if isinstance(cmaps, pd.Series):
            index = treat_intervals_argument(cmaps.index)
            cmaps_dict = treat_cmaps_argument(cmaps.values)
        else:
            index = treat_intervals_argument(cmaps.keys())
            cmaps_dict = treat_cmaps_argument(cmaps.values())
        super().__init__(
            cmaps_dict.values(),
            target_unit=target_unit,
            column_name=column_name,
            conversion_function=conversion_function,
            id_prefix=id_prefix,
            uid=uid,
            **kwargs,
        )
        region_data = [
            dict(
                id=cmap.id,
                class_name=cmap.class_name,
                targets_relative_to_origin=cmap.targets_relative_to_origin,
                cmap_category=cmap._cmap_category,
            )
            for cmap in cmaps_dict.values()
        ]
        self._region_map = pd.DataFrame.from_records(
            region_data, index=index
        ).sort_index()
        assert (
            self._region_map.index.is_non_overlapping_monotonic
        ), "Intervals need to be non-overlapping and monotonically increasing."
        self._offset_source_map = None
        self._offset_target_map = None

    def validate_cmap(self, cmap: MT):
        """Makes sure all added cmaps have the same target time. For this purpose, the first cmap
        added is decisive.
        """
        if self.target_unit is None:
            if cmap.target_unit is not None:
                self.target_unit = cmap.target_unit
        elif cmap.target_unit is not None:
            assert cmap.target_unit == self.target_unit, (
                f"Cannot concatenate {cmap.__class__.__name__} with target type {cmap.target_unit} to "
                f"a {self.class_name} with target type {self._target_unit}."
            )

    def _make_adapted_cmap(self, cmap: CoordinatesMap):
        """This method is called by :meth:`add_conversion_maps` and is responsible for adapting
        time shifts.
        """
        return cmap

    @property
    def offset_source_map(self):
        """Series mapping source coordinate ranges to source offsets."""
        return self._offset_source_map

    @offset_source_map.setter
    def offset_source_map(self, offset_source_map: pd.Series):
        self.validate_input_series(offset_source_map, "offset_source_map", self.length)
        self._offset_source_map = offset_source_map

    @property
    def offset_target_map(self):
        """Series mapping source coordinate ranges to target offsets."""
        return self._offset_target_map

    @offset_target_map.setter
    def offset_target_map(self, offset_target_map: pd.Series):
        # Target offset map's length isn't directly tied to source length like scalar/source_offset maps
        self.validate_input_series(offset_target_map, "offset_target_map")
        self._offset_target_map = offset_target_map

    @property
    def target_unit(self) -> tuple[str | TimeUnit, ...]:
        return self._target_unit

    @target_unit.setter
    def target_unit(self, target_unit: str):
        if self.target_unit is not None and target_unit != self.target_unit:
            raise ValueError(
                f"The target unit of this {self.class_name} has already been set "
                f"to {self._target_unit} and cannot be changed to {target_unit}."
            )
        self._target_unit = target_unit

    def _convert_selection_with_single_cmap(
        self, result: pd.Series, cmap: ConversionMap, selection_mask: pd.Series
    ):
        result.loc[selection_mask] = cmap(result[selection_mask])

    def _convert_with_heterogeneous_cmaps(
        self,
        result=pd.Series,
        left_unbounded: bool = False,
        right_unbounded: bool = True,
    ):
        """
        Iterates over concatenated maps and applies each individually to those coordinates that
        fall into its interval.
        """
        for cmap_id, group in self.get_region_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        ).groupby("id"):
            cmap = self._cmaps[cmap_id]
            selection_mask = utils.get_boolean_mask_for_intervals(
                result.index, group.index
            )
            self._convert_selection_with_single_cmap(result, cmap, selection_mask)
        return result

    def default_conversion_function(
        self,
        value: Union[Number, np.ndarray],
        left_unbounded: bool = False,
        right_unbounded: bool = False,
        **kwargs,
    ) -> Union[Number, np.ndarray]:
        """Applies interval-based offsets and scalar multiplication.

        Args:
            value: Input value(s).
            left_unbounded: If True, first interval of maps is left-unbounded.
            right_unbounded: If True, last interval of maps is right-unbounded.
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        self.logger.debug(
            f"{self.class_name}.default_conversion_function({left_unbounded=}, {right_unbounded=}, "
            f"{kwargs=})"
        )
        if not self.n_maps:
            raise ValueError(f"No maps have been added to this {self.class_name}.")
        region_map = self.get_region_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        # osm = self.get_offset_source_map(
        #     left_unbounded=left_unbounded,
        #     right_unbounded=right_unbounded
        # )
        # if (osm != 0).any():
        #     offset_source = get_values_from_interval_map(osm, value)
        #     result += offset_source
        cmap_types = region_map.cmap_category.value_counts(dropna=False)
        if len(cmap_types) == 1:
            uniform_type = cmap_types.index[0]
            if uniform_type == "ConstantMap":
                return self._convert_with_constant_maps(
                    value,
                    left_unbounded=left_unbounded,
                    right_unbounded=right_unbounded,
                )
            elif uniform_type == "ShiftMap":
                return self._convert_with_shift_maps(
                    value,
                    left_unbounded=left_unbounded,
                    right_unbounded=right_unbounded,
                )
            elif uniform_type == "LinearMap":
                return self._convert_with_linear_maps(
                    value,
                    left_unbounded=left_unbounded,
                    right_unbounded=right_unbounded,
                )
            else:
                raise NotImplementedError(
                    f"Don't know how to concatenate {uniform_type}s :(("
                )
        else:
            self._convert_with_heterogeneous_cmaps(
                value, left_unbounded=left_unbounded, right_unbounded=right_unbounded
            )

    def _convert_with_linear_maps(
        self,
        result: pd.Series,
        left_unbounded: bool = False,
        right_unbounded: bool = False,
    ):
        cmap2scalar = {}
        for cmap in self.iter_cmaps():
            if isinstance(cmap, ScalarMultiplicationMap):
                cmap2scalar[cmap.id] = cmap.scalar
            elif isinstance(cmap, ScalarDivisionMap):
                cmap2scalar[cmap.id] = 1 / cmap.scalar
        scalar_map = self._region_map["id"].map(cmap2scalar)
        if left_unbounded or right_unbounded:
            fill_value = "extrapolate"
            if not left_unbounded or not right_unbounded:
                warnings.warn(
                    "For InterpolationMaps, extrapolation is always allowed for left and right."
                )
        else:
            fill_value = np.nan
        imap = InterpolationMap.from_scalar_map(scalar_map, fill_value=fill_value)
        return imap(result)

    def _convert_with_shift_maps(
        self,
        result: pd.Series,
        left_unbounded: bool = False,
        right_unbounded: bool = False,
    ):
        source_offsets = {
            cmap.id: 0 if not cmap.offset_source else cmap.offset_source
            for cmap in self.iter_cmaps()
        }
        target_offsets = {
            cmap.id: 0 if not cmap.offset_target else cmap.offset_target
            for cmap in self.iter_cmaps()
        }
        region_map = self.get_region_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        source_shifts = region_map["id"].map(source_offsets)
        target_shifts = region_map["id"].map(target_offsets)
        return (
            result
            + get_values_from_interval_map(source_shifts, result)
            + get_values_from_interval_map(target_shifts, result)
        )

    def _convert_with_constant_maps(
        self,
        result: pd.Series,
        left_unbounded: bool = False,
        right_unbounded: bool = False,
    ):
        constants = {cmap.id: cmap.constant for cmap in self.iter_cmaps()}
        region_map = self.get_region_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        constant_map = region_map["id"].map(constants)
        return get_values_from_interval_map(constant_map, result)

    # def get_inverse(self) -> Self:
    #     """Cannot currently compute inverse for ConcatenationMaps."""
    #     raise NotImplementedError(
    #         "Cannot currently compute inverse for ConcatenationMaps."
    #     )

    def get_offset_source_map(
        self, left_unbounded: bool = False, right_unbounded: bool = True
    ) -> Optional[pd.Series]:
        """Retrieves the source offset map, optionally with unbounded intervals.

        Args:
            left_unbounded: If True, makes the first interval left-unbounded.
            right_unbounded: If True, makes the last interval right-unbounded.

        Returns:
            The source offset map Series, or None.
        """
        if self._offset_source_map is not None:
            raise NotImplementedError(
                "Cannot currently combin the default shifts with a given one."
            )
        if len(self._region_map) == 0:
            return pd.Series([], index=pd.IntervalIndex([]))
        region_intervals = self._region_map.index
        region_starts = pd.Series(region_intervals.left, index=region_intervals)
        region_starts = region_starts.where(
            self._region_map.targets_relative_to_origin, 0
        )
        shifts = pd.Series(-region_starts.cumsum(), index=region_intervals)
        if not (right_unbounded or left_unbounded):
            return shifts
        return utils.replace_interval_index_with_unbounded_one(
            shifts, left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )

    def get_offset_target_map(
        self, left_unbounded: bool = False, right_unbounded: bool = True
    ) -> Optional[pd.Series]:
        """Retrieves the target offset map, optionally with unbounded intervals.

        Args:
            left_unbounded: If True, makes the first interval left-unbounded.
            right_unbounded: If True, makes the last interval right-unbounded.

        Returns:
            The target offset map Series, or None.
        """
        otm = self._offset_target_map
        if otm is None or not (right_unbounded or left_unbounded):
            return otm
        return utils.replace_interval_index_with_unbounded_one(
            otm, left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )

    @cache
    def get_region_map(
        self, left_unbounded: bool = False, right_unbounded: bool = False
    ) -> Optional[pd.Series]:
        """Retrieves the region map mapping intervals to converison maps,
        optionally with unbounded intervals to convert any value, even out of bounds.

        Args:
            left_unbounded: If True, makes the first interval left-unbounded.
            right_unbounded: If True, makes the last interval right-unbounded.

        Returns:
            The target offset map Series, or None.
        """
        region_map = self._region_map
        if region_map is None or not (right_unbounded or left_unbounded):
            return region_map
        return utils.replace_interval_index_with_unbounded_one(
            region_map, left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )

    def validate_input_series(
        self, s_map: pd.Series, arg_name: str, target_length: Optional[Number] = None
    ):
        """Validates an input Series for use in this map.

        Args:
            s_map: The Series to validate.
            arg_name: Name of the argument for error messages.
            target_length: Expected maximum right boundary of the IntervalIndex.

        Raises:
            ValueError: If Series is empty.
            AssertionError: If index is not IntervalIndex, not non-overlapping/monotonic, or length mismatches.
        """
        if s_map.size == 0:
            raise ValueError(f"{arg_name} cannot be empty")
        assert isinstance(
            s_map.index, pd.IntervalIndex
        ), f"The index of a {arg_name} needs to be an IntervalIndex."
        assert s_map.index.is_non_overlapping_monotonic, (
            f"The IntervalIndex of a {arg_name} needs to be "
            f"non-overlapping and monotonic."
        )
        if target_length is not None:
            this_length = s_map.index.right.max()
            assert this_length == target_length, (
                f"The index of the {arg_name} has length {this_length} "
                f"{self.source_unit} but should have {target_length}, "
                f"like the scalar_map."
            )


class MultiScalarCoordinatesMap(RegionMap, CoordinatesMap):
    """Converts using different scalars for different coordinate regions.

    The conversion is defined by a pandas Series with an IntervalIndex mapping
    coordinate ranges (in source units) to scalar values.
    """

    _default_target_type = NumberType.float

    def __init__(
        self,
        scalar_map: pd.Series,
        offset_source_map: Optional[pd.Series] = None,
        offset_target_map: Optional[pd.Series] = None,
        **kwargs,
    ):
        """Initializes a MultiScalarCoordinatesMap.

        Args:
            scalar_map: Series with IntervalIndex mapping source ranges to scalars.
            offset_source_map: Optional Series mapping source ranges to source offsets.
            offset_target_map: Optional Series mapping source ranges to target offsets.
            **kwargs: Arguments for CoordinatesMap.
        """
        super().__init__(
            region_map=scalar_map,
            offset_source_map=offset_source_map,
            offset_target_map=offset_target_map,
            **kwargs,
        )

    @property
    def scalar_map(self):
        """Series with IntervalIndex mapping source ranges to scalar values."""
        return self._region_map

    @scalar_map.setter
    def scalar_map(self, scalar_map: pd.Series):
        self.validate_input_series(scalar_map, "scalar_map")
        self._region_map = scalar_map
        self.length = scalar_map.index.right.max()

    def get_inverse(self) -> Optional["CoordinatesMap"]:
        """Calculates the inverse of this MultiScalarCoordinatesMap.

        Returns:
            An inverse MultiScalarCoordinatesMap instance.
        """
        cls = self.get_inverse_class()
        scalar_map_values = self._region_map.values
        if cls is None:
            cls = self.__class__
            scalar_map_values = 1 / scalar_map_values
        left_values = self._region_map.index.left
        right_values = self._region_map.index.right.values
        converted_lefts = self.convert_array(left_values)
        converted_rights = self.convert(right_values, right_unbounded=True)
        converted_index = pd.IntervalIndex.from_arrays(
            converted_lefts, converted_rights, closed="left"
        )
        inverse_map = pd.Series(scalar_map_values, index=converted_index)
        if self._offset_source_map is None:
            offset_target_map = None
        else:
            offset_target_map = pd.Series(
                -self._offset_source_map.values, index=converted_index
            )
        if self._offset_target_map is None:
            offset_source_map = None
        else:
            offset_source_map = pd.Series(
                -self._offset_target_map.values, index=converted_index
            )
        return cls(
            inverse_map,
            offset_source_map=offset_source_map,
            offset_target_map=offset_target_map,
            source_unit=self.target_unit,
            target_unit=self.source_unit,
            target_type=self.source_type,
            column_name=self._make_inverse_column_name(),
            id_prefix="imap",
        )


def get_values_from_interval_map(
    intv_map: pd.Series, values: Union[Number, np.ndarray]
) -> Union[Number, np.ndarray]:
    """Retrieves values from an interval-indexed Series corresponding to input values.

    Args:
        intv_map: The interval-indexed Series.
        values: A scalar or array of values to look up.

    Returns:
        Corresponding scalar or array of values from the intv_map.
    """
    result = intv_map.loc[values]
    return result if is_scalar(result) else result.values


class MultiScalarMultiplicationMap(MultiScalarCoordinatesMap):
    """MultiScalarCoordinatesMap that multiplies by scalars."""

    _default_inverse_class = "MultiScalarDivisionMap"

    def default_conversion_function(
        self,
        value: Union[Number, np.ndarray],
        left_unbounded: bool = False,
        right_unbounded: bool = True,
        **kwargs,
    ) -> Union[Number, np.ndarray]:
        """Applies interval-based offsets and scalar multiplication.

        Args:
            value: Input value(s).
            left_unbounded: If True, first interval of maps is left-unbounded.
            right_unbounded: If True, last interval of maps is right-unbounded.
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        self.logger.debug(
            f"{self.class_name}.default_conversion_function({left_unbounded=}, {right_unbounded=}, "
            f"{kwargs=})"
        )
        converted_value = value
        osm = self.get_offset_source_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        if osm is not None:
            offset_source = get_values_from_interval_map(osm, value)
            converted_value = converted_value + offset_source
        sc = self.get_region_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        scalars = get_values_from_interval_map(sc, value)
        converted_value = converted_value * scalars
        otm = self.get_offset_target_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        if otm is not None:
            offset_target = get_values_from_interval_map(otm, value)
            converted_value = converted_value + offset_target
        if self.target_type == NumberType.int:
            converted_value = np.round(converted_value)
        return converted_value


class MultiScalarDivisionMap(MultiScalarCoordinatesMap):
    """MultiScalarCoordinatesMap that divides by scalars."""

    _default_inverse_class = "MultiScalarMultiplicationMap"

    def default_conversion_function(
        self,
        value: Union[Number, np.ndarray],
        left_unbounded: bool = False,
        right_unbounded: bool = True,
        **kwargs,
    ) -> Union[Number, np.ndarray]:
        """Applies interval-based offsets and scalar division.

        Args:
            value: Input value(s).
            left_unbounded: If True, first interval of maps is left-unbounded.
            right_unbounded: If True, last interval of maps is right-unbounded.
            **kwargs: Not used.

        Returns:
            Converted value(s).
        """
        converted_value = value

        osm = self.get_offset_source_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        if osm is not None:
            offset_source = get_values_from_interval_map(osm, value)
            converted_value = converted_value + offset_source
        sc = self.get_region_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        scalars = get_values_from_interval_map(sc, value)
        converted_value = converted_value / scalars
        otm = self.get_offset_target_map(
            left_unbounded=left_unbounded, right_unbounded=right_unbounded
        )
        if otm is not None:
            offset_target = get_values_from_interval_map(otm, value)
            converted_value = converted_value + offset_target
        if self.target_type == NumberType.int:
            converted_value = np.round(converted_value)
        return converted_value


class TicksToSeconds(MultiScalarMultiplicationMap):
    """Converts musical ticks to seconds using a tempo map."""

    _default_source_unit: TimeUnit = TimeUnit.ticks
    _default_target_unit: TimeUnit = TimeUnit.seconds
    _default_target_type = NumberType.float
    _default_inverse_class = "SecondsToTicks"

    def __init__(
        self,
        seconds_per_tick_map: pd.Series,
        offset_source_map: Optional[pd.Series] = None,
        offset_target_map: Optional[pd.Series] = None,
        **kwargs,
    ):
        """Initializes TicksToSeconds map.

        Args:
            seconds_per_tick_map: Series mapping tick intervals to seconds-per-tick scalars.
            offset_source_map: Optional source offset map.
            offset_target_map: Optional target offset map.
            **kwargs: Additional arguments.
        """
        super().__init__(
            scalar_map=seconds_per_tick_map,
            offset_source_map=offset_source_map,
            offset_target_map=offset_target_map,
            **kwargs,
        )


class SecondsToTicks(MultiScalarDivisionMap):
    """Converts seconds to musical ticks using a tempo map."""

    _default_source_unit: TimeUnit = TimeUnit.seconds
    _default_target_unit: TimeUnit = TimeUnit.ticks
    _default_target_type = NumberType.int
    _default_inverse_class = TicksToSeconds

    def __init__(
        self,
        seconds_per_tick_map: pd.Series,  # This map is still seconds_per_tick for division
        offset_source_map: Optional[pd.Series] = None,
        offset_target_map: Optional[pd.Series] = None,
        **kwargs,
    ):
        """Initializes SecondsToTicks map.

        Args:
            seconds_per_tick_map: Series mapping second intervals to seconds-per-tick scalars (for division).
            offset_source_map: Optional source offset map.
            offset_target_map: Optional target offset map.
            **kwargs: Additional arguments.
        """
        super().__init__(
            scalar_map=seconds_per_tick_map,
            offset_source_map=offset_source_map,
            offset_target_map=offset_target_map,
            **kwargs,
        )


def seconds_per_tick_scalar_map_from_midi_tempos(
    tempo_change_ticks: pd.Series,
    midi_tempos: pd.Series,
    right_boundary: int,
    ticks_per_quarter: int,
) -> pd.Series:
    """Creates a scalar map (seconds per tick) from MIDI tempo changes.

    Args:
        tempo_change_ticks: Series of tick instants where tempo changes occur.
        midi_tempos: Series of MIDI tempo values (microseconds per quarter note) at those instants.
        right_boundary: The final tick instant to define the last interval.
        ticks_per_quarter: The number of ticks per quarter note for the MIDI file.

    Returns:
        A pandas Series with an IntervalIndex (in ticks) mapping to seconds-per-tick values.
    """
    change_instants_shifted = tempo_change_ticks.shift(
        -1, fill_value=right_boundary
    ).astype(int)
    iix = pd.IntervalIndex.from_arrays(
        tempo_change_ticks, change_instants_shifted, closed="left"
    )
    micro_s_per_quarter = DS(midi_tempos, index=iix)
    micro_s_per_tick = micro_s_per_quarter / ticks_per_quarter
    scalar_map = (micro_s_per_tick / 1000000).rename("seconds_per_tick")
    return scalar_map


def seconds_per_tick_scalar_map_from_midi_df(midi_df: pd.DataFrame) -> pd.Series:
    """Extracts tempo information from a MIDI DataFrame to create a seconds-per-tick scalar map.

    Args:
        midi_df: DataFrame created from a MIDI file (e.g., by `midi_to_df`).

    Returns:
        A pandas Series with an IntervalIndex (in ticks) mapping to seconds-per-tick values.
    """
    ends = midi_df.absolute_time.where(
        midi_df.duration.isna(), midi_df.absolute_time + midi_df.duration
    )
    right_boundary = ends.max()
    tempo_changes = midi_df[midi_df.type == "set_tempo"]
    ticks_per_quarter = midi_df.get_meta("ticks_per_beat")
    tempo_change_instants = tempo_changes.absolute_time
    midi_tempos = tempo_changes.tempo.rename("micro_s_per_quarter")
    scalar_map = seconds_per_tick_scalar_map_from_midi_tempos(
        tempo_change_instants, midi_tempos, right_boundary, ticks_per_quarter
    )
    return scalar_map


def make_ticks2seconds_map(scalar_map: pd.Series) -> TicksToSeconds:
    """Creates a TicksToSeconds map with appropriate offsets from a seconds-per-tick scalar map.

    This function calculates cumulative target offsets (in seconds) based on the duration
    of each tick-based interval when converted to seconds. It also sets source offsets
    to align the start of each tick interval to zero for the scalar multiplication.

    Args:
        scalar_map: A Series with IntervalIndex (in ticks) mapping to seconds-per-tick values.

    Returns:
        A TicksToSeconds map instance.
    """
    Result = TicksToSeconds(scalar_map)
    tempo_segments_ticks = scalar_map.index.length
    tempo_segments_seconds = scalar_map * tempo_segments_ticks
    segment_durations_cumulative = tempo_segments_seconds.cumsum()
    Result.offset_target_map = segment_durations_cumulative.shift(fill_value=0)
    segment_start_ticks = scalar_map.index.left
    Result.offset_source_map = pd.Series(-segment_start_ticks, index=scalar_map.index)
    return Result


def ticks2seconds_map_from_midi_df(midi_df: pd.DataFrame) -> TicksToSeconds:
    """Creates a TicksToSeconds map directly from a MIDI DataFrame.

    Args:
        midi_df: DataFrame created from a MIDI file.

    Returns:
        A TicksToSeconds map instance.
    """
    scalar_map = seconds_per_tick_scalar_map_from_midi_df(midi_df)
    return make_ticks2seconds_map(scalar_map)


# endregion ConcatenationMap
# region CombinationMap


class CombinationMap(MultiMap):
    """Stores one or more :class:`SegmentMap` objects allowing to perform
    multiple conversions at once using a single object/id."""

    @property
    def source_unit(self) -> Optional[TimeUnit]:
        if not self.n_maps:
            return None
        units = set(
            su for cmap in self.iter_cmaps() if (su := cmap.source_unit) is not None
        )
        if len(units) > 1:
            raise ValueError(
                f"The maps include more than one source units which is not possible: {units}"
            )
        return units.pop() if units else None

    @property
    def target_unit(self) -> tuple[TimeUnit, ...]:
        if self._target_unit is None:
            return tuple(cmap.target_unit for cmap in self.iter_cmaps())
        return self._target_unit

    @target_unit.setter
    def target_unit(self, target_unit: tuple[str, ...]):
        if target_unit is None:
            self._target_unit = None
            return
        assert (
            len(target_unit) == self.n_maps
        ), f"Cannot set {len(target_unit)} units for {self.n_maps} combined maps."
        # ToDo: more sophisticated mechanism for combining combined maps also
        self._target_unit = target_unit

    def validate_cmap(self, cmap):
        su = self.source_unit
        if (
            su is not None and cmap.source_unit is not None and cmap.source_unit != su
        ):  # computed based on all
            # current cmaps
            raise ValueError(
                f"Cannot combine {cmap.__class__.__name__} with source unit {cmap.source_unit!r} with "
                f"a {self.class_name} with source unit {self.source_unit!r}."
            )

    def convert_number(self, number: Number, *args, **kwargs) -> tuple[Number, ...]:
        return tuple(
            cmap.convert(number, *args, **kwargs) for cmap in self.iter_cmaps()
        )

    def convert_array(self, data: np.ndarray, *args, **kwargs) -> np.ndarray:
        fields = np.dtype(
            [field for cmap in self.iter_cmaps() for field in cmap.target_fields]
        )
        conversions = [
            cmap._convert_array(data, *args, **kwargs) for cmap in self.iter_cmaps()
        ]
        # return np.column_stack(conversions)
        structured_array = np.array(list(zip(*conversions)), dtype=fields)
        return structured_array

    def convert_series(self, data: pd.Series, **kwargs) -> DF:
        """Converts a pandas Series.

        Args:
            data: The pandas Series to convert.
            name: Optional name for the resulting Series.
            as_dataframe: If True, returns a DataFrame. If a dict, adds columns from dict.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            A converted DataFrame.
        """
        meta = self.get_meta()
        if data.size == 0:
            return DF([], meta=meta)
        converted = [cmap.convert_series(data, **kwargs) for cmap in self.iter_cmaps()]
        if len(converted) == 1:
            return DF(converted[0].to_frame(), meta=meta)
        return pd_concat(converted, axis=1, meta=meta)

    def convert_index(self, data: pd.Index, **kwargs) -> pd.MultiIndex:
        """Converts a pandas Index.

        Args:
            data: The pandas Series to convert.
            **kwargs: Additional arguments for the conversion function.

        Returns:
            A converted MultiIndex, i.e., an index with multiple levels.
        """
        if data.size == 0:
            return pd.MultiIndex([])
        converted = self.convert_series(data)
        return pd.MultiIndex.from_frame(converted)

    def get_meta(self) -> Meta:
        """Generates metadata for converted timestamp Series/DataFrames.

        Returns:
            A Meta object.
        """
        return Meta(
            map_id=self.id,
            map_type=self.class_name,
            combined_maps=[cmap_id for cmap_id in self._cmaps.keys()],
            source_unit=self.source_unit,
            target_unit=self.target_unit,
            column_name=self.column_name,
        )


def _resolve_number_or_tuple(
    x: tuple[Coordinate | Number] | Coordinate | Number,
) -> tuple[Number] | Number:
    if isinstance(x, Number):
        return x
    if isinstance(x, Coordinate):
        return x.value
    if len(x) != 2:
        raise ValueError(
            f"Expected either a number or a pair thereof, "
            f"got a {type(x)} of length ({len(x)})"
        )
    x0, x1 = x
    x0, x1 = get_coordinate_value(x0), get_coordinate_value(x1)
    if x0 == x1:
        return x0
    return x0, x1


class StraightLineMap(CombinationMap):
    """This :class:`CombinationMap` is used to convert a graphical axis to (x, y) coordinates in
    a raster graphic.
    """

    @classmethod
    def from_coordinates(
        cls,
        x: tuple[Coordinate | Number, Coordinate | Number] | Coordinate | Number,
        y: tuple[Coordinate | Number, Coordinate | Number] | Coordinate | Number,
        **kwargs,
    ):
        """Creates a mapping from a DiscreteGraphicalTimeline to (x,y) coordinates.
        As of now, this needs to be either horizontal (single y-value with (x0, x1) pair)
        or vertical (single x-value with (y0, y1) pair). The order in which x0, x1
        (or y0, y1) are given determines the line's orientation:

            * x0 < x1: horizontal left to right
            * x0 > x1: horizontal right to left
            * y0 < y1: vertical top-down
            * y1 > y0: vertical bottom-up

        This implies that the origin (x, y) = (0, 0) is understood to be the upper left corner.
        """
        x = _resolve_number_or_tuple(x)
        y = _resolve_number_or_tuple(y)
        is_tuple = [isinstance(x, tuple), isinstance(y, tuple)]
        if all(is_tuple):
            raise NotImplementedError("As of now, only one of x, y can be a pair.")
        if not any(is_tuple):
            raise ValueError("Exactly one of x, y needs to be a pair.")
        if is_tuple[0]:
            orientation = "horizontal"
            start, end = x
            const = y
        else:
            orientation = "vertical"
            start, end = y
            const = x
        scalar = np.sign(end - start)

        SLM = cls(**kwargs)
        x_col, y_col = "x", "y"
        sc_col, cnst_col = (
            (x_col, y_col) if orientation == "horizontal" else (y_col, x_col)
        )
        scalar_map = ScalarMultiplicationMap(
            scalar=scalar,
            offset_source=start,
            source_unit=TimeUnit.px,
            target_unit=TimeUnit.px,
            column_name=sc_col,
        )
        constant_map = ConstantMap(
            constant=const,
            source_unit=TimeUnit.px,
            target_unit=TimeUnit.px,
            column_name=cnst_col,
        )
        if orientation == "horizontal":
            SLM.add_conversion_maps(scalar_map, constant_map)
        else:
            SLM.add_conversion_maps(constant_map, scalar_map)
        return SLM


# endregion CombinationMap
# region FixedCoordinateTypeObject


class FixedCoordinateTypeObject(_CmapsMixin, RegisteredObject[D]):
    """This object serves as base class for :class:`Timeline` and `Event`, both of which are bound
    to single coordinate type. A FixedCoordinateTypeObject is a :class:`RegisteredObject` that
    is instantiated with a :class:`TimeUnit` and a :class:`NumberType`. Usually, subclasses
    would lock the properties :attr:`unit` and :attr:`coordinate_type` once data has been added
    and/or refer to some conversion mechanism.
    """

    _allowed_units: Optional[tuple[TimeUnit, ...]] = None
    _allowed_number_types: Optional[tuple[NumberType | Type[Number], ...]] = None
    _default_unit: Optional[TimeUnit] = None
    _default_number_type: Optional[NumberType] = None

    def __init__(
        self,
        unit: TimeUnit | str,
        number_type: NumberType | Type[Number],
        id_prefix: str,
        uid: Optional[str] = None,
    ):
        """Initializes a FixedCoordinateTypeObject.

        Args:
            unit: The TimeUnit for this object.
            number_type: The NumberType or Python numeric type for this object.
            id_prefix: Prefix for the object's ID.
            uid: Unique identifier.
        """
        super().__init__(id_prefix=id_prefix, uid=uid)
        self._unit = None
        self._number_type = None
        self._inverse_maps: Dict[
            tuple[TimeUnit, Optional[NumberType]] | TimeUnit, CoordinatesMap
        ] = {}
        self.unit = unit
        self.number_type = number_type

    @property
    def coordinate_type(self) -> str:
        """String key for this object's coordinate type."""
        return get_key(self.unit, self.number_type)

    @property
    def number_type(self) -> NumberType:
        """The NumberType of this object."""
        return self._number_type

    @number_type.setter
    def number_type(self, value: NumberType | Type[Number]):  # Allow Type[Number]
        if value is None:
            if self._default_number_type is None:
                raise ValueError(
                    f"number_type cannot be None when {self.class_name}._default_number_type is None."
                )
            self._number_type = NumberType(self._default_number_type)
            return
        if isinstance(value, NumberType):
            value = value.value
        if self._allowed_number_types is None:
            allowed = Number
        else:
            if isinstance(self._allowed_number_types, Iterable):
                allowed = self._allowed_number_types
            else:
                allowed = [self._allowed_number_types]
            allowed = tuple(
                t.value if isinstance(t, NumberType) else t for t in allowed
            )
        if not issubclass(value, allowed):
            try:
                value_name = value.__name__
            except Exception:
                value_name = value
            raise ValueError(
                f"number_type needs to be a subclass of {allowed}, not {value_name}"
            )
        self._number_type = NumberType(value)

    @property
    def interval(self):
        raise NotImplementedError(
            f"Property 'interval' not defined for {self.class_name}"
        )

    @property
    def pd_interval(self) -> pd.Interval:
        left, right = self.interval
        return pd.Interval(left, right, closed="left")

    @property
    def unit(self) -> TimeUnit:
        """The TimeUnit of this object."""
        return self._unit

    @unit.setter
    def unit(self, value: TimeUnit | str):
        if value is None:
            if self._default_unit is None:
                raise ValueError(
                    f"unit cannot be None when {self.class_name}._default_unit is None."
                )
            self._unit = TimeUnit(self._default_unit)
            return

        new_value = TimeUnit(value)
        if self._allowed_units is not None:
            if new_value not in self._allowed_units:
                allowed_names = [u.name for u in self._allowed_units]
                raise TypeError(
                    f"The unit of a {self.class_name} cannot be {new_value.name!r}. Valid units are: "
                    f"{allowed_names}."
                )
        self._unit = new_value

    def validate_cmap(self, cmap: ConversionMap):
        """Checks whether the cmap to be added converts from or to this object's unit.

        Args:
            cmap: The CoordinatesMap to store.

        Raises:
            ValueError: If the cmap is incompatible with this object's unit.
        """
        if (
            cmap.source_unit is not None
            and cmap.source_unit != self.unit
            and cmap.target_unit != self.unit
        ):
            raise ValueError(
                f"ConversionMap from {cmap.source_unit.name} to {cmap.target_unit.name} "
                f"is incompatible with this {self.unit.name}-based object {self.id}."
            )

    def _make_adapted_cmap(self, cmap: CoordinatesMap):
        """This method may create a cmap based on the one to be added. Typically, this could be
        an inverted cmap if the one to be added converts into the "wrong direction" ("correct"
        default: from the object's unit to another one).
        """
        if cmap.source_unit is None or cmap.source_unit == self.unit:
            return cmap
        inverted = cmap.get_inverse()
        assert inverted.source_unit == self.unit, (
            f"Inversion of {cmap.class_name} resulted in a {inverted.class_name} "
            f"with source_unit {inverted.source_unit}, not {self.unit}."
        )
        self.logger.debug(
            f"{cmap.class_name} had to be inverted before adding it to {self.class_name}"
            f" {self.id} such that the source unit matches."
        )
        return inverted

    def convert_to(
        self,
        values: pd.Series | np.ndarray | Sequence[Coord] | Coord,
        target_unit: TimeUnit,
        target_type: Optional[NumberType] = None,
        custom_converter_func: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
    ) -> Any:
        """Converts values from this object's coordinate type to a target type.

        Args:
            values: Data to convert.
            target_unit: Target TimeUnit.
            target_type: Optional target NumberType.
            custom_converter_func: Optional custom conversion function.

        Returns:
            Converted data.

        Raises:
            ValueError: If conversion is not possible.
        """
        if values is None:
            raise ValueError("Cannot convert None.")
        cmaps = self.get_conversion_maps(target_unit)
        if cmaps:
            if custom_converter_func is not None:
                warnings.warn(
                    "Existing cmaps were found, custom converter function ignored."
                )
            if len(cmaps) == 1:
                return cmaps[0].convert(values)
            combined = CombinationMap(cmaps)
            return combined.convert(values)
        if custom_converter_func is None:
            raise ValueError(
                f"Cannot convert {self.unit} to {target_unit} because no CoordinatesMap is known and no custom "
                f"converter function has been specified."
            )
        new_cmap = CoordinatesMap(
            source_unit=self.unit,
            target_unit=target_unit,
            target_type=target_type,
            conversion_function=custom_converter_func,
        )
        return new_cmap(values)

    def convert_from(
        self,
        values: pd.Series | np.ndarray | Sequence[Coord] | Coord,
        source_unit: TimeUnit,
        custom_converter_func: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
    ) -> Any:
        """Converts values from an external source type to this object's coordinate type.

        Args:
            values: Data to convert.
            source_unit: TimeUnit of the source data.
            source_type: Optional NumberType of the source data.
            custom_converter_func: Optional custom conversion function.

        Returns:
            Converted data.

        Raises:
            ValueError: If conversion is not possible.
        """
        if values is None:
            raise ValueError("Cannot convert None.")
        cmaps = self.get_inverse_maps(source_unit)
        if cmaps:
            if len(cmaps) == 1:
                return cmaps[0].convert(values)
            combined = CombinationMap(cmaps)
            return combined.convert(values)
        if custom_converter_func is None:
            raise ValueError(
                f"Cannot convert {self.unit} to {source_unit} because no CoordinatesMap is known and no custom "
                f"converter function has been specified."
            )
        new_cmap = CoordinatesMap(
            source_unit=source_unit,
            target_unit=self.unit,
            target_type=self.number_type,
            conversion_function=custom_converter_func,
        )
        return new_cmap(values)

    def make_coordinate(self, value: Coord) -> Coordinate:
        """Creates a Coordinate with this object's unit and number type.

        Args:
            value: The numerical value or an existing Coordinate.

        Returns:
            A new Coordinate object.
        """
        return convert_coordinate(value, self.coordinate_type)

    def make_number(self, value: Number) -> Number:
        """Converts a number to this object's number type.

        Args:
            value: The number to convert.

        Returns:
            The number, cast to this object's NumberType.
        """
        return self.number_type.value(value)


# endregion FixedCoordinateTypeObject
# region helper functions


def treat_cmaps_argument(
    cmaps: Iterable[ConversionMap | str] | ConversionMap | str,
) -> dict[ID_str, ConversionMap]:
    cmaps = make_argument_iterable(cmaps)
    result = {}
    for cmap_arg in cmaps:
        if arg_was_id := isinstance(cmap_arg, str):
            cmap = get_object_by_id(cmap_arg)
        else:
            cmap = cmap_arg
        if not isinstance(cmap, ConversionMap):
            if arg_was_id:
                raise ValueError(
                    f"The ID {cmap_arg} resolved to a {cmap.__class__.__name__}, "
                    f"not a ConversionMap."
                )
            else:
                raise ValueError(f"Expected a ConversionMap, got a {type(cmap_arg)}.")
        result[cmap.id] = cmap
    return result


# endregion helper functions
