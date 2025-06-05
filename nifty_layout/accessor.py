from __future__ import annotations

import warnings
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Optional, Protocol, Type, TypeAlias, TypeVar

from django.core.exceptions import FieldDoesNotExist
from django.db import models

AccessorContext: TypeAlias = object | Mapping[str, Any] | Sequence

# Any type that implements the protocol
AccessorType = TypeVar("AccessorType", bound="AccessorProtocol")

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
        """Initialise the accessor with a string specifying the "path" used to resolve access to a value."""
        ...

    def resolve(self, context: AccessorContext) -> Any:
        """Return the value of this accessor in the given context."""
        ...

    def get_field(self, model: models.Model | type[models.Model]) -> models.Field:
        """Resolve this accessor using given model as context to return the model field rather than its value."""
        ...

    def get_label(self, model: models.Model | type[models.Model]) -> str:
        """Resolve this accessor using given model as context to return the model field verbose name."""
        ...  # Note: this method is not defined on base tables2 Accessor, see extension below.


#####
# BaseAccessor - copied directly from https://github.com/jieter/django-tables2/blob/master/django_tables2/utils.py
#    to avoid otherwise unnecessary dependency on `table2`, but you should use tables2 anyhow, its awesome !!
#    Licence:  https://github.com/jieter/django-tables2/blob/master/LICENSE
#####


class BaseAccessor(str):
    """
    A string describing a path from one object to another via attribute/index
    accesses. For convenience, the class has an alias `.A` to allow for more concise code.

    Relations are separated by a ``__`` character.

    To support list-of-dicts from ``QuerySet.values()``, if the context is a dictionary,
    and the accessor is a key in the dictionary, it is returned right away.
    """

    LEGACY_SEPARATOR = "."
    SEPARATOR = "__"

    ALTERS_DATA_ERROR_FMT = "Refusing to call {method}() because `.alters_data = True`"
    LOOKUP_ERROR_FMT = "Failed lookup for key [{key}] in {context}, when resolving the accessor {accessor}"

    def __init__(self, value, callable_args=None, callable_kwargs=None):
        self.callable_args = (
            callable_args or getattr(value, "callable_args", None) or []
        )
        self.callable_kwargs = (
            callable_kwargs or getattr(value, "callable_kwargs", None) or {}
        )
        super().__init__()

    def __new__(cls, value, callable_args=None, callable_kwargs=None):
        instance = super().__new__(cls, value)
        if cls.LEGACY_SEPARATOR in value:
            instance.SEPARATOR = cls.LEGACY_SEPARATOR

            message = (
                f"Use '__' to separate path components, not '.' in accessor '{value}'"
                " (fallback will be removed in django_tables2 version 3)."
            )

            warnings.warn(message, DeprecationWarning, stacklevel=3)

        return instance

    def resolve(self, context, safe=True, quiet=False):
        """
        Return an object described by the accessor by traversing the attributes of *context*.

        Lookups are attempted in the following order:

         - dictionary (e.g. ``obj[related]``)
         - attribute (e.g. ``obj.related``)
         - list-index lookup (e.g. ``obj[int(related)]``)

        Callable objects are called, and their result is used, before
        proceeding with the resolving.

        Example::

            >>> x = Accessor("__len__")
            >>> x.resolve("brad")
            4
            >>> x = Accessor("0__upper")
            >>> x.resolve("brad")
            "B"

        If the context is a dictionary and the accessor-value is a key in it,
        the value for that key is immediately returned::

            >>> x = Accessor("user__first_name")
            >>> x.resolve({"user__first_name": "brad"})
            "brad"


        Arguments:
            context : The root/first object to traverse.
            safe (bool): Don't call anything with `alters_data = True`
            quiet (bool): Smother all exceptions and instead return `None`

        Returns:
            target object

        Raises:
            TypeError`, `AttributeError`, `KeyError`, `ValueError`
            (unless `quiet` == `True`)
        """
        # Short-circuit if the context contains a key with the exact name of the accessor,
        # supporting list-of-dicts data returned from values_list("related_model__field")
        if isinstance(context, dict) and self in context:
            return context[self]

        try:
            current = context
            for bit in self.bits:
                try:  # dictionary lookup
                    current = current[bit]
                except (TypeError, AttributeError, KeyError):
                    try:  # attribute lookup
                        current = getattr(current, bit)
                    except (TypeError, AttributeError):
                        try:  # list-index lookup
                            current = current[int(bit)]
                        except (
                            IndexError,  # list index out of range
                            ValueError,  # invalid literal for int()
                            KeyError,  # dict without `int(bit)` key
                            TypeError,  # unsubscriptable object
                        ):
                            current_context = (
                                type(current)
                                if isinstance(current, models.Model)
                                else current
                            )

                            raise ValueError(
                                self.LOOKUP_ERROR_FMT.format(
                                    key=bit, context=current_context, accessor=self
                                )
                            )
                if callable(current):
                    if safe and getattr(current, "alters_data", False):
                        raise ValueError(
                            self.ALTERS_DATA_ERROR_FMT.format(method=current.__name__)
                        )
                    if not getattr(current, "do_not_call_in_templates", False):
                        current = current(*self.callable_args, **self.callable_kwargs)
                # Important that we break in None case, or a relationship
                # spanning across a null-key will raise an exception in the
                # next iteration, instead of defaulting.
                if current is None:
                    break
            return current
        except Exception:
            if not quiet:
                raise

    @property
    def bits(self):
        if self == "":
            return ()
        return self.split(self.SEPARATOR)

    def get_field(self, model):
        """
        Return the django model field for model in context, following relations.
        """
        if not hasattr(model, "_meta"):
            return

        field = None
        for bit in self.bits:
            try:
                field = model._meta.get_field(bit)
            except FieldDoesNotExist:
                break

            if hasattr(field, "remote_field"):
                rel = getattr(field, "remote_field", None)
                model = getattr(rel, "model", model)

        return field

    def penultimate(self, context, quiet=True):
        """
        Split the accessor on the right-most separator ('__'), return a tuple with:
         - the resolved left part.
         - the remainder

        Example::

            >>> Accessor("a__b__c").penultimate({"a": {"a": 1, "b": {"c": 2, "d": 4}}})
            ({"c": 2, "d": 4}, "c")

        """
        path, _, remainder = self.rpartition(self.SEPARATOR)
        return BaseAccessor(path).resolve(context, quiet=quiet), remainder


#####
# Accessor - cornerstone building block - defines how to resolve a value from a string description.
#####
class Accessor(BaseAccessor):
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
        """Resolve this accessor using given model as context to return the model field verbose name."""
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
                return {
                    self.t(accessor): value for accessor, value in accessors.items()
                }
            case _:
                return [self.t(accessor) for accessor in accessors]


def get_accessor(
    accessor: Optional[AccessorSpec], accessor_type: Type[AccessorType] = Accessor
) -> AccessorType | None:
    """helper: return an Accessor instance from the given spec.  Returns None if input accessor is None."""
    return accessor_type(accessor) if isinstance(accessor, str) else accessor
