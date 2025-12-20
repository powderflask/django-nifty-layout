from dataclasses import dataclass
from functools import partial
from types import SimpleNamespace
from typing import Any

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase

from nifty_layout.components import (
    field_labeller, DictCompositeNode, FieldNode, BoundNode, get_field_display,
    get_formatted_labeller
)
from nifty_layout.accessor import AccessorSpec

User = get_user_model()


class GetFieldDisplayTests(SimpleTestCase):
    """Test suite for template get_field_display functionality."""

    @dataclass
    class SimpleObject:
        a: int = 42
        b: str = "Question?"
        c: SimpleNamespace = SimpleNamespace(x=1, y=99, get_x_display=lambda: f"X:{1}")

        def get_a_display(self):
            return f"The answer is {self.a}"

    def test_get_field_display_with_simple_obj(self):
        """Test formatter usage with a simple object that defines a "magic" get_foo_display method."""
        obj = self.SimpleObject()

        obj_field_formatter = lambda accessor: get_field_display("default", record=obj, accessor=accessor)
        self.assertEqual(obj_field_formatter('c__y'), "99")
        self.assertEqual(obj_field_formatter('c__x'), "X:1")

    def test_get_field_display_with_accessor(self):
        """Test formatter usage with a simple object that defines a "magic" get_foo_display method."""
        obj = self.SimpleObject()

        obj_field_formatter = lambda accessor: get_field_display("default", record=obj, accessor=accessor)
        self.assertEqual(obj_field_formatter('a'), "The answer is 42")
        self.assertEqual(obj_field_formatter('b'), "Question?")

    def test_get_field_display_with_user_model(self):
        """Test labelling fields for a User instance."""
        larry = User(username="lmapmaker", first_name="Larry", last_name="Mapmaker")
        larry.get_full_name = lambda: f"{larry.first_name} {larry.last_name}"

        # this is the "normal" way nifty Node's make use a FieldFormatter: bind to accessor, then resolve for data
        first_name_formatter = partial(get_field_display, accessor="first_name")
        self.assertEqual(first_name_formatter("default", record=larry), "Larry")

        user_field_formatter = lambda accessor: get_field_display("default", record=larry, accessor=accessor)
        self.assertEqual(user_field_formatter("first_name"), "Larry")
        self.assertEqual(user_field_formatter("last_name"), "Mapmaker")
        self.assertEqual(user_field_formatter("get_full_name"), "Larry Mapmaker")


class LabellerTests(SimpleTestCase):
    """Test suite for field labeller functionality."""

    @dataclass
    class SimpleObject:
        a: int = 42
        a_label: str = "The Answer"
        b: str = "Question?"
        some_unlabelled_attr: Any = None

        def get_b_label(self):
            return f"What is {self.a_label}"

    def test_labeller_with_object(self):
        """Test labeller usage with partials."""
        obj = self.SimpleObject()

        obj_field_labeller = partial(field_labeller, obj)
        self.assertEqual(obj_field_labeller('a'), "The Answer")
        self.assertEqual(obj_field_labeller('b'), "What is The Answer")
        self.assertEqual(obj_field_labeller('some_unlabelled_attr'), "Some Unlabelled Attr")

    def test_labeller_with_user_model(self):
        """Test labelling fields for a User instance."""
        larry = User(username="lmapmaker", first_name="Larry", last_name="Mapmaker")
        larry.get_full_name = lambda: f"{larry.first_name} {larry.last_name}"

        # this is the "normal" way nifty Node's make use a FieldLabeller: bind to accessor, then resolve for data
        first_name_labeller = partial(field_labeller, accessor="first_name")
        self.assertEqual(first_name_labeller(larry), "first name")

        user_field_labeller = partial(field_labeller, larry)
        self.assertEqual(user_field_labeller("first_name"), "first name")
        self.assertEqual(user_field_labeller("last_name"), "last name")
        self.assertEqual(user_field_labeller("get_full_name"), "Get Full Name")

    def test_get_formatted_labeller(self):
        labeller = get_formatted_labeller(
            labeller=lambda obj, **kwargs: "ring",
            formatter=lambda label, **kwargs: f"the one {label}"
        )
        self.assertEqual(labeller(None), "the one ring")


class FieldNodeTests(SimpleTestCase):
    """Test suite for FieldNode functionality."""

    @dataclass
    class SimpleObject:
        a: int = 42
        b: str = "Question?"
        c: SimpleNamespace = SimpleNamespace(x=1, y=99, z=lambda: 42, get_x_display=lambda: f"X:{1}")

        def get_a_display(self):
            return f"The answer is {self.a}"

    @staticmethod
    def _fld(obj: Any, accessor: AccessorSpec, **kwargs) -> BoundNode:
        return FieldNode(accessor, **kwargs).bind(obj)

    def test_display_value_with_simple_obj(self):
        obj = self.SimpleObject()

        self.assertEqual(self._fld(obj, "a").value, "The answer is 42")
        self.assertEqual(self._fld(obj, "b").value, "Question?")

    def test_display_value_with_deep_accessor(self):
        obj = self.SimpleObject()

        self.assertEqual(self._fld(obj, "c__y").value, "99")
        self.assertEqual(self._fld(obj, "c__x").value, "X:1")
        self.assertEqual(self._fld(obj, "c__z").value, "42")

    def test_display_value_with_user_model(self):
        larry = User(username="lmapmaker", first_name="Larry", last_name="Mapmaker")
        larry.get_full_name = lambda: f"{larry.first_name} {larry.last_name}"

        self.assertEqual(self._fld(larry, "first_name").value, "Larry")
        self.assertEqual(self._fld(larry, "last_name").value, "Mapmaker")
        self.assertEqual(self._fld(larry, "get_full_name").value, "Larry Mapmaker")


class CompositeNodeTests(SimpleTestCase):
    """Test suite for DictCompositeNode and related functionality."""

    def test_get_field_with_comments(self):
        """Test creating and using DictCompositeNode with field and comments."""
        checkbox = self._get_field_with_comments("my_field", "my_field_comments")

        self.assertEqual(len(checkbox), 2)
        self.assertEqual(checkbox['field'].accessor, 'my_field')
        self.assertEqual(checkbox['comments'].accessor, 'my_field_comments')
        self.assertListEqual(list(checkbox.keys()), ['field', 'comments'])

        with checkbox.as_sequence():
            self.assertListEqual(
                [fld.accessor for fld in checkbox],
                ['my_field', 'my_field_comments']
            )

    def test_binding_composite_node(self):
        """Test binding DictCompositeNode to an object."""
        obj_node = self._get_field_with_comments("a", "b")
        obj = LabellerTests.SimpleObject(a=987, a_label="A Label", b="some comments!")

        bnd_node = obj_node.bind(obj)
        self.assertEqual(bnd_node['field'].label, "A Label")
        self.assertEqual(bnd_node['field'].raw_value, 987)
        self.assertEqual(bnd_node['field'].value, "987")
        self.assertEqual(bnd_node['comments'].value, "some comments!")

    @staticmethod
    def _get_field_with_comments(accessor: AccessorSpec, comment_accessor: AccessorSpec, **kwargs) -> DictCompositeNode:
        return DictCompositeNode(
            ("field", FieldNode(accessor=accessor, **kwargs)),
            ("comments", FieldNode(accessor=comment_accessor))
        )
