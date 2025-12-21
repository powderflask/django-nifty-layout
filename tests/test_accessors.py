"""Tests for Accessor and Accessor related algorithms and objects"""

from django.db import models

from nifty_layout.accessor import Accessor, get_accessor


class Place(models.Model):
    name = models.CharField(max_length=50, verbose_name="A Place")
    city = models.CharField(max_length=50)

    class Meta:
        app_label = "nifty_layout_tests"

    def __str__(self):
        return self.name


class Owner(models.Model):
    name = models.CharField(max_length=100)
    place = models.ForeignKey(Place, models.CASCADE)

    class Meta:
        app_label = "nifty_layout_tests"

    def __str__(self):
        return f"{self.name} at {self.place}"


class Location(models.Model):
    place = models.ForeignKey(Place, models.CASCADE)

    class Meta:
        app_label = "nifty_layout_tests"


class OwnerProfile(models.Model):
    owner = models.OneToOneField(Owner, models.CASCADE, primary_key=True)
    age = models.PositiveIntegerField()

    class Meta:
        app_label = "nifty_layout_tests"

    def __str__(self):
        return "%s is %d" % (self.owner.name, self.age)


class TestAccessor:
    """Test Accessor extensions. Should also add tests for BaseAccessor at some point!"""

    def test_get_label_default_no_such_field(self):
        place_name = Accessor("place__name")
        assert place_name.get_label(None) == "Place Name"  # default label is title-case of split accessor
        city = Accessor("city")
        assert city.get_label(None) == "City"
        owner_name = Accessor("owner__name")
        assert owner_name.get_label(None) == "Owner Name"

    def test_get_label_from_field_default_verbose_name(self):
        city = Accessor("city")
        assert city.get_label(Place) == "city"  # django's default verbose_name is not title case!
        profile = OwnerProfile()
        owner_name = Accessor("owner__name")
        assert owner_name.get_label(profile) == "name"

    def test_get_label_from_field_with_verbose_name(self):
        place_name = Accessor("place__name")
        assert place_name.get_label(Location) == "A Place"
        assert place_name.get_label(Owner) == "A Place"

    def test_get_label_from_instance(self):
        profile = OwnerProfile()
        owner_place_name = Accessor("owner__place__name")
        assert owner_place_name.get_label(profile) == "A Place"


class TestGetAccessor:
    """Test get_accessor method."""
    def test_get_accessor_basics(self):
        foo = get_accessor("foo")
        assert isinstance(foo, Accessor)
        assert foo == "foo"
        bar = get_accessor(foo)
        assert bar is foo

    def test_get_accessor_with_type(self):
        class MyAccessor(Accessor):
            def resolve(self, context, safe=True, quiet=False):
                return 42

        accessor = get_accessor("literally_anything", MyAccessor)
        assert isinstance(accessor, MyAccessor)
        assert accessor.resolve(None) == 42
        assert get_accessor(accessor) is accessor
