import logging
from typing import Optional, Generic, TypeVar

from processing.tta.registry import register_object, register_class

D = TypeVar("D") # any data type

class RegisteredObject(Generic[D]):
    """
    Base class for objects that will be managed by an ObjectRegistry.
    """

    @classmethod
    @property
    def class_name(cls) -> str:
        return str(cls.__name__)

    @classmethod
    @property
    def logger(cls) -> logging.Logger:
        return logging.getLogger(cls.__module__ + '.' + cls.__name__)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        register_class(cls)


    def __init__(
            self,
            id_prefix: str,
            uid: Optional[str] = None,
            *args,
            **kwargs
    ):
        given_id = kwargs.pop("given_id", None)
        self._id: str = ""
        _ = register_object(  # assigns ID
            self,
            id_prefix=id_prefix,
            uid=uid,
            description=given_id
        )
        # super().__init__(*args, **kwargs)

    @property
    def id(self):
        return self._id

    def __repr__(self) -> str:
        return f"{self.class_name}(id={self.id!r})"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, RegisteredObject):
            return self.id == other.id
        return False