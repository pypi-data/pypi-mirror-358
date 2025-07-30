from __future__ import annotations

import logging
import os.path as osp
import warnings
from dataclasses import dataclass
from dataclasses import replace as copy_dataclass
from pathlib import Path
from pprint import pformat
from typing import Dict, Generic, Iterable, Optional, Self, Type, TypeVar

import pymupdf
from pymupdf import Document, Matrix, Page, Pixmap, Rect, csRGB

from processing.tta import utils
from processing.tta.common import RegisteredObject
from processing.tta.events import (
    AudioSilo,
    MidiDataFrameSilo,
    PartituraScoreSilo,
    Silo,
)
from processing.tta.registry import ID_str, ensure_registration, get_object_by_id
from processing.tta.timelines import (
    Timeline,
)
from processing.tta.utils import NamedSources
from processing.utils import get_specimen_path

logger = logging.getLogger(__name__)


@dataclass
class File:
    """A simple data class to represent a file with its identifiers, checksum, and other metadata."""

    name: Optional[str] = None
    """Arbitrary name for the file."""
    local_path: Optional[Path] = None
    """Local path to the file if present on the current filesystem."""
    uri: Optional[str] = None
    """Unique Resource Identifier (URI) for the file, if applicable. Could be a URL."""
    id: Optional[str | ID_str] = None
    """ID under which this file is registered and retrievable."""
    checksum: Optional[str] = None
    """Checksum of the file for integrity verification."""
    silo_type: Optional[Type[Silo]] = None
    """Suggested type of Silo."""
    silo_id: Optional[str] = None
    """ID of the Silo when one has been instantiated for this file."""
    timeline_id: Optional[str] = None
    """ID of the Timeline associated with this file, if applicable."""

    @property
    def fname(self) -> Optional[str]:
        if self.local_path is not None:
            return self.local_path.name

    @property
    def fext(self) -> Optional[str]:
        """File extension of the local path, if available."""
        if self.local_path is not None:
            return self.local_path.suffix.lower()
        return None

    @property
    def local_directory(self) -> Optional[Path]:
        """Directory of the local path, if available."""
        if self.local_path is not None:
            return self.local_path.parent
        return None

    @property
    def has_silo(self) -> bool:
        """Check if a silo has been instantiated for this file."""
        return self.silo_id is not None

    @classmethod
    def from_path(
        cls,
        local_path: Path | str,
        id_prefix: Optional[str] = "file",
        uid: Optional[str] = None,
        **kwargs,
    ):
        """Create a File instance from a file path."""
        if isinstance(local_path, str):
            local_path = Path(local_path)
        if not local_path.is_file():
            if local_path.is_dir():
                raise FileNotFoundError(
                    f"Expected a file, but got a directory: {local_path}"
                )
            raise FileNotFoundError(f"File not found: {local_path}")
        self = cls(
            name=local_path.stem,
            local_path=local_path,
            checksum=utils.calculate_file_checksum(local_path),
            **kwargs,
        )
        if id_prefix is not None:
            self.id = ensure_registration(self, id_prefix=id_prefix, uid=uid)
        return self

    def get_silo(
        self,
    ) -> Optional[Silo]:
        """Get the silo associated with this file, if it has been instantiated."""
        if self.silo_id is None:
            return None
        return get_object_by_id(self.silo_id)

    def instantiate_silo(
        self, silo_type: Optional[Type[Silo]] = None, **kwargs
    ) -> Silo:
        """(Re-)instantiate an Silo for this file."""
        if silo_type is None:
            if self.silo_type is not None:
                raise ValueError(
                    "No silo type specified for instantiation. "
                    "Please provide a valid Silo subclass."
                )
            silo_type = self.silo_type
        else:
            if not issubclass(silo_type, Silo):
                raise TypeError(f"Expected a subclass of Silo, got {silo_type}.")
            self.silo_type = silo_type
        silo = silo_type.from_filepath(
            self.local_path,
            id_prefix=f"{self.id}/silo",
            **kwargs,
        )
        self.silo_id = silo.id
        return silo

    def make_timeline(
        self,
    ) -> Timeline:
        silo = self.get_silo()
        if silo is None:
            raise ValueError(
                f"No silo instantiated for {self!r}. Cannot create a timeline."
            )
        tl = silo.make_timeline()
        self.timeline_id = tl.id
        return tl

    def __repr__(self):
        info_str = "File("
        if self.name:
            info_str += f"name={self.name!r}, "
        elif self.uri:
            info_str += f"uri={self.uri!r}, "
        elif self.fname:
            info_str += f"fname={self.fname!r}, "
        info_str += f"checksum={self.checksum!r})"
        return info_str


ST = TypeVar("ST")  # source type; currently always File


class Representation(NamedSources[ST], RegisteredObject, Generic[ST]):
    pass


class FileCollection(Representation[File]):
    _allowed_extensions: Optional[tuple[str, ...]] = None
    """If this class attribute is set, only files with the enumerated extensions will be allowed as sources.
    Every extension needs to start with a dot, e.g. (".mid", ".midi"). If set to None, no restrictions are applied.
    """
    _default_silo_types: dict[Optional[str], Type[Silo]] = {None: None}
    """Mapping of file extensions to Silo types. The None key is used for the default type."""

    @classmethod
    def from_filepaths(
        cls,
        filepaths: Iterable[Path | str] | Path | str,
        create_silos: Optional[bool | Type[Silo] | Iterable[Type[Silo]]] = None,
    ) -> Self:
        self = cls()
        for path in utils.make_argument_iterable(filepaths):
            self.add_sources(File.from_path(path))
        return self

    @classmethod
    def from_directory(
        cls,
        directory: Path | str,
        create_silos: Optional[bool | Type[Silo] | Iterable[Type[Silo]]] = None,
    ) -> Self:
        self = cls()
        if isinstance(directory, str):
            directory = Path(directory)
        if not self.allowed_extensions:
            filepaths = directory.glob("*")
        else:
            extensions = self.allowed_extensions
            filepaths = [
                p
                for p in directory.iterdir()
                if p.is_file() and p.suffix.lower() in extensions
            ]
        self.add_sources(sources=filepaths, create_silos=create_silos)
        return self

    def __init__(
        self,
        *,
        silo_types: Optional[dict[Optional[str], Type[Silo]]] = None,
        id_prefix: str,
        uid: Optional[str] = None,
    ):
        super().__init__(id_prefix=id_prefix, uid=uid)
        self._silo_types: dict[Optional[str], Type[Silo]] = {}
        self.silo_types = silo_types
        self._timelines = {}
        self._silo_default_timelines: dict[str | int, str] = {}
        """Mapping a key to the ID of the default timeline for the respective silo, once it has been added."""
        self._spine_id = None
        self._sources: dict[int | str, File] = {}
        """Currently only local files are supported as sources. They can be added with or without a
        name. In the latter case, a key will be assigned based on the order of addition."""
        self._checksums = {}

    @property
    def allowed_extensions(self) -> tuple[str, ...]:
        """Allowed file extensions for this collection."""
        if self._allowed_extensions is None:
            return tuple()
        return tuple(
            "." + ext.lower().strip(".")
            for ext in utils.make_argument_iterable(self._allowed_extensions)
        )

    @property
    def silo_types(self) -> dict[Optional[str], Type[Silo]]:
        """Mapping of file extensions to Silo types."""
        return self._silo_types

    @silo_types.setter
    def silo_types(self, value: Optional[dict[Optional[str], Type[Silo]]]):
        if value is None:
            self._silo_types = self._default_silo_types.copy()
        elif isinstance(value, dict):
            for key, val in value.items():
                if key is not None and not isinstance(key, str):
                    raise TypeError(f"Expected a string key for silo type, got {key}.")
                if not isinstance(val, type) or not issubclass(val, Silo):
                    raise TypeError(f"Expected a subclass of Silo, got {val}.")
                self._silo_types[key] = val
        else:
            raise TypeError(f"Expected a dict of silo types, got {type(value)}.")

    def __repr__(self):
        info_str = (
            f"{self.class_name}("
            f"id={self.id!r}, "
            f"n_timelines={self.n_timelines})"
            f"spine={self._spine_id!r}, "
            f"n_sources={self.n_sources}"
        )
        if self.n_sources > 0:
            info_str += pformat(self._sources, indent=4, width=80)
        info_str += ")"
        return info_str

    @property
    def n_timelines(self):
        return len(self._timelines)

    @property
    def n_silos(self):
        return sum(f.has_silo for f in self.iter_sources())

    @property
    def n_sources(self):
        return len(self._sources)

    def add_timeline(self, timeline: Timeline):
        """The first timeline added is treated as the spine."""
        self._timelines[timeline.id] = timeline
        if self.n_timelines == 1:
            self._spine_id = timeline.id

    def update_default_timelines(
        self,
        keys: Iterable[str | int | Path] | str | int | Path = None,
    ):
        """Retrieve default timelines from the silos associated with the given keys and add them
        to the representation. This does not instantiate new silos nor re-generate once generated
        default timelines.
        """
        for key, source in self.iter_sources(keys, as_tuples=True):
            if key in self._silo_default_timelines:
                # Timeline already added for this silo
                continue
            if not source.has_silo:
                warnings.warn(
                    f"No silo instantiated for {source!r}. Skipping default timeline retrieval."
                )
                continue
            timeline = source.make_timeline()
            self.add_timeline(timeline)
            self._silo_default_timelines[key] = timeline.id
        if len(self._silo_default_timelines) == 0:
            warnings.warn(
                f"No default timelines were created. Probably, no silo types were "
                f"associated with the sources in {self.class_name} {self.id!r}."
            )

    def get_default_timelines(
        self, keys: Iterable[str | int] | str | int = None
    ) -> dict[str | int, Timeline]:
        """Retrieve default timelines from the silos associated with the given keys."""
        keys = self.resolve_keys(keys)
        self.update_default_timelines(keys=keys)
        if self.n_timelines == 0:
            raise ValueError(
                f"No default timelines available for {self.class_name} {self.id!r}. "
                "Probably none of the sources is associated with a silo type."
            )
        return {key: self._timelines[self._silo_default_timelines[key]] for key in keys}

    def get_key(self, key_or_path: str | int | Path) -> int | str:
        """Get the key for a given source path or key. If the key is not found, it raises KeyError."""
        try:
            return super().get_key(key_or_path)
        except KeyError:
            for key, file in self._sources.items():
                if file.local_path == key_or_path:
                    return key
            raise KeyError(f"Source {key_or_path!r} not found in sources.")

    def _add_silo(self, key: str | int | Path, silo: Silo):
        """Add a silo to the representation. If the silo already exists, it will be replaced."""
        source = self.get_source(key)
        if source.has_silo:
            warnings.warn(
                f"{source!r} already was associated with {source.silo_id}. The reference "
                f"has been replaced with {silo.id}.",
            )
        source.silo_id = silo.id

    def _make_silo(self, key: str | int | Path, silo_type: Optional[Type[Silo]] = None):
        source = self.get_source(key)
        source.instantiate_silo(silo_type=silo_type, id_prefix=f"{self.id}/silo")

    def get_silos(self, keys: Iterable[str] | str | int) -> list[Silo]:
        """Get the silos for the given keys or for all sources."""
        silos = []
        for source in self.iter_sources(keys):
            if source.has_silo:
                silos.append(source.get_silo())
        return silos

    def get_source(self, key: str | int | Path):
        if isinstance(key, Path):
            return self.get_source_by_path(key)
        return super().get_source(key)

    def get_source_by_path(self, path: Path | str) -> File:
        """Get a source by its local path. If the path is not found, it raises KeyError."""
        if isinstance(path, str):
            path = Path(path)
        for k, file in self._sources.items():
            if file.local_path == path:
                return file
        raise KeyError(f"None of the source files corresponds to the path {path!r}.")

    def get_spine(self) -> Timeline:
        if self.n_timelines == 0:
            self.update_default_timelines()
        if self._spine_id is None:
            raise ValueError(
                f"No spine timeline set for {self.class_name} {self.id!r}. "
                "Please set a spine using set_spine() or add a timeline."
            )
        return self._timelines[self._spine_id]

    def iter_sources(
        self,
        keys: Optional[Iterable[str | int] | str | int] = None,
        as_tuples: bool = False,
    ) -> Iterable[File] | Iterable[tuple[str | int, File]]:
        """Iterate over all sources in the collection."""
        if keys is None:
            if as_tuples:
                yield from self._sources.items()
            else:
                yield from self._sources.values()
        else:
            for key in self.resolve_keys(keys):
                yield key, self.get_source(key) if as_tuples else self.get_source(key)

    def set_spine(self, timeline: str | Timeline):
        if isinstance(timeline, str):
            timeline_id = timeline
            if timeline_id not in self._timelines:
                timeline = get_object_by_id(timeline_id)
                self.add_timeline(timeline)
        else:
            timeline_id = timeline.id
            if timeline_id not in self._timelines:
                self.add_timeline(timeline)
        self._spine_id = timeline_id

    def add_sources(
        self,
        sources: Iterable[File | Path | str] | File | Path | str,
        create_silos: bool | Type[Silo] | Iterable[Type[Silo]] = None,
    ):
        """For now assuming that sources are local files. All sources can be retrieved by their
        index (order of addition) or, if assigned, by their name using the get_source() and
        get_sources() methods.
        """
        for source in utils.make_argument_iterable(sources):
            self._add_source(source, create_silo=create_silos)

    def _add_source(
        self,
        source: File,
        name: Optional[str] = None,
        create_silo: Optional[bool | Type[Silo]] = None,
        **kwargs,
    ):
        new_key = super()._add_source(source=source, name=name)
        self.logger.debug(
            f"Added source {name!r} = {source!r} to {self.class_name} {self.id!r}"
        )
        if create_silo is False:
            return
        source = self.get_source(new_key)
        if create_silo is None or create_silo is True:
            if source.silo_type is not None:
                create_with_type = source.silo_type
            elif create_silo is True:
                raise ValueError(
                    f"No silo type specified for source {source.local_path!r} "
                    f"and no default type available in {self.class_name} {self.id!r}."
                )
            else:
                return  # if None and no default silo class (neither Repr. nor File): do nothing
        elif isinstance(create_silo, type) and issubclass(create_silo, Silo):
            create_with_type = create_silo
        else:
            raise TypeError(
                f"Expected boolean or a subclass of Silo for create_silo, got {create_silo}."
            )
        silo = source.instantiate_silo(create_with_type, **kwargs)
        self.logger.info(f"Created silo {silo.id!r} for source {source!r}")

    def get_silo_type(self, key: Optional[str | int] = None) -> Type[Silo]:
        """Get the silo type for a given source key or path. If key is None, returns the default silo type."""
        file = self.get_source(key)
        return file.silo_type

    def _adapt_source(self, source: File | Path | str) -> File:
        if isinstance(source, (Path, str)):
            source = File.from_path(source, id_prefix=f"{self.id}/file")
        if isinstance(source, File):
            if source.silo_type is None:
                if source.fext is not None and source.fext in self._silo_types:
                    source.silo_type = self._silo_types[source.fext]
                elif None in self._silo_types:
                    source.silo_type = self._silo_types[None]
            return source
        raise TypeError(f"Expected a File, Path, or str, got {type(source)}.")

    def validate_source(self, source: File):
        """Should raise when a source is not valid."""
        return


class GraphicalRepresentation(FileCollection):

    def __init__(
        self,
        silo_types: Optional[dict[Optional[str], Type[Silo]]] = None,
        id_prefix: str = "gr",
        uid: Optional[str] = None,
    ):
        super().__init__(silo_types=silo_types, id_prefix=id_prefix, uid=uid)


class LogicalRepresentation(FileCollection):

    def __init__(
        self,
        silo_types: Optional[dict[Optional[str], Type[Silo]]] = None,
        id_prefix: str = "mu",
        uid: Optional[str] = None,
    ):
        super().__init__(silo_types=silo_types, id_prefix=id_prefix, uid=uid)


class PhysicalRepresentation(FileCollection):

    def __init__(
        self,
        silo_types: Optional[dict[Optional[str], Type[Silo]]] = None,
        id_prefix: str = "ph",
        uid: Optional[str] = None,
    ):
        super().__init__(silo_types=silo_types, id_prefix=id_prefix, uid=uid)


class AlignmentRepresentation(FileCollection):

    def __init__(
        self,
        silo_types: Optional[dict[Optional[str], Type[Silo]]] = None,
        id_prefix: str = "al",
        uid: Optional[str] = None,
    ):
        super().__init__(silo_types=silo_types, id_prefix=id_prefix, uid=uid)


class MatchfileRepresentation(AlignmentRepresentation):
    _allowed_extensions = (".match",)
    _default_silo_types = {None: PartituraScoreSilo}


class MidiRepresentation(LogicalRepresentation):
    _allowed_extensions = (".mid", ".midi")
    _default_silo_types = {None: MidiDataFrameSilo}


class AudioRepresentation(PhysicalRepresentation):
    _default_silo_types = {None: AudioSilo}


# region to be refactored


@dataclass
class EmbeddedImage:
    """
    Represents information about an embedded image instance on a PDF page,
    as provided by an item in pymupdf's page.get_image_info() list.
    """

    number: int
    bbox: Rect | tuple[float, float, float, float]  # (x0, y0, x1, y1), in pt
    transform: (
        Matrix | tuple[float, float, float, float, float, float]
    )  # (x-scale, y-shear, x-shear, y-scale, x-shift, y-shift)
    width: int  # original image width
    height: int  # original image height
    colorspace: int  # colorspace.n
    cs_name: str  # colorspace name
    xres: int  # X resolution, in px
    yres: int  # Y resolution, in px
    bpc: int  # Bits per component
    size: int  # Size in bytes
    digest: bytes  # MD5 hashcode
    has_mask: bool  # whether the image is transparent and has a mask
    xref: int  # The cross-reference number of the image object
    page_index: int
    page_width: float  # measured in points
    page_height: float  # measured in points
    filename: Optional[str] = None
    filepath: Optional[str] = None

    def __post_init__(self):
        self.bbox = Rect(self.bbox)
        self.transform = Matrix(self.transform)

    @property
    def inverse_transform(self) -> Optional[Matrix]:
        result = Matrix(self.transform)
        degenerate_matrix = result.invert()  # mutates
        if degenerate_matrix:
            return None
        return result

    def get_image_rect(self):
        return Rect(0, 0, self.width, self.height)

    def image_pixel_to_page_point(
        self,
        bbox_pixels: Rect,
    ):
        """Transform a bounding box (px) within the image to a bounding box (pt) on the PDF page."""
        shrink = Matrix(1 / self.width, 0, 0, 1 / self.height, 0, 0)
        return bbox_pixels * shrink * self.transform

    def page_point_to_image_pixel(
        self,
        bbox_page_points: Rect,
    ) -> Rect:
        """Transform a bounding box (pt) on the PDF page back to a bounding box (px) within the image."""
        expand = Matrix(self.width, 0, 0, self.height, 0, 0)
        return bbox_page_points * self.inverse_transform * expand


# class Orientation(FancyStrEnum):
#     horizontal = auto()
#     h = horizontal
#     vertical = auto()
#     v = vertical


# @dataclass
# class ImgSegment(Segment):
#     """
#     A segment comprises a time interval the dimensions of which are defined by two boundary
#     :class:`timestamps <Timestamp>`.
#     Its backbone is the spine which is an ordered sequence of :class:`timestamps <Timestamp>` which can correspond
#     to :class:`events <Event>`
#     """
#     name: str
#     unit: TimeUnit | str
#     img: EmbeddedImage
#     orientation: Orientation
#     start: Optional[Timestamp | VirtualCoordinate] = None
#     end: Optional[Timestamp | VirtualCoordinate] = None
#     origin: VirtualCoordinate = field(init=False)
#     # spine: Spine
#     # events: dict[ID_str, Segment]
#     ID: ID_str = field(init=False)
#
#     def __post_init__(self):
#         self.unit = TimeUnit(self.unit)
#         self.origin = VirtualCoordinate(0, self.unit)
#         self.ID = register_object(self.name, self)
#         self.orientation = Orientation(self.orientation)
#
#     def as_interval(self):
#         if self.start is None or self.end is None:
#             return
#         start, end = self.start.value, self.end.value
#         return pd.Interval(start, end, closed="left")
#
#     @property
#     def length(self):
#         rect = self.img.get_image_rect()
#         if self.orientation == Orientation.horizontal:
#             return Length(rect.width, "px")
#         return Length(rect.height, "px")


class PdfFile(GraphicalRepresentation):

    def __init__(
        self, doc: pymupdf.Document, id_prefix: str = "gr", uid: Optional[str] = None
    ):
        assert isinstance(
            doc, pymupdf.Document
        ), f"Expected PDF document, got {type(doc)}"
        super().__init__(id_prefix=id_prefix, uid=uid)
        self.doc = doc
        self.images = get_images_embedded_in_document(doc)

    #
    # def append_segment(
    #         self,
    #         segment: ImgSegment
    # ):
    #     self.segments[segment.ID] = segment
    #     self.spine.append_segment(segment)
    #
    # def define_and_append_new_segment(
    #         self,
    #         page_index: int,
    #         image_index: int,
    #         crop_px: Optional[Rect] = None,
    #         orientation: Orientation | str = Orientation.horizontal,
    #         name: Optional[str] = None,
    #         store_in: Optional[str] = None
    # ) -> ImgSegment:
    #     """Combination of .define_new_segment() and .append_segment()"""
    #     segment = self.define_new_segment(page_index, image_index, crop_px, orientation, name, store_in)
    #     self.append_segment(segment)
    #
    # def define_new_segment(
    #         self,
    #         page_index: int,
    #         image_index: int,
    #         crop_px: Optional[Rect] = None,
    #         orientation: Orientation | str = Orientation.horizontal,
    #         name: Optional[str] = None,
    #         store_in: Optional[str] = None
    # ) -> ImgSegment:
    #     if not name:
    #         name = f"{self.name}_ImgSegment"
    #     img = self.images[page_index][image_index]
    #     img_rect = img.get_image_rect()
    #     if crop_px:
    #         crop_px = Rect(crop_px)
    #         assert img_rect.contains(
    #             crop_px
    #         ), (f"The crop box {crop_px} is not fully contained by "
    #            f"image[{page_index}][{image_index}] ({img.width}px × {img.height}px)")
    #         pix, new_img = get_cropped_pix(self.doc, img, crop_px)
    #     else:
    #         pix = get_pixmap(self.doc, img.xref)
    #         new_img = copy_dataclass(img)
    #     segment = ImgSegment(name=name, unit="px", img=new_img, orientation=orientation)
    #     if store_in:
    #         segment.img.filename = segment.ID + ".png"
    #         segment.img.filepath = osp.join(store_in, segment.img.filename)
    #         pix.save(segment.img.filepath)
    #         print(f"Stored {segment.img.filename}")
    #         del (pix)
    #     return segment
    #
    # def get_text(self, option) -> Dict[int, Any]:
    #     result = {}
    #     for page_index, page in self.iter_pages():
    #         result[page_index] = page.get_text(option)
    #     return result
    #
    # def get_words(self):
    #     dataframes = {}
    #     for page_index, page in self.iter_pages():
    #         words = pd.DataFrame(
    #             page.get_text("words"), columns=["x0", "y0", "x1", "y1", "word", "block_no", "line_no", "word_no"]
    #             )
    #         dataframes[page_index] = words
    #     return pd.concat(dataframes, names=["page", "ix"]).reset_index().drop(columns="ix")
    #
    # def iter_pages(self) -> Iterator[tuple[int, pymupdf.Page]]:
    #     yield from enumerate(self.doc)


def get_images_embedded_in_page(page: Page) -> list[EmbeddedImage]:
    width = page.rect.width
    height = page.rect.height
    image_info_list = page.get_image_info(xrefs=True)
    result = []
    for image_index, image_info in enumerate(
        image_info_list, start=1
    ):  # enumerate the image list
        image_info["cs_name"] = image_info.pop("cs-name")  #
        image_info["has_mask"] = image_info.pop("has-mask")
        img = EmbeddedImage(
            **image_info, page_index=page.number, page_width=width, page_height=height
        )
        result.append(img)
    return result


def get_images_embedded_in_document(
    doc: Document | str,
) -> Dict[int, list[EmbeddedImage]]:
    result = {}
    for idx, page in enumerate(doc):
        result[idx] = get_images_embedded_in_page(page)
    return result


def get_pixmap(doc: Document, xref: int) -> Pixmap:
    pix = Pixmap(doc, xref)  # create a Pixmap
    if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
        pix = Pixmap(csRGB, pix)
    return pix


def store_embedded_image(
    doc: Document | str,
    xref: int,
    filepath: str,
):
    pix = get_pixmap(doc, xref)
    pix.save(filepath)
    logger.info(f"Stored {filepath}")


def update_img_from_cropped_pix(img, pix, crop_px, **kwargs):
    new_bbox = img.image_pixel_to_page_point(crop_px)
    return copy_dataclass(
        img,
        bbox=new_bbox,
        width=crop_px.width,
        height=crop_px.height,
        size=pix.size,
        digest=pix.digest,
        **kwargs,
    )


def crop_pixmap(
    pix: Pixmap, crop_px: Rect, img: EmbeddedImage, **kwargs
) -> tuple[Pixmap, EmbeddedImage]:
    crop_px = Rect(crop_px)
    cropped_pix = Pixmap(pix, img.width, img.height, crop_px)
    new_img = update_img_from_cropped_pix(img, cropped_pix, crop_px, **kwargs)
    return cropped_pix, new_img


def store_image(
    doc: Document | str,
    img: EmbeddedImage,
    filepath: str,
    crop_px: Optional[Rect] = None,
) -> EmbeddedImage:
    filename = osp.basename(filepath)
    pix = get_pixmap(doc, xref=img.xref)
    if crop_px is not None:
        pix, new_img = crop_pixmap(pix, crop_px, img, filename, filepath)
    else:
        new_img = copy_dataclass(
            img,
            filename=filename,
            filepath=filepath,
        )
    pix.save(filepath)
    del pix
    logger.info(f"Stored {filepath}")
    return new_img


def get_cropped_pix(
    doc: Document | str, img: EmbeddedImage, crop_px: Optional[Rect] = None, **kwargs
) -> tuple[Pixmap, EmbeddedImage]:
    pix = get_pixmap(doc, xref=img.xref)
    return crop_pixmap(pix, crop_px, img, **kwargs)


# endregion to be refactored

if __name__ == "__main__":
    filepath = get_specimen_path("supra_rolls", "midi", "fd660zf8362_exp.mid")
    midi_file = MidiRepresentation.from_filepaths(filepath)
    print(midi_file)
