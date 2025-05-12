from __future__ import annotations

from django_tables2.utils import Accessor as tables2_Accessor

from collections.abc import Iterable, Mapping, Sequence
from typing import TypeAlias, Protocol, Any, Optional, TypeVar, Type

from django.db import models


AccessorContext: TypeAlias = object | Mapping[str, Any] | Sequence

# Any type that implements the protocol
AccessorType = TypeVar('AccessorType', bound='AccessorProtocol')

# An AccessorSpec allows an accessor to be specified by its string representation
AccessorSpec: TypeAlias = str | AccessorType


class AccessorProtocol(Protocol):
    """
    A string that describes how to resolve a value from an arbitrarily deeply nested object, dictionary, or sequence.
    E.g. hn.helpers.algorithms.Accessor implements this protocol

    Design note: this combines API for a generic Accessor with API for a more specific "ModelFieldAccessor"
    This violates SR principle a little, but keeps things simple and don't forsee any problems.
    """
    def __init__(self, value: str):
        """ Initialise the accessor with a string specifying the "path" used to resolve access to a value. """
        ...

    def resolve(self, context: AccessorContext) -> Any:
        """ Return the value of this accessor in the given context. """
        ...

    def get_field(self, model: models.Model | type[models.Model]) -> models.Field:
        """ Resolve this accessor using given model as context to return the model field rather than its value. """
        ...

    def get_label(self, model: models.Model | type[models.Model]) -> str:
        """ Resolve this accessor using given model as context to return the model field verbose name. """
        ...  # Note: this method is not defined on base tables2 Accessor, see extension below.


#####
# Accessor - cornerstone building block - defines how to resolve a value from a string description.
#####
class Accessor(tables2_Accessor):
    """
    A string describing a path from one object to another via attribute/index accesses.

    Relations are separated by a ``__`` character.

    Usage::

        >>> x = Accessor("__len__")
        >>> x.resolve("brad")
        4
        >>> x = Accessor("0__upper")
        >>> x.resolve("brad")
        "B"

    This class is a placeholder in case we want to eliminate dependency on tables2.
    While we have this dependency, why re-invent the wheel?
    """

    def get_label(self, model: models.Model | type[models.Model]) -> str:
        """ Resolve this accessor using given model as context to return the model field verbose name. """
        if isinstance(model, models.Model):
            model = type(model)
        field = self.get_field(model)
        if field and field.verbose_name:
            return field.verbose_name
        return self.bits[-1].replace("_", " ").title()


class AccessorTransform:
    """Provides a transform from standard accessor names to prefixed accessor names"""

    def __init__(self, prefix: str = None):
        self.prefix = prefix

    def t(self, accessor: str) -> str:
        """Transform key, if it exists in this KeyMap"""
        return f"{self.prefix}__{accessor}" if self.prefix else accessor

    def __call__(self, accessors: str | dict | Iterable) -> str | dict | list:
        """Transform all value(s) in accessors and return an object of the same type"""
        match accessors:
            case str():
                return self.t(accessors)
            case dict():
                return {self.t(accessor): value for accessor, value in accessors.items()}
            case _:
                return [self.t(accessor) for accessor in accessors]


def get_accessor(accessor: Optional[AccessorSpec], accessor_type: Type[AccessorType] = Accessor) -> AccessorType | None:
    """ helper: return an Accessor instance from the given spec.  Returns None if input accessor is None. """
    return accessor_type(accessor) if isinstance(accessor, str) else accessor
