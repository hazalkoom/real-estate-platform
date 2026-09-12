import factory
from properties.models import PropertyType, Location, Property, Listing

class PropertyTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PropertyType

    name = factory.Sequence(lambda n: f"Type {n}")

class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    city = "Cairo"
    district = "Maadi"
    address = factory.Sequence(lambda n: f"{n} Test Street")

class PropertyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Property

    property_type = factory.SubFactory(PropertyTypeFactory)
    location = factory.SubFactory(LocationFactory)
    bedrooms = 3
    bathrooms = 2
    area = 150.0
    description = "A standard test property"
    # owner must be passed in from UserFactory when creating!