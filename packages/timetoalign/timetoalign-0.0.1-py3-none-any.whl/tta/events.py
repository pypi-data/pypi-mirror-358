from __future__ import annotations

import warnings
from collections import defaultdict
from functools import cache, partial
from numbers import Number
from pathlib import Path
from pprint import pformat
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Optional,
    Protocol,
    Self,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    overload,
)

import librosa
import numpy as np
import pandas as pd
from partitura import performance as ptp
from partitura import score as pts
from partitura.utils.generic import interp1d as pt_interpolator
from scipy.interpolate import interp1d as sp_interpolator

from processing.metaframes import DF, Meta
from processing.tta import utils
from processing.tta.common import RegisteredObject
from processing.tta.conversions import (
    ConversionMap,
    Coordinate,
    FixedCoordinateTypeObject,
    RegionMap,
    SamplesToSeconds,
    make_coordinate,
    ticks2seconds_map_from_midi_df,
)
from processing.tta.parsing import (
    event_df_from_part_list,
    get_divs_per_quarter,
    get_event_dict,
    get_performed_notes,
    load_json_file,
    midi_to_df,
    parse_tilia_json,
)
from processing.tta.registry import (
    flyweight,
    get_class,
    get_registry_by_prefix,
    iter_objects_by_ids,
)
from processing.tta.utils import Missing, NumberType, PartMap, TimeUnit

if TYPE_CHECKING:
    from processing.tta.timelines import Timeline

ST = TypeVar("ST")  # type of silo data
ET = TypeVar("ET")  # type of event data
Interpolator: TypeAlias = Union[pt_interpolator, sp_interpolator]

# region Event types


def get_event_properties(
    ids: str | Iterable[str],
    include_shared=False,
    include_individual=False,
    exclude_properties: Optional[tuple[str]] = ("data",),
    skip_missing=True,
    **column2field,
):
    idx = pd.Index(utils.make_argument_iterable(ids))
    id_is_duplicate = idx.duplicated()
    if id_is_duplicate.any():
        event_ids = idx.unique()
    else:
        event_ids = idx
    event_records = []
    for evt in iter_objects_by_ids(*event_ids):
        try:
            event_info = evt.get_property_values(
                include_shared=include_shared,
                include_individual=include_individual,
                exclude_properties=exclude_properties,
                **column2field,
            )
            if not include_individual:
                event_info["id"] = evt.id
        except AttributeError:
            if skip_missing:
                continue
            else:
                raise
        event_records.append(event_info)
    events = pd.DataFrame.from_records(event_records).set_index("id")
    return events.reindex(idx).reset_index()


@flyweight()
class Event(FixedCoordinateTypeObject[ET]):
    """
    The base types are initialized with a dict-like or any other object that can be indexed:
    Event.get(x) is equivalent to Event._data[x]. Subclasses may be adapted for other data types
    by overriding :meth:`get_accessor` and/or :meth:`get`.
    """

    _property_defaults = None

    def __init__(
        self,
        unit: TimeUnit | str,
        number_type: NumberType,
        data: Optional[ET] = None,
        id_prefix: str = "ev",
        uid: Optional[str] = None,
    ) -> None:
        super().__init__(
            unit=unit, number_type=number_type, id_prefix=id_prefix, uid=uid
        )
        self._data = None
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: Any):
        self._data = data

    def assert_property(self, name):
        assert getattr(self, name, None) is not None, (
            f"No {name!r} has been defined for {self.class_name} " f"{self.id!r}."
        )

    def validate(self) -> None:
        assert self.data is not None, f"{self.class_name} does not point to any data."

    def get_accessor(self) -> Callable:
        return self._data.__getitem__

    def get(self, field: str) -> Literal:
        """Get property value from the event_data."""
        if field is None:
            return Missing.FIELD_NAME_UNDEFINED
        if not self._data:
            return Missing.DATA_UNDEFINED
        accessor = self.get_accessor()
        try:
            return accessor(field)
        except (KeyError, AttributeError):
            return Missing.FIELD_MISSING_FROM_EVENT_DATA

    def get_shared_property_value(self, field_name):
        return self._shared[field_name]

    def __getattr__(self, name: str):
        """Returning plain values for flyweights for which no @property has been defined."""
        if name in self._shared:
            return self.get_shared_property_value(name)
        raise AttributeError(f"{self.class_name} has no {name!r} property.")

    @cache
    def get_property(self, name: str):
        field_name = self.get_shared_property_value(name)
        if field_name is None:
            return Missing.FIELD_NAME_UNDEFINED
        return self.get(field_name)

    def __repr__(self):
        properties = self.get_property_values(
            include_shared=True
        )  # method injected by @flyweight
        prop_str = ", ".join([f"{k}={v!r}" for k, v in properties.items()])
        return f"{self.class_name}(id={self.id!r}, {prop_str})"


@flyweight()
class InstantEvent(Event[ET]):

    @classmethod
    def from_event_data(cls, data: ET, **kwargs) -> Self:
        return cls(instant=data.get("instant"), data=data, **kwargs)

    def __init__(
        self,
        instant: Coordinate | Number,
        unit: Optional[TimeUnit | str] = None,
        number_type: Optional[NumberType] = None,
        data: Optional[ET] = None,
        id_prefix: str = "ev",
        uid: Optional[str] = None,
    ):
        instant = make_coordinate(
            value=instant,
            unit=unit,
            number_type=number_type,
            default_unit=self._default_unit,
            default_number_type=self._default_number_type,
        )
        super().__init__(
            unit=instant.unit,
            number_type=instant.number_type,
            data=data,
            id_prefix=id_prefix,
            uid=uid,
        )
        self._instant = instant

    def validate(self) -> None:
        super().validate()
        self.assert_property("instant")

    @property
    def instant(self):
        return self._instant

    @instant.setter
    def instant(self, instant: Coordinate):
        if not isinstance(instant, Coordinate):
            raise ValueError(f"Expected a Coordinate, got a {type(instant).__name__}.")
        self._instant = instant

    @property
    def start(self):
        return self.instant

    @property
    def length(self):
        return self.make_coordinate(0)

    @property
    def end(self):
        return self.instant

    @property
    def interval(self) -> tuple[Number, Number]:
        """Pair of coordinate values understood as [start, end), i.e., as a left-inclusive interval."""
        return (self.instant.value, self.instant.value)


@flyweight()
class IntervalEvent(Event[ET]):

    @classmethod
    def from_event_data(cls, data: ET, **kwargs) -> Self:
        return cls(
            start=data.get("start"),
            end=data.get("end"),
            length=data.get("length"),
            data=data,
            **kwargs,
        )

    def __init__(
        self,
        start: Coordinate | Number,
        end: Optional[Coordinate | Number] = None,
        length: Optional[Coordinate | Number] = None,
        unit: Optional[TimeUnit | str] = None,
        number_type: Optional[NumberType] = None,
        data: Optional[ET] = None,
        id_prefix: str = "ev",
        uid: Optional[str] = None,
    ):
        start = make_coordinate(
            value=start,
            unit=unit,
            number_type=number_type,
            default_unit=self._default_unit,
            default_number_type=self._default_number_type,
        )
        super().__init__(
            unit=start.unit,
            number_type=start.number_type,
            data=data,
            id_prefix=id_prefix,
            uid=uid,
        )
        utils.validate_interval_args(start=start, end=end, length=length)
        self._start = None
        self._end = None
        self._length = None
        self.start = start
        if end is not None:
            self.end = end
        if length is not None:
            self.length = length

    def validate(self) -> None:
        super().validate()
        self.assert_property("start")
        self.assert_property("end")

    @property
    def start(self) -> Coordinate:
        return self._start

    @start.setter
    def start(self, value: Coordinate):
        if self._end is not None:
            assert value <= self.end, f"Start {value} is after end {self.end}"
        self._start = self.make_coordinate(value)
        self._update_length()

    @property
    def length(self):
        if self._length is not None:
            return self._length
        return self.end - self.start

    @length.setter
    def length(self, length: Coordinate | Number):
        assert length >= 0, f"Length cannot be negative, got {length}"
        self._length = self.make_coordinate(length)
        self._end = self.start + self._length

    @property
    def end(self):
        if self._end is not None:
            return self._end
        return self.start + self.length

    @end.setter
    def end(self, value: Coordinate | Number):
        assert value >= self.start, f"End {value} is before start {self.start}"
        self._end = self.make_coordinate(value)
        self._update_length()

    # this has decidedly no 'instants' property so that the presence of it can be used to
    # differentiate between events that implement the PInstantEvent Protocol from those that
    # implement the PIntervalEvent Protocol in an efficient way

    @property
    def interval(self) -> tuple[Number, Number]:
        """Pair of coordinate values understood as [start, end), i.e., as a left-inclusive interval."""
        return (self.start.value, self.end.value)

    def _update_length(self):
        if self._end is None and self._length is None:
            return
        new_length = self.end - self.start
        assert new_length >= 0, f"Start {self.start} is after end {self.end}"
        self._length = new_length


class GraphicalEvent:
    _default_unit = TimeUnit.pixels
    _default_number_type = NumberType.int


@flyweight()
class GraphicalInstantEvent(GraphicalEvent, InstantEvent[ET], Generic[ET]):
    pass


@flyweight()
class GraphicalIntervalEvent(GraphicalEvent, IntervalEvent[ET], Generic[ET]):
    pass


class LogicalEvent(Event):
    _default_unit = TimeUnit.quarters
    _default_number_type = NumberType.fraction


@flyweight()
class LogicalInstantEvent(LogicalEvent, InstantEvent[ET], Generic[ET]):
    pass


@flyweight()
class LogicalIntervalEvent(LogicalEvent, IntervalEvent[ET], Generic[ET]):
    pass


class PhysicalEvent:
    _default_unit = TimeUnit.seconds
    _default_number_type = NumberType.float


@flyweight()
class PhysicalInstantEvent(PhysicalEvent, InstantEvent[ET], Generic[ET]):
    pass


@flyweight()
class PhysicalIntervalEvent(PhysicalEvent, IntervalEvent[ET], Generic[ET]):
    pass


class PEvent(Protocol):
    id: str
    data: Any

    def get(self, field: str) -> Literal: ...


class PInstantEvent(PEvent):
    """"""

    instant: Number


class PIntervalEvent(PEvent):
    """"""

    start: Number
    end: Number
    length: Number


Inst = TypeVar("Inst", bound=InstantEvent | PInstantEvent)
Intv = TypeVar("Intv", bound=IntervalEvent | PIntervalEvent)

# endregion Event types
# region Silo types


class Silo(RegisteredObject[ST], Generic[ST]):
    _default_timeline_type: Optional[str] = None

    def __init__(
        self,
        data: ST,
        meta: Optional[Meta | dict] = None,
        id_prefix: str = "silo",
        uid: Optional[str] = None,
        **kwargs,
    ):
        self.validate_silo_data(data)
        super().__init__(
            id_prefix=id_prefix,
            uid=uid,
        )
        self._data = None
        self.data = data
        self._meta = meta
        self.meta = meta

    @classmethod
    def from_filepath(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        **kwargs,
    ):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = f.read()
        except UnicodeDecodeError:
            with open(filepath, "rb") as f:
                data = f.read()
        return cls(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )

    @property
    def data(self) -> ET:
        return self._data

    @data.setter
    def data(self, data: ET):
        self._data = data

    @property
    def meta(self) -> Meta:
        """Metadata associated with the EventSilo."""
        return Meta(
            id=self.id,
            **self._meta,
        )

    @meta.setter
    def meta(self, meta: Meta | dict):
        self._meta = Meta() if meta is None else Meta(meta)

    def validate_silo_data(self, data: ST) -> None:
        assert data is not None, "data cannot be None"

    def initialize_empty_timeline(
        self, timeline_class: Optional[Type[Timeline] | str] = None, **kwargs
    ):
        """Create a new timeline using the default timeline class if not otherwise specified."""
        if timeline_class is None:
            if self._default_timeline_type is None:
                raise ValueError(
                    f"No default timeline type has been defined for {self.class_name}"
                )
            timeline_class = self._default_timeline_type
        timeline_class = get_class(timeline_class)
        id_prefix = kwargs.pop("id_prefix", f"{self.id}/tl")
        meta = self.meta.update(kwargs.pop("meta", {}))
        timeline: Timeline = timeline_class(id_prefix=id_prefix, meta=meta, **kwargs)
        return timeline

    def get_default_conversion_maps(self) -> list[ConversionMap]:
        return []

    def get_default_cmaps(self):
        """Alias for get_default_conversion_maps."""
        return self.get_default_conversion_maps()

    def make_timeline(
        self, timeline_class: Optional[Type[Timeline] | str] = None, **kwargs
    ):
        timeline = self.initialize_empty_timeline(timeline_class, **kwargs)
        self.populate_timeline(timeline)
        cmaps = self.get_default_conversion_maps()
        timeline.add_conversion_maps(*cmaps)
        return timeline

    def populate_timeline(self, timeline):
        """Most subclasses will override this method to add events to the timeline."""
        return


class AudioSilo(Silo[np.ndarray]):

    _default_timeline_type = "DiscretePhysicalTimeline"

    @classmethod
    def from_filepath(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        **kwargs,
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            y, sr = librosa.load(filepath, sr=None, mono=True)
        return cls(
            data=y,
            sample_rate=sr,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )

    def __init__(
        self,
        data: np.ndarray,
        sample_rate: int | float,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        id_prefix: str = "silo",
        uid: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            id_prefix=id_prefix,
            uid=uid,
            **kwargs,
        )
        self._sample_rate = sample_rate

    @property
    def sample_rate(self) -> int | float:
        return self._sample_rate

    def make_timeline(
        self, timeline_class: Optional[Type[Timeline] | str] = None, **kwargs
    ):
        length = Coordinate(self.data.shape[0], "samples_int")
        tl_args = dict(kwargs, length=length)
        return super().make_timeline(timeline_class=timeline_class, **tl_args)

    def get_default_conversion_maps(self) -> list[ConversionMap]:
        cmaps = super().get_default_conversion_maps()
        cmaps.append(SamplesToSeconds(sample_rate=self.sample_rate))
        return cmaps


# endregion Silo types
# region EventSilo types


class PEventSilo(Protocol):

    def iter_events(self, **kwargs) -> Iterator[Inst | Intv]: ...

    @overload
    def iter_instant_events(
        self, event_type: Literal[None]
    ) -> Iterator[PInstantEvent]: ...

    @overload
    def iter_instant_events(self, event_type: Type[Inst]) -> Iterator[Inst]: ...

    def iter_instant_events(
        self, event_type: Optional[Type[Inst]] = None
    ) -> Iterator[PInstantEvent] | Iterator[Inst]: ...

    @overload
    def iter_interval_events(
        self, event_type: Literal[None]
    ) -> Iterator[PIntervalEvent]: ...

    @overload
    def iter_interval_events(self, event_type: Type[Inst]) -> Iterator[Inst]: ...

    def iter_interval_events(
        self, event_type: Optional[Type[Inst]] = None
    ) -> Iterator[PIntervalEvent] | Iterator[Inst]: ...

    def iter_raw_event_data(self) -> Iterator[Any]: ...

    def iter_raw_instant_event_data(self) -> Iterator[Any]: ...

    def iter_raw_interval_event_data(self) -> Iterator[Any]: ...


class _EventTypesMixin:
    """Injects instant_event_type and interval_event_type as init arguments and properties.
    The latter make use of the class attributes _default_instant_event_type and
    _default_interval_event_type.
    """

    _default_instant_event_type: Optional[Type[PInstantEvent]] = None
    _default_interval_event_type: Optional[Type[PIntervalEvent]] = None

    def __init__(
        self,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        **kwargs,
    ):
        self._instant_event_type: Optional[Type[Inst]] = instant_event_type
        self._interval_event_type: Optional[Type[Intv]] = interval_event_type
        super().__init__(**kwargs)

    @property
    def instant_event_type(self) -> Type[Inst]:
        if self._instant_event_type is not None:
            return self._instant_event_type
        if self._default_instant_event_type is not None:
            return self._default_instant_event_type
        raise ValueError(
            f"No instant_event_type has been defined for this {self.class_name}."
        )

    @property
    def interval_event_type(self) -> Type[Intv]:
        if self._interval_event_type is not None:
            return self._interval_event_type
        if self._default_interval_event_type is not None:
            return self._default_interval_event_type
        raise ValueError(
            f"No interval_event_type has been defined for this {self.class_name}."
        )


class EventSilo(_EventTypesMixin, Silo[ST], PEventSilo, Generic[ST, Inst, Intv]):
    """Silo"""

    _default_instant_event_type = InstantEvent
    _default_interval_event_type = IntervalEvent

    def __init__(
        self,
        data: ST,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        meta: Optional[Meta | dict] = None,
        id_prefix: str = "silo",
        uid: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            data=data,
            meta=meta,
            id_prefix=id_prefix,
            uid=uid,
        )

    def iter_raw_instant_event_data(self) -> Iterator[Any]:
        raise NotImplementedError

    def iter_raw_interval_event_data(self) -> Iterator[Any]:
        raise NotImplementedError

    def iter_events(self, **kwargs) -> Iterator[PInstantEvent | PIntervalEvent]:
        yield from self.iter_instant_events(**kwargs)
        yield from self.iter_interval_events(**kwargs)

    def iter_instant_events(
        self, event_type: Optional[Type[PInstantEvent]] = None, **kwargs
    ) -> Iterator[Inst] | Iterator[PInstantEvent]:
        id_prefix = kwargs.pop("id_prefix", f"{self.id}/ev")
        if event_type is None:
            event_type = self.instant_event_type
        for raw_instant_event in self.iter_raw_instant_event_data():
            yield event_type.from_event_data(
                raw_instant_event, id_prefix=id_prefix, **kwargs
            )

    def iter_interval_events(
        self, event_type: Optional[Type[Inst]] = None, **kwargs
    ) -> Iterator[Intv] | Iterator[PIntervalEvent]:
        id_prefix = kwargs.pop("id_prefix", f"{self.id}/ev")
        if event_type is None:
            event_type = self.interval_event_type
        for raw_interval_event in self.iter_raw_interval_event_data():
            yield event_type.from_event_data(
                raw_interval_event, id_prefix=id_prefix, **kwargs
            )

    def populate_timeline(self, timeline):
        timeline.add_events(
            self.iter_events(id_prefix=f"{timeline.id}/ev"), allow_expansion=True
        )


class DataFrameSilo(EventSilo[pd.DataFrame, Inst, Intv]):
    """A Silo that creates events from a pandas DataFrame."""

    @classmethod
    def from_csv_file(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        parse_options: Optional[dict] = None,
        **kwargs,
    ) -> Self:
        if parse_options is None:
            parse_options = {}
        data = pd.read_csv(filepath, **parse_options)
        return cls(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )

    @classmethod
    def from_json_file(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        parse_options: Optional[dict] = None,
        **kwargs,
    ) -> Self:
        data = load_json_file(filepath)

        return cls(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )

    @classmethod
    def from_filepath(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        parse_options: Optional[dict] = None,
        **kwargs,
    ) -> Self:
        if isinstance(filepath, str):
            filepath = Path(filepath)
        fext = filepath.suffix.lower()
        if fext in (".csv", ".tsv"):
            if fext == ".tsv" and "sep" not in parse_options:
                parse_options["sep"] = "\t"
            return cls.from_csv_file(
                filepath=filepath,
                instant_event_type=instant_event_type,
                interval_event_type=interval_event_type,
                parse_options=parse_options,
                **kwargs,
            )
        elif fext in (".json", ".jsonl"):
            return cls.from_json_file(
                filepath=filepath,
                instant_event_type=instant_event_type,
                interval_event_type=interval_event_type,
                parse_options=parse_options,
                **kwargs,
            )
        else:
            raise ValueError(
                f"Unsupported file extension {fext!r} for {cls.class_name}. "
                "Supported extensions are: .csv, .tsv, .json, .jsonl."
            )

    def __init__(
        self,
        data: pd.DataFrame,
        instant_event_selector: Optional[
            pd.Series | pd.Index | np.ndarray | list | tuple
        ] = None,
        interval_event_selector: Optional[
            pd.Series | pd.Index | np.ndarray | list | tuple
        ] = None,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        instant_col: str = "instant",
        start_col: str = "start",
        end_col: str = "end",
        length_col: str = "length",
        **kwargs,
    ):
        super().__init__(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )
        if instant_event_selector is None and interval_event_selector is None:
            warnings.warn(
                "No event selectors have been defined, assuming all events are intervals."
            )
            self.instant_event_selector = None
            self.interval_event_selector = pd.Series(True, index=data.index)
        else:
            self.instant_event_selector = instant_event_selector
            self.interval_event_selector = interval_event_selector
        self.instant_col: str = instant_col
        self.start_col: str = start_col
        self.end_col: str = end_col
        self.length_col: str = length_col

    def validate_silo_data(self, data: ST) -> None:
        assert (
            data.index.is_unique
        ), "DataFrame index has duplicates. Use .reset_index()"
        duplicate_cols = data.columns[data.columns.duplicated()]
        assert (
            duplicate_cols.size == 0
        ), f"DataFrame has duplicate columns: {duplicate_cols.to_list()}"

    def subselect_instant_events(self) -> pd.DataFrame:
        if self.instant_event_selector is None:
            return
        selection = self.data[self.instant_event_selector]
        if self.instant_col is not None and self.instant_col != "instant":
            renaming = {self.instant_col: "instant"}
            return selection.rename(columns=renaming)
        return selection

    def subselect_interval_events(self) -> pd.DataFrame:
        if self.interval_event_selector is None:
            return
        selection = self.data[self.interval_event_selector]
        renaming = {}
        if self.start_col is not None and self.start_col != "start":
            renaming[self.start_col] = "start"
        if self.end_col is not None and self.end_col != "end":
            renaming[self.end_col] = "end"
        if self.length_col is not None and self.length_col != "length":
            renaming[self.length_col] = "length"
        if renaming:
            return selection.rename(columns=renaming)
        return selection

    def iter_raw_instant_event_data(self) -> Iterator[dict]:
        selection = self.subselect_instant_events()
        if selection is None:
            return
        yield from selection.to_dict(orient="records")

    def iter_raw_interval_event_data(self) -> Iterator[dict]:
        selection = self.subselect_interval_events()
        if selection is None:
            return
        yield from selection.to_dict(orient="records")


# endregion EventSilo types
# region MidiDataFrameSilo


class MidiEvent:
    """This is a mix-in class used for class composition."""

    _property_defaults = dict(type="type", note="note", velocity="velocity")
    _default_unit = TimeUnit.ticks
    _default_number_type = NumberType.int

    @property
    def type(self):
        return self.get_property("type")

    @property
    def note(self):
        return self.get_property("note")

    @property
    def velocity(self):
        return self.get_property("velocity")


@flyweight()
class MidiIntervalEvent(MidiEvent, IntervalEvent):
    pass


@flyweight()
class MidiInstantEvent(MidiEvent, InstantEvent):
    pass


class MidiDataFrameSilo(DataFrameSilo):
    _default_timeline_type = "DiscreteLogicalTimeline"
    _default_instant_event_type = MidiInstantEvent
    _default_interval_event_type = MidiIntervalEvent

    @classmethod
    def from_filepath(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        **kwargs,
    ):
        fp = Path(filepath)
        if fp.suffix.lower() in (".midi", ".mid"):
            midi_df = midi_to_df(filepath)
            has_duration = midi_df.duration.notna()
            return cls(
                data=midi_df,
                instant_event_selector=~has_duration,
                interval_event_selector=has_duration,
                instant_event_type=instant_event_type,
                interval_event_type=interval_event_type,
                **kwargs,
            )
        return super().from_filepath(
            filepath=filepath,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )

    def __init__(
        self,
        data: pd.DataFrame,
        instant_event_selector: pd.Series | pd.Index | np.ndarray | list | tuple,
        interval_event_selector: pd.Series | pd.Index | np.ndarray | list | tuple,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        instant_col: str = "absolute_time",
        start_col: str = "absolute_time",
        end_col: str = "end",
        length_col: str = "duration",
        **kwargs,
    ):
        super().__init__(
            data=data,
            instant_event_selector=instant_event_selector,
            interval_event_selector=interval_event_selector,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            instant_col=instant_col,
            start_col=start_col,
            end_col=end_col,
            length_col=length_col,
            **kwargs,
        )

    def get_default_conversion_maps(self) -> list[ConversionMap]:
        return [ticks2seconds_map_from_midi_df(self.data)]


# endregion MidiDataFrameSilo
# region TiliaDataFrameSilo


class TiliaEvent:
    _default_unit = TimeUnit.seconds
    _default_number_type = NumberType.float
    _property_defaults = dict(
        timeline="timeline",
        name="name",
        component="component",
    )

    @property
    def timeline(self):
        return self.get_property("timeline")

    @property
    def name(self):
        return self.get_property("name")

    @property
    def component(self):
        return self.get_property("component")


@flyweight()
class TiliaInstantEvent(TiliaEvent, PhysicalInstantEvent):
    pass


@flyweight()
class TiliaIntervalEvent(TiliaEvent, PhysicalIntervalEvent):
    pass


class TiliaDataFrameSilo(DataFrameSilo):
    _default_timeline_type = "ContinuousPhysicalTimeline"
    _default_instant_event_type = TiliaInstantEvent
    _default_interval_event_type = TiliaIntervalEvent

    @classmethod
    def from_csv_file(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        parse_options: Optional[dict] = None,
        **kwargs,
    ) -> Self:
        raise NotImplementedError(f"CSV files are not supported for {cls.class_name}.")

    @classmethod
    def from_json_file(
        cls,
        filepath: str | Path,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        parse_options: Optional[dict] = None,
        **kwargs,
    ) -> Self:
        data = parse_tilia_json(filepath)
        is_instant = data.time.notna()
        is_interval = data.start.notna()
        return cls(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            instant_event_selector=is_instant,
            interval_event_selector=is_interval,
            **kwargs,
        )

    def __init__(
        self,
        data: pd.DataFrame,
        instant_event_selector: pd.Series | pd.Index | np.ndarray | list | tuple,
        interval_event_selector: pd.Series | pd.Index | np.ndarray | list | tuple,
        instant_event_type: Optional[Type[Inst]] = None,
        interval_event_type: Optional[Type[Intv]] = None,
        instant_col: str = "time",
        start_col: str = "start",
        end_col: str = "end",
        length_col: str = None,
        **kwargs,
    ):
        super().__init__(
            data=data,
            instant_event_selector=instant_event_selector,
            interval_event_selector=interval_event_selector,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            instant_col=instant_col,
            start_col=start_col,
            end_col=end_col,
            length_col=length_col,
            **kwargs,
        )

    def get_default_conversion_maps(self) -> list[ConversionMap]:
        measure_map = make_region_map_from_tilia_df(self.data, column_type="measure")
        beat_map = make_region_map_from_tilia_df(self.data, column_type="beat")
        return [measure_map, beat_map]


def make_region_map_from_tilia_df(
    tla: pd.DataFrame, column_type: Literal["measure", "beat"]
):
    seconds2values = make_unique_constants_map_from_tilia_df(tla, column_type)
    breaks = seconds2values.index.to_list() + [np.inf]
    return RegionMap.from_breaks(
        breaks,
        seconds2values.values,
        source_unit="seconds",
        target_unit=column_type + "s",
        column_name=column_type,
    )


def make_unique_constants_map_from_tilia_df(
    tla: pd.DataFrame, column_type: Literal["measure", "beat"]
):
    intv_start_col = f"start_{column_type}"
    intv_end_col = f"end_{column_type}"
    instant2measure_complete = pd.concat(
        [
            tla[["start", f"start_{column_type}"]].rename(
                columns={"start": "instant", intv_start_col: column_type}
            ),
            tla[["end", "end_measure"]].rename(
                columns={"end": "instant", intv_end_col: column_type}
            ),
            tla[["time", column_type]].rename(columns=dict(time="instant")),
        ]
    )
    instant2measure = instant2measure_complete.groupby("instant").agg(set).iloc[:, 0]
    (instant2measure.map(len) > 1).any()
    values = instant2measure.map(lambda x: x.pop())
    values = values.loc[values != values.shift()]
    return values


# endregion TiliaDataFrameSilo
# region partitura parsing


class PartituraEvent(LogicalEvent):
    _default_unit = TimeUnit.ticks
    _default_number_type = NumberType.int

    _property_defaults = dict(type="type", note_id="id")

    def get_accessor(self) -> Callable:
        return partial(getattr, self._data)

    @property
    def type(self):
        return self.data.__class__.__name__

    @property
    def note_id(self):
        return self.get_property("note_id")


@flyweight()
class PartituraInstantEvent(PartituraEvent, LogicalInstantEvent[pts.TimedObject]):

    @classmethod
    def from_event_data(cls, data: pts.TimedObject, **kwargs) -> Self:
        instant = data.start.t
        return cls(instant=instant, data=data, uid=getattr(data, "id", None), **kwargs)


@flyweight()
class PartituraIntervalEvent(PartituraEvent, LogicalIntervalEvent[pts.TimedObject]):

    @classmethod
    def from_event_data(cls, data: pts.TimedObject, **kwargs) -> Self:
        start_val = data.start.t
        end_val = data.end.t
        length = data.duration
        return cls(
            start=start_val,
            end=end_val,
            length=length,
            data=data,
            uid=getattr(data, "id", None),
            **kwargs,
        )


@flyweight()
class PartituraPerformedNote(PartituraEvent, LogicalIntervalEvent[ptp.PerformedNote]):

    @classmethod
    def from_event_data(cls, data: ptp.PerformedNote, **kwargs) -> Self:
        """Does not work directly with PerformedNote objects because they have insufficient
        timing information. The PartituraPerformanceSilo enriches them using the same
        function used for partitura's note arrays.
        """
        start_val = data.get("onset_tick")
        length = data.get("duration_tick")
        end_val = start_val + length
        return cls(
            start=start_val,
            end=end_val,
            length=length,
            data=data,
            uid=getattr(data, "id", None),
            **kwargs,
        )

    def get_accessor(self) -> Callable:
        return self._data.get


class _PartituraMixin:
    """Mixin for Partitura-specific silos."""

    _default_timeline_type = "DiscreteLogicalTimeline"

    @property
    def timed_object_counts(self) -> dict[Type[pts.TimedObject], int]:
        """An overview dict counting this silo's raw event items by type."""
        return {k: len(v) for k, v in self._events_by_type.items()}

    @property
    def n_instant_events(self) -> int:
        return sum(1 for _ in self.iter_raw_instant_event_data())

    @property
    def n_events(self) -> int:
        return sum(map(len, self._events_by_type.values()))

    @property
    def n_parts(self) -> int:
        return len(self.data)

    @property
    def n_interval_events(self) -> int:
        """Number of all interval events without merging tied notes (i.e., two tied notes count as 2)."""
        return sum(1 for _ in self.iter_raw_interval_event_data(merge_tied_notes=False))

    def __repr__(self):
        type_counts = {cls.__name__: n for cls, n in self.timed_object_counts.items()}
        type_counts = pformat(type_counts)
        return (
            f"{self.class_name}("
            f"id={self.id!r}, "
            f"n_parts={self.n_parts}, "
            f"n_interval_events={self.n_interval_events}, "
            f"n_instant_events={self.n_instant_events}"
            f")\n{type_counts}"
        )


class PartituraPerformanceSilo(
    _PartituraMixin,
    EventSilo[list[pts.Part], PartituraInstantEvent, PartituraIntervalEvent],
):
    _default_instant_event_type = None
    _default_interval_event_type = PartituraPerformedNote

    def __init__(
        self,
        data: ptp.Performance | ptp.PerformedPart | Iterable[ptp.PerformedPart],
        instant_event_type: Optional[Type[PInstantEvent]] = None,
        interval_event_type: Optional[Type[PIntervalEvent]] = None,
        **kwargs,
    ):
        self._performance: Optional[ptp.Performance] = None
        super().__init__(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )
        self.ppq_values = []
        pnotes = set()
        for ppart in self.data:
            self.ppq_values.append(get_divs_per_quarter(ppart))
            pnotes.update(get_performed_notes(ppart, ppart.ppq, ppart.mpq))
        self._events_by_type: dict[Type[ptp.PerformedNote], set[ptp.PerformedNote]] = {
            ptp.PerformedNote: pnotes,
        }

    @property
    def data(self):
        return self._data

    @data.setter
    def data(
        self, data: ptp.Performance | ptp.PerformedPart | Iterable[ptp.PerformedPart]
    ):
        if isinstance(data, ptp.Performance):
            self._data = data.performedparts
            self._performance = data
        else:
            parts = list(utils.make_argument_iterable(data))
            if not parts:
                raise ValueError(
                    f"No parts provided to the {self.class_name} {self.id!r}."
                )
            self._data = []
            for p in parts:
                if isinstance(p, ptp.PerformedPart):
                    self._data.append(p)
                else:
                    warnings.warn(
                        f"Ignoring unsupported type {type(p).__name__} in data."
                    )

    def iter_events(self, **kwargs) -> Iterator[PInstantEvent | PIntervalEvent]:
        yield from self.iter_interval_events(**kwargs)

    def iter_instant_events(self):
        yield from []

    def iter_raw_event_data(self, merge_tied_notes=True) -> Iterator[Any]:
        if len(set(self.ppq_values)) > 1:
            raise NotImplementedError(
                f"Performed parts need to have the same ppq value, got {self.ppq_values}"
            )
        for instances in self._events_by_type.values():
            yield from instances

    def iter_raw_instant_event_data(self) -> Iterator[Any]:
        yield from []

    def iter_raw_interval_event_data(self, merge_tied_notes=True) -> Iterator[Any]:
        yield from self.iter_raw_event_data()


class PartituraScoreSilo(
    _PartituraMixin,
    EventSilo[list[pts.Part], PartituraInstantEvent, PartituraIntervalEvent],
):
    _default_instant_event_type = PartituraInstantEvent
    _default_interval_event_type = PartituraIntervalEvent

    def __init__(
        self,
        data: pts.Score | pts.Part | Iterable[pts.Part],
        instant_event_type: Optional[Type[PInstantEvent]] = None,
        interval_event_type: Optional[Type[PIntervalEvent]] = None,
        **kwargs,
    ):
        self._score: Optional[pts.Score] = None
        super().__init__(
            data=data,
            instant_event_type=instant_event_type,
            interval_event_type=interval_event_type,
            **kwargs,
        )
        self.ppq_values = [get_divs_per_quarter(part) for part in self.data]
        self._events_by_type: dict[Type[pts.TimedObject], set[pts.TimedObject]] = (
            get_event_dict(self._data)
        )

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: pts.Score | pts.Part | Iterable[pts.Part]):
        if isinstance(data, pts.Score):
            self._data = data.parts
            self._score = data
        else:
            parts = list(utils.make_argument_iterable(data))
            if not parts:
                raise ValueError(
                    f"No parts provided to the {self.class_name} {self.id!r}."
                )
            self._data = []
            for p in parts:
                if isinstance(p, pts.Part):
                    self._data.append(p)
                else:
                    warnings.warn(
                        f"Ignoring unsupported type {type(p).__name__} in data."
                    )
        for part in self._data:
            pts.add_segments(part)

    def make_df(
        self,
        note_array=True,
        rest_array=True,
        event_array=True,
        include_pitch_spelling=False,
        include_key_signature=False,
        include_time_signature=False,
        include_metrical_position=False,
        include_grace_notes=False,
        include_staff=False,
        include_divs_per_quarter=False,
        merge_tied_notes=True,
        collapse_rests=True,
        include_type=True,
        meta: Optional[Meta | dict] = None,
    ) -> DF:
        return event_df_from_part_list(
            parts=self.data,
            note_array=note_array,
            rest_array=rest_array,
            event_array=event_array,
            include_pitch_spelling=include_pitch_spelling,
            include_key_signature=include_key_signature,
            include_time_signature=include_time_signature,
            include_metrical_position=include_metrical_position,
            include_grace_notes=include_grace_notes,
            include_staff=include_staff,
            include_divs_per_quarter=include_divs_per_quarter,
            merge_tied_notes=merge_tied_notes,
            collapse_rests=collapse_rests,
            include_type=include_type,
            meta=meta,
        )

    @overload
    def get_part_maps(
        self, map_types: PartMap, part_index: Optional[Iterable[int | slice]] = None
    ) -> dict[str, Interpolator]: ...

    @overload
    def get_part_maps(
        self,
        map_types: Iterable[PartMap] | Literal[None],
        part_index: Optional[Iterable[int | slice]] = None,
    ) -> dict[str, dict[PartMap, Interpolator]]: ...

    def get_part_maps(
        self,
        map_types: Optional[PartMap | Iterable[PartMap]] = None,
        part_index: Optional[Iterable[int | slice]] = None,
    ) -> dict[str, Interpolator | dict[PartMap, Interpolator]]:
        single_element = False
        if map_types is None:
            map_types = list(PartMap)
        else:
            single_element = isinstance(map_types, str)
            map_types = [PartMap(mt) for mt in utils.make_argument_iterable(map_types)]
        if part_index is None:
            parts = self.data
        else:
            idx = utils.make_argument_iterable(part_index)
            parts = [self.data[i] for i in idx]
        result = {} if single_element else defaultdict(dict)
        for part in parts:
            if single_element:
                result[part.id] = getattr(part, map_types[0].value)
            else:
                result[part.id] = {m: getattr(part, m.value) for m in map_types}
        return result

    def iter_events(
        self, merge_tied_notes=True, **kwargs
    ) -> Iterator[PInstantEvent | PIntervalEvent]:
        yield from self.iter_instant_events(**kwargs)
        yield from self.iter_interval_events(
            merge_tied_notes=merge_tied_notes, **kwargs
        )

    def iter_interval_events(
        self, event_type: Optional[Type[Inst]] = None, merge_tied_notes=True, **kwargs
    ) -> Iterator[Intv] | Iterator[PIntervalEvent]:
        id_prefix = kwargs.pop("id_prefix", f"{self.id}/ev")
        if event_type is None:
            event_type = self.interval_event_type
        for raw_interval_event in self.iter_raw_interval_event_data(
            merge_tied_notes=merge_tied_notes
        ):
            yield event_type.from_event_data(
                raw_interval_event, id_prefix=id_prefix, **kwargs
            )

    def iter_raw_event_data(self, merge_tied_notes=True) -> Iterator[Any]:
        div_pq_values = [get_divs_per_quarter(part) for part in self.data]
        if len(set(div_pq_values)) > 1:
            merged_parts = pts.merge_parts(self.data, reassign="staff")
            self.logger.warning(
                f"The parts had different quarter_durations ({div_pq_values}) and "
                f"had to be merged and converted to a quarter_duration of {get_divs_per_quarter(merged_parts)}"
            )
            merged_events = get_event_dict(merged_parts)
            event_iterator = merged_events.values()
        else:
            event_iterator = self._events_by_type.values()
        for instances in event_iterator:
            for instance in instances:
                instance_id = getattr(instance, "id", None)
                if instance.duration is not None and instance.duration < 0:
                    self.logger.warning(
                        f"Skipped {instance.__class__.__name__} @ {instance.start} because of "
                        f"its negative duration {instance.duration}"
                    )
                    continue
                if merge_tied_notes and hasattr(instance, "tie_prev"):
                    if instance.tie_prev is not None:
                        obj_info = instance.__class__.__name__
                        if instance_id is not None:
                            obj_info += f" (ID {instance_id!r})"
                        self.logger.debug(
                            f"Skipped {obj_info} @ {instance.start} because "
                            f"it is tied to the previous note and merge_tied_notes=True"
                        )

                        continue
                    instance.length = instance.duration_tied
                else:
                    instance.length = instance.duration
                yield instance

    def iter_raw_instant_event_data(self) -> Iterator[Any]:
        yield from filter(lambda evt: evt.duration is None, self.iter_raw_event_data())

    def iter_raw_interval_event_data(self, merge_tied_notes=True) -> Iterator[Any]:
        yield from filter(
            lambda evt: evt.duration is not None,
            self.iter_raw_event_data(merge_tied_notes=merge_tied_notes),
        )


# endregion partitura parsing

if __name__ == "__main__":
    from processing.notebooks.midi_parsing import load_supra_midi

    midi_df = load_supra_midi()
    ev_data = midi_df.loc[151]
    inst_ev = InstantEvent(ev_data, instant="absolute_time")
    print(inst_ev.instant)
    print(inst_ev)
    intv_ev = IntervalEvent(ev_data, start="absolute_time", length="duration")
    print(intv_ev)
    print(intv_ev.length)
    reg = get_registry_by_prefix("ev")
    print(reg.get("ev2"))
