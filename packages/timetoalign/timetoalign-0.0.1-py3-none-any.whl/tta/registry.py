from __future__ import annotations

import re
import warnings
from functools import cache
from numbers import Number
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Hashable,
    Iterator,
    Optional,
    Type,
    TypeVar,
    Union,
)

import numpy as np
import pandas as pd

from processing.tta import utils

if TYPE_CHECKING:
    from .common import RegisteredObject
    from .conversions import ConversionMap
    from .utils import NumberType, TimeUnit


class ID_str(str):
    def __new__(cls, content: str, uid: Optional[Hashable] = None):
        instance = super().__new__(cls, content)
        instance.uid = uid
        return instance


# region Base Registry

_R = TypeVar("_R")  # Type variable for the items stored in the registry


class Registry(Generic[_R]):
    """
    A generic registry for storing and retrieving items by a hashable key.
    """

    def __init__(self):
        self._objects: Dict[Hashable, _R] = {}

    def register(self, key: Hashable, obj_instance: _R) -> _R:
        """
        Registers an item with the given key.
        Warns if overwriting an existing key.
        """
        if key in self._objects:
            warnings.warn(
                f"Object with key {key!r} already registered in this registry."
            )
        self._objects[key] = obj_instance
        return obj_instance

    def get(self, key: Hashable, default=None) -> Optional[_R]:
        """Retrieves an item by its key."""
        return self._objects.get(key, default)

    def unregister(self, key: Hashable) -> Optional[_R]:
        """Removes and returns an item by its key, or None if not found."""
        return self._objects.pop(key, None)

    def __contains__(self, key: Hashable) -> bool:
        return key in self._objects

    def __len__(self) -> int:
        return len(self._objects)

    def all_items(self) -> Dict[Hashable, _R]:
        """Returns a copy of all items in the registry."""
        return dict(self._objects)


# endregion Base Registry


# region ClassRegistry
class ClassRegistry(Registry[Type["RegisteredObject"]]):
    pass


CLASS_REGISTRY = ClassRegistry()


def get_class(class_name: str | Type["RegisteredObject"]) -> Type["RegisteredObject"]:
    if isinstance(class_name, type):
        if class_name.__name__ not in CLASS_REGISTRY:
            raise ValueError(f"Class {class_name.__name__} is not registered.")
        return class_name
    if not isinstance(class_name, str):
        raise ValueError(
            f"Classes are registered with their names as keys. Expected a string, got {type(class_name)}"
        )
    return CLASS_REGISTRY.get(class_name)


def register_class(cls):
    CLASS_REGISTRY.register(cls.__name__, cls)


# endregion ClassRegistry

# region ObjectRegistry


class PrefixRegistry(Registry["RegisteredObject"]):
    """
    Manages the creation, storage, and retrieval of objects with unique IDs,
    typically objects that self-register using a specific id_prefix. New IDs are generated
    incrementally, the number format can be controlled by passing number_format to the constructor
    which needs to be a valid f-string format (e.g. "04" for padding four-or-less digit numbers
    with leading zeros)
    """

    def __init__(
        self,
        type_prefix: str,
        number_format: str = "",
    ):
        """The number_format argument will be used in an f-string to format the number.
        For example, pass number_format="04" to pad four-or-less digit numbers with leading zeros.
        """
        super().__init__()
        self._type_prefix = type_prefix
        self._counter = 0
        self._number_format = number_format

    def current_number(self, as_string=True) -> Union[str, int]:
        if as_string:
            return f"{self._counter:{self._number_format}}"
        return self._counter

    def next_number(self, as_string=True) -> Union[str, int]:
        self._counter += 1
        return self.current_number(as_string=as_string)

    def _generate_id(
        self,
        description: Optional[str] = None,
        uid: Optional[Hashable] = None,
    ) -> ID_str:
        """Generates a unique ID string based on prefix, counter, and description."""
        # Determine the numeric part of the ID using the counter
        numeric_part_of_id = self.next_number(as_string=True)
        id_string = f"{self._type_prefix}{numeric_part_of_id}"

        if description:
            sane_description = "".join(
                c if (c.isalnum() or c == "_") else "_" for c in str(description)
            ).strip("_")
            if sane_description:
                id_string += "_" + sane_description
        return ID_str(id_string, uid=uid)

    def create_and_register(
        self, cls, description: str = "", uid: Optional[Hashable] = None, **kwargs
    ):
        """
        Creates an instance of 'cls', assigns a unique ID, registers it,
        and returns the instance.
        'cls' __init__ method must accept 'obj_id' as its first argument after self.
        'description' is used for the descriptive part of the ID.
        Other kwargs are passed to the cls constructor.
        """
        obj_id = self._generate_id(description=description, uid=uid)
        # The class's __init__ must be prepared to accept obj_id
        instance = cls(id_prefix=self._type_prefix, uid=uid, **kwargs)
        if obj_id in self._objects:
            # This should ideally not happen if _generate_id is robust
            raise ValueError(
                f"Critical error: Duplicate ID {obj_id} generated for {self._type_prefix}."
            )
        self._objects[obj_id] = instance
        return instance

    def get(self, obj_id: str) -> Optional[Any]:
        return super().get(obj_id)

    def register_existing(self, obj_instance: Any, _key: Optional[str] = None) -> Any:
        """Registers an externally created object that already has an ID."""
        if _key is None:
            if not hasattr(obj_instance, "id") or obj_instance.id is None:
                raise ValueError("Object must have an ID to be registered.")

            obj_id_str = str(obj_instance.id)  # Ensure it's a string for startswith

        else:
            # _key should only be used for external objects
            obj_id_str = _key

        if not obj_id_str.startswith(self._type_prefix):
            raise ValueError(
                f"Object ID '{obj_id_str}' does not match registry prefix '{self._type_prefix}'"
            )

        super().register(obj_id_str, obj_instance)

        # Try to update counter if a manually registered ID has a higher sequence
        # ID format is "{id_prefix}{int_counter}[_optional_arbitrary_description]"
        # Escape the prefix in case it contains special regex characters
        escaped_prefix = re.escape(self._type_prefix)
        pattern = rf"^{escaped_prefix}(\d+)(?:_.*)?$"

        match = re.match(pattern, obj_id_str)
        if match:
            num_str = match.group(1)  # Get the captured digits
            seq = int(num_str)
            if seq > self._counter:
                self._counter = seq
        return obj_instance


REGISTRY: Dict[str, PrefixRegistry] = {}


def get_registry_by_prefix(prefix: str) -> PrefixRegistry:
    if prefix not in REGISTRY:
        REGISTRY[prefix] = PrefixRegistry(type_prefix=prefix)
    return REGISTRY[prefix]


@cache
def get_object_by_id(obj_id: str) -> Any:
    """Retrieves an object by its ID from any known ObjectRegistry."""
    for registry_instance in REGISTRY.values():
        if (obj := registry_instance.get(obj_id)) is not None:
            return obj
    raise KeyError(f"Object with ID '{obj_id}' not found in any registry.")


@cache
def id_is_registered(obj_id: str) -> Any:
    """Returns true if obj_id is registered in any ObjectRegistry."""
    for registry_instance in REGISTRY.values():
        if registry_instance.get(obj_id) is not None:
            return True
    return False


def iter_objects_by_ids(*obj_ids: str) -> Iterator["RegisteredObject"]:
    obj_ids = utils.treat_variadic_argument(obj_ids)
    for obj_id in obj_ids:
        yield get_object_by_id(obj_id)


def register_object(
    obj: Any,
    id_prefix: str,
    uid: Optional[Hashable] = None,
    description: Optional[str] = None,
) -> Any:  # Return the object itself
    """
    Assigns an ID to an object and registers it in the appropriate registry.
    The object's 'id' attribute will be set.
    """
    reg = get_registry_by_prefix(id_prefix)
    obj._id = reg._generate_id(uid=uid, description=description)
    reg.register_existing(obj)  # This uses obj.id as the key
    return obj


def ensure_registration(
    obj: Any,
    id_prefix: Optional[str] = None,
    uid: Optional[Hashable] = None,
    description: Optional[str] = None,
) -> str:
    """This makes sure that the object is part of a registry and can be retrieved via an id.
    For internal objects (:class:`RegisteredObject`) this returns simply the id. External objects
    are added to a registry according to their class name and a new ID is returned.
    """
    if (existing_id := getattr(obj, "id", None)) is not None:
        if id_is_registered(existing_id):
            return existing_id
    if id_prefix is not None:
        reg = get_registry_by_prefix(id_prefix)
    else:
        reg = get_registry_by_prefix(obj.__class__.__name__)
    if existing_id is None:
        obj_id = reg._generate_id(uid=uid, description=description)
    else:
        obj_id = existing_id
    reg.register_existing(obj, _key=obj_id)
    return obj_id


# endregion ObjectRegistry

# region CoordinatesMapRegistry


class CoordinatesMapRegistry(Registry["CoordinatesMap"]):
    """
    Manages CoordinatesMap instances, keyed by (source_type_key, target_type_key).
    """

    def __init__(self):
        super().__init__()
        self._get_coordinate_type_func_cache: Optional[Callable] = None

    def _get_coordinate_type_loader(self) -> Callable:
        """Helper to load get_coordinate_type lazily to avoid import issues."""
        if self._get_coordinate_type_func_cache is None:
            from processing.tta.conversions import get_coordinate_type

            self._get_coordinate_type_func_cache = get_coordinate_type
        return self._get_coordinate_type_func_cache

    def make_key_for_map(self, cmap: "ConversionMap") -> tuple:
        return (
            cmap._source_unit,
            cmap._target_unit,
            cmap._target_type,
            cmap._custom_conversion_function,
        )

    def register_map(self, cmap: "ConversionMap"):
        """Registers a CoordinatesMap instance.
        The key is derived from the map's source and target coordinate types.
        """
        # CoordinatesMap must have source_coordinate_type and target_coordinate_type properties
        key = self.make_key_for_map(cmap)
        if key in self._objects:
            return
        super().register(key, cmap)

    def get_map(
        self,
        source_unit: TimeUnit,
        target_unit: TimeUnit,
        target_type: Optional[NumberType] = None,
        converter_func: Optional[
            Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
        ] = None,
    ) -> Optional["ConversionMap"]:
        """
        Retrieves a CoordinatesMap instance based on source and target coordinate types.
        """
        key = (source_unit, target_unit, target_type, converter_func)
        super().get(key)


CMAP_REGISTRY = CoordinatesMapRegistry()


def register_cmap(cmap: "ConversionMap"):
    CMAP_REGISTRY.register_map(cmap)


def get_cmap(
    source_unit: TimeUnit,
    target_unit: TimeUnit,
    target_type: Optional[NumberType] = None,
    converter_func: Optional[
        Callable[[Union[Number, np.ndarray]], Union[Number, np.ndarray]]
    ] = None,
) -> "ConversionMap":
    return CMAP_REGISTRY.get_map(
        source_unit=source_unit,
        target_unit=target_unit,
        target_type=target_type,
        converter_func=converter_func,
    )


# endregion CoordinatesMapRegistry


# region flyweight


@cache
def get_property_defaults(cls):
    class_property_defaults = getattr(cls, "_property_defaults", {})
    if class_property_defaults is None:
        class_property_defaults = {}
    elif not isinstance(class_property_defaults, dict):
        class_property_defaults = {field: None for field in class_property_defaults}
    return class_property_defaults


def get_property_values(
    self,
    include_shared=True,
    include_individual=True,
    exclude_properties: Optional[tuple[str]] = ("data",),
    **column2field,
) -> dict:
    """Returns a dictionary of property values for a flyweight object."""
    if exclude_properties is None:
        exclude_properties = []
    if include_shared:
        properties_dict = {
            k: v for k, v in self._shared.items() if k not in exclude_properties
        }
    else:
        properties_dict = {}
    if include_individual:
        for name in dir(self):
            if name.startswith("_") or name in exclude_properties:
                continue
            class_attribute = getattr(type(self), name, None)
            if isinstance(class_attribute, property):
                try:
                    value = getattr(self, name)
                    properties_dict[name] = value
                except AttributeError:
                    properties_dict[name] = None
                except Exception as e:
                    properties_dict[name] = f"Error accessing property: {e}"
    for column, field in column2field.items():
        properties_dict[column] = self.get(field)
    return properties_dict


def flyweight(**decorator_defaults):
    """Class decorator that lets you define the parameters (and their default values) that are to be
    shared among all instances for which they have the same value configuration. The shared
    values are accessible via the ._shared dict. Shared fields can be defined via decorator
    arguments or a '_property_defaults' class attribute.

    Conflict Resolution: Decorator arguments take precedence over class attribute defaults.

    Example:

        # Defining shared fields via decorator
        @flyweight(data=None)
        class Decorated:
            def __init__(self):
                pass

            @property
            def data(self):
                return self._shared['data']

        # Defining shared fields via class attribute (decorator wins)

        @flyweight(value='decorator_value', another='decorator_another')
        class WithClassAttributes:
            _property_defaults = {'value': 'class_attribute_value', 'default_only': 'only_from_class'}

            def __init__(self):
                pass

            @property
            def value(self):
                return self._shared['value']

            @property
            def another(self):
                return self._shared['another']

            @property
            def default_only(self):
                return self._shared['default_only']

    """

    def decorator(cls):
        _original_new = cls.__new__
        _original_init = (
            cls.__init__
            if hasattr(cls, "__init__") and cls.__init__ is not object.__init__
            else None
        )

        _shared_dict_cache = {}

        # Combining _property_defaults class attributes from all base classes in the MRO
        combined_property_defaults = {}
        for base_class in cls.__mro__:
            class_defaults = get_property_defaults(base_class)
            combined_property_defaults.update(class_defaults)

        shared_params_defaults = dict(
            combined_property_defaults
        )  # start with class attributes
        shared_params_defaults.update(
            decorator_defaults
        )  # update (override) with decorator defaults

        def __new__(cls, *args, **kwargs):
            shared_kwargs_for_key = {
                k: kwargs.get(k, shared_params_defaults.get(k))
                for k in shared_params_defaults
            }

            hashable_key_parts = []
            for k, v in sorted(shared_kwargs_for_key.items()):
                # Special handling for unhashable types
                if isinstance(v, (list, dict, set, pd.DataFrame, bytearray)):
                    hashable_key_parts.append((k, id(v)))
                else:
                    hashable_key_parts.append((k, v))

            shared_key = tuple(hashable_key_parts)

            if shared_key not in _shared_dict_cache:
                _shared_dict = {}
                for k, v in shared_kwargs_for_key.items():
                    _shared_dict[k] = v
                _shared_dict_cache[shared_key] = _shared_dict

            cached_shared_dict = _shared_dict_cache[shared_key]
            setattr(
                cls, "get_property_values", get_property_values
            )  # Add get_property_values method to the class
            new_instance = _original_new(cls)
            new_instance._shared = cached_shared_dict
            return new_instance

        def __init__(self, *args, **kwargs):
            # Use the combined defaults here to remove shared parameters from kwargs
            for k in shared_params_defaults:
                if k in kwargs:
                    del kwargs[k]

            if _original_init:
                _original_init(self, *args, **kwargs)
            else:
                object.__init__(
                    self
                )  # Call original object __init__ if no custom one exists

        cls.shared_params_defaults = shared_params_defaults  # For introspection
        cls.__new__ = __new__
        cls.__init__ = __init__

        return cls

    return decorator


# endregion flyweight

if __name__ == "__main__":
    pass
