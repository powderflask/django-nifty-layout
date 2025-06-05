"""Nifty Layout Components

A micro-framework for defining re-usable layout components from the fields of an object

- a "Layout Component" has 2 parts;
  - Component Nodes define the hierarchical structure for a sub-set of object fields.
    Each node encapsulates how to access, format, and label a field's value and its children.
    Once bound to a data object (e.g., a model instance) the "bound node" provides a
    uniform interface to access the value and label for one or more fields in an encapsulated object.
  - One or more templates that use the interface defined by a Bound Node to render the component into HTML.

- most layout components expect to work with django Models,
  but can be adapted to any object type by injecting custom accessors
"""

from __future__ import annotations

import abc
from collections.abc import Iterable, Mapping, Sequence
from contextlib import contextmanager
from functools import partial
from typing import Any, Callable, Hashable, Iterator, Optional, Type, TypeAlias

from django.db import models
from django.template import Template
from django.template.loader import get_template

from .accessor import Accessor, AccessorSpec, AccessorType, get_accessor

# A Formatter is a function that takes a value returns a formatted value
Formatter: TypeAlias = Callable[[Any, ...], str]

# A Labeller is a function that takes an accessor and returns string label for the attribute
Labeller: TypeAlias = Callable[[AccessorSpec, ...], str]


def field_labeller(obj: object | models.Model, accessor: AccessorSpec, **unused) -> str:
    """Return a label for the given accessor of given object, which could be a django Model instance.

    If `obj` is a model instance, returns the verbose name of the accessor field, if accessor is a model field.
    Otherwise, looks for magic attribute / method:  `foo_label` or `get_foo_label` on obj.
    In either case, if no labelling is provided by obj, defines a title-case label based on accessor.
    """
    accessor = Accessor(accessor) if isinstance(accessor, str) else accessor
    if isinstance(obj, models.Model):
        return accessor.get_label(obj)
    # look for "foo_label" attribute or "get_foo_label" method on object, if there isn't one, use the attribute name
    attr = accessor.bits[-1]
    label = getattr(obj, f"{attr}_label", getattr(obj, f"get_{attr}_label", None))
    if callable(label):
        label = label()
    label = label if label is not None else attr.replace("_", " ").title()
    return label


def get_formatted_labeller(
    labeller, formatter
):  # todo - add tests or change labelling/formatting logic
    def formatted_labeller(*args, **kwargs):
        return formatter(labeller(*args, **kwargs))

    return formatted_labeller


# Examples:


#########
# Component Nodes
# A Bound Node is an adapter that provides a uniform interface for access to values and labels of encapsulated object
# Its unbound Node defines access and formatting rules.
#########
#########
# Important design note: although we are defining the type hierarchy with inheritance here, the behaviours for each
#  type are assembled using composition.
#  E.g., define reusable accessor, labeller, formatter to assemble custom node types.
#  Custom node types are mainly for convenience - a commonly used assembly - think of them as syntactic sugar
#  The key here is: don't build a deeply nested inheritance hierarchy!  Use composition to customize Node behaviours.
#########


# A TemplateType can be a Template object, the string template path, or a callable that takes a single parameter.
TemplateType: TypeAlias = Template | str | Callable[["BoundNode"], Template]


class BoundNode(Iterable):
    """A node that is bound to a piece of data, usually a dict, iterable, object, or model instance
    Defines the interface for accessing a "value" and "label" from the data, and iterating / accessing its children.

    If node is a composite, all children are also bound to the same data.  Iteration is over the bound fixings nodes
    Optional template is passed through to context, and **may** be used, if parent template is so configured.
    """

    def __init__(
        self, data: Any, node: BaseNode, template: Optional[TemplateType] = None
    ):
        self.node = node
        self.data = data
        self.children = [child.bind(data) for child in node]
        self.template = self._get_template(template) if template else None

    def _get_template(self, template: TemplateType) -> Template:
        """return a template for rendering this node with."""
        match template:
            case Template():
                return template
            case str():
                return get_template(template)
            case _ if callable(template):
                return template(self)
            case _:
                raise ValueError(f"Unexpected value for template: {template}.")

    @property
    def value(self):
        """Fetch the data value from data object and format it."""
        return self.node.get_formatted_value(self.node.get_raw_value(self.data))

    @property
    def label(self):
        """Fetch the label from the data object."""
        return self.node.get_label(self.data)

    # Iterable and Sequence interface

    def __getitem__(self, index) -> BoundNode:
        """Return the bound fixings node at given 0 <= index < len(self)"""
        return self.children[index]

    def __len__(self) -> int:
        return len(self.children)

    def __iter__(self) -> Iterator[BoundNode]:
        """Iterate over bound fixings nodes."""
        return iter(self.children)


class BoundSequenceNode(BoundNode, Sequence):
    """A BoundNode representing a linear sequence of bound nodes."""

    def __init__(
        self,
        data: Any,
        node: SequenceCompositeNode,
        template: Optional[TemplateType] = None,
    ):
        """Narrowing Types only - exactly same as a BoundNode"""
        self.node = node  # only to please the type checker, which otherwise thinks node is a BaseNode
        super().__init__(data, node, template)


class BoundDictNode(BoundNode, Mapping):
    """A BoundNode representing a mapping of keys to bound nodes."""

    def __init__(
        self,
        data: Any,
        node: DictCompositeNode,
        template: Optional[TemplateType] = None,
    ):
        self.node = node  # only to please the type checker, which otherwise thinks node is a BaseNode
        with node.as_sequence():
            super().__init__(data, node, template)
        self.mapping = {k: v for k, v in zip(self.node.mapping.keys(), self.children)}

    @contextmanager
    def as_sequence(self):
        """A context manager allowing direct iteration and numeric indexing on the fixings nodes"""
        orig_class = type(self)
        try:
            self.__class__ = BoundSequenceNode
            yield self  # Hand back control to the with-block
        finally:
            self.__class__ = orig_class

    # Mapping interface
    def __iter__(self) -> Iterator[Hashable]:
        """Iterate over the map's ordered key set."""
        return iter(self.mapping)

    def __getitem__(self, key: Hashable) -> BoundNode:
        """Lookup bound fixings node in dict by key"""
        return self.mapping[key]


##############
# Unbound Nodes are a static description of the logic to access, format, and label a value.
# The intent is to define a small, declarative syntax.
# `bind` a Node to some data (and optionally a template) to get a BoundNode suitable for rendering.
#############


class BaseNode(Iterable, abc.ABC):
    """Abstract Base class for all types of Spiffy Component Nodes"""

    default_formatter: Formatter | bool = False  # default does no formatting
    default_labeller: Labeller | str | bool = False  # default has no label
    bound_node_type: type[BoundNode] = (
        BoundNode  # data type returned by `bind` operation
    )

    def __init__(
        self,
        formatter: Optional[Formatter | bool] = None,
        labeller: Optional[Labeller | str | bool] = None,
        template: Optional[TemplateType] = None,
    ):
        """Parameters passed as None default to Node type's default values."""
        self.formatter = (
            formatter if formatter is not None else type(self).default_formatter
        )
        self.labeller = (
            labeller if labeller is not None else type(self).default_labeller
        )
        self.template = template

    def bind(self, data: Any, template: Optional[TemplateType] = None) -> BoundNode:
        """Return a BoundNode that binds the given data (and template) to this node"""
        template = template or self.template
        return self.bound_node_type(data=data, node=self, template=template)

    # Value / Label extraction API

    def get_raw_value(self, data: Any) -> Any:
        """Extract and return the raw value for this Node from the given data object"""
        return data

    def get_formatted_value(self, value: Any) -> str | Any:
        """Return formatted version of given raw value"""
        return self.formatter(value) if self.formatter else value

    def get_label(self, data: Any) -> str | None:
        """Return a label for the given data object"""
        return (
            self.labeller(data)
            if callable(self.labeller)
            else str(self.labeller) if self.labeller else None
        )

    # Iterable interface

    def __iter__(self):
        return iter([])


# Concrete Node types fall in 2 basic classes: Atomic and Composite


class AtomicNode(BaseNode, abc.ABC):
    """Abstract Base class for an atomic Components (no children)"""

    pass


class FieldNode(AtomicNode):
    """Basic atomic node for encapsulating access to the data for a single field using a Accessor"""

    default_accessor_type: Type[AccessorType] = (
        Accessor  # The Accessor type used to wrap naked accessor spec.
    )
    default_labeller: Labeller | str | bool = field_labeller

    def __init__(
        self,
        accessor: AccessorSpec,
        formatter: Optional[Formatter | bool] = None,
        labeller: Optional[Labeller | str | bool] = None,
        template: Optional[TemplateType] = None,
    ):
        """Parameters passed as None default to Node type's default values."""
        labeller = (
            labeller
            if labeller is not None
            else partial(type(self).default_labeller, accessor=accessor)
        )
        super().__init__(formatter=formatter, labeller=labeller, template=template)
        self.accessor = get_accessor(accessor, type(self).default_accessor_type)

    def get_raw_value(self, data: Any) -> Any:
        """Extract and return the raw value for this Node from the given data object"""
        return self.accessor.resolve(data)


# define extended FieldNodes for common use-cases, assembled with custom labellers and formatters
# E.g., CurrencyFieldNode, DecimalFieldNode, DateField, DateTimeField,...


class CompositeNode(BaseNode, abc.ABC):
    """Abstract Base class for a composite iterable component with zero or more ordered children"""

    default_child_node_type: type[FieldNode] = (
        FieldNode  # "naked" children are wrapped in this Node type.
    )

    def __init__(
        self,
        *children: BaseNode | AccessorSpec,
        formatter: Optional[
            Formatter | bool
        ] = None,  # default: use class default_formatter
        labeller: Optional[
            Labeller | str | bool
        ] = None,  # default: use class default_labeller
        child_node_type: Optional[type[BaseNode]] = None,
        **attributes: str,
    ):
        super().__init__(formatter=formatter, labeller=labeller, **attributes)
        self.child_node_type = child_node_type or type(self).default_child_node_type
        self.children = [self.wrap_child(child) for child in children]

    def wrap_child(self, child: BaseNode | AccessorSpec) -> FieldNode:
        return child if isinstance(child, BaseNode) else self.child_node_type(child)

    # Iterable interface and Sequence interface
    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index: int) -> FieldNode:
        return self.children[index]

    def __len__(self) -> int:
        return len(self.children)


class SequenceCompositeNode(CompositeNode, Sequence):
    """A Composite node that behaves as an iterable of ordered fixings nodes"""

    bound_node_type = BoundSequenceNode


# A MappingElement can be defined by any dict-like object or by a 2-tuple (key, value)
# When used to initialize a DictCompositeNode, all MappingElements are combined, in order, to form a single dict.
MappingElement: TypeAlias = (
    Mapping[Hashable, BaseNode | AccessorSpec]
    | tuple[Hashable, BaseNode | AccessorSpec]
)


class DictCompositeNode(CompositeNode, Mapping):
    """A Composite that allows fixings nodes to be looked up with a key. Caution: iteration is over keys not values!"""

    bound_node_type = BoundDictNode

    def __init__(self, *children: MappingElement, **kwargs):
        """Children can be looked up by key, and iteration is over keys.  dict semantics."""
        mappings = (
            child if hasattr(child, "items") else dict((child,)) for child in children
        )
        mapping = {k: v for mapping in mappings for k, v in mapping.items()}

        super().__init__(*mapping.values(), **kwargs)
        assert len(mapping.keys()) == len(self.children)
        self.mapping = {k: v for k, v in zip(mapping.keys(), self.children)}

    @contextmanager
    def as_sequence(self):
        """A context manager allowing direct iteration and numeric indexing on the fixings nodes"""
        orig_class = type(self)
        try:
            self.__class__ = SequenceCompositeNode
            yield self  # Hand back control to the with-block
        finally:
            self.__class__ = orig_class

    # Mapping interface
    def __iter__(self) -> Iterator[Hashable]:
        """Iterate over the map's ordered key set."""
        return iter(self.mapping)

    def __getitem__(self, key: Hashable) -> FieldNode:
        """Lookup fixings node in map by key"""
        return self.mapping[key]


class Seq(SequenceCompositeNode):

    def __init__(self, *children: BaseNode | AccessorSpec | Iterable, **kwargs):
        if len(children) == 1 and isinstance(children[0], (list, tuple, set)):
            # Instead of wrapping the iterable itself in `child_node_class`, we wrap each element individually
            # enables us to use `child_node_class=Seq` to create a nested sequence
            children = children[0]
        super().__init__(*children, **kwargs)
