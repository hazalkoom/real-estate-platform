import pytest
from users.tests.factories import UserFactory
from properties.tests.factories import PropertyTypeFactory, PropertyFactory, LocationFactory
from properties.models import Property, Listing

@pytest.mark.django_db
def test_property_string_representation():
    prop_type = PropertyTypeFactory(name="Penthouse")
    location = LocationFactory(city="Giza", address="Pyramid View")
    user = UserFactory()
    
    property_obj = PropertyFactory(owner=user, property_type=prop_type, location=location)
    
    assert str(property_obj) == "Penthouse at Giza"

@pytest.mark.django_db
def test_property_soft_delete():
    user = UserFactory()
    prop_type = PropertyTypeFactory()
    property_obj = PropertyFactory(owner=user, property_type=prop_type)
    
    assert property_obj.is_deleted is False
    assert property_obj.deleted_at is None
    
    property_obj.soft_delete()
    property_obj.refresh_from_db()
    
    assert property_obj.is_deleted is True
    assert property_obj.deleted_at is not None

@pytest.mark.django_db
def test_listing_creation():
    user = UserFactory()
    agent = UserFactory(is_agent=True)
    property_obj = PropertyFactory(owner=user)
    
    listing = Listing.objects.create(
        property=property_obj,
        agent=agent,
        listing_type=Listing.ListingType.SALE,
        status=Listing.ListingStatus.ACTIVE,
        price=1500000.00
    )
    
    assert listing.price == 1500000.00
    assert listing.agent == agent
    assert str(listing) == f"SALE - {property_obj} - ACTIVE"