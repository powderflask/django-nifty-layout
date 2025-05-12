from dataclasses import dataclass
from functools import partial
from typing import Any

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase

from nifty_layout.components import field_labeller, DictCompositeNode, FieldNode
from nifty_layout.accessor import AccessorSpec

User = get_user_model()

class FormatterTests(SimpleTestCase):
    """Test suite for template formatter functionality."""

    def test_currency_formatter(self):
        """Test formatting numbers as currency."""
        currency_formatter = partial(self._template_formatter, template="${:,.2f}")
        self.assertEqual(currency_formatter(123.4567), "$123.46")

    @staticmethod
    def _template_formatter(value: Any, template: str, **context) -> str:
        return template.format(value, **context)


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

    def test_labeller_with_partial(self):
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

        first_name_labeller = partial(field_labeller, accessor="first_name")
        self.assertEqual(first_name_labeller(larry), "first name")

        user_field_labeller = partial(field_labeller, larry)
        self.assertEqual(user_field_labeller("first_name"), "first name")
        self.assertEqual(user_field_labeller("last_name"), "last name")
        self.assertEqual(user_field_labeller("get_full_name"), "Get Full Name")


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
        self.assertEqual(bnd_node['field'].value, 987)
        self.assertEqual(bnd_node['comments'].value, "some comments!")

    @staticmethod
    def _get_field_with_comments(accessor: AccessorSpec, comment_accessor: AccessorSpec, **kwargs) -> DictCompositeNode:
        return DictCompositeNode(
            ("field", FieldNode(accessor=accessor, **kwargs)),
            ("comments", FieldNode(accessor=comment_accessor))
        )
