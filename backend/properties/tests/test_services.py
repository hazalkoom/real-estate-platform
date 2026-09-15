import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType, Property, Location
from properties.services import create_property_service, create_listing_service
from properties.models import Listing

User = get_user_model()

@pytest.mark.django_db
def test_create_property_service():
    # 1. Setup dummy data
    owner = User.objects.create_user(email="owner_service@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Apartment")
    
    location_data = {
        "city": "Cairo",
        "district": "Zamalek",
        "address": "22 Nile Street",
        "latitude": 30.05,
        "longitude": 31.22
    }
    
    # 2. Call the service directly
    prop = create_property_service(
        user=owner,
        property_type_id=ptype.id,
        bedrooms=3,
        bathrooms=2,
        area=150.0,
        description="Nile view",
        location_data=location_data
    )
    
    # 3. Assert it actually created the records in PostgreSQL
    assert prop.id is not None
    assert prop.owner == owner
    assert prop.property_type == ptype
    assert prop.location.city == "Cairo"
    assert prop.area == 150.0
    
    # Verify database counts
    assert Property.objects.count() == 1
    assert Location.objects.count() == 1


@pytest.mark.django_db
def test_create_listing_service_success():
    owner = User.objects.create_user(email="owner_list@example.com", password="Password123!", is_owner=True)
    agent = User.objects.create_user(email="agent_list@example.com", password="Password123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Villa")
    
    location_data = {
        "city": "Alexandria",
        "district": "Smouha",
        "address": "15 Sea Road"
    }
    
    # Create the property first
    prop = create_property_service(owner, ptype.id, 5, 4, 300.0, "Sea view", location_data)
    
    # Create the listing
    listing = create_listing_service(agent, prop.id, "SALE", 15000000.00)
    
    assert listing.id is not None
    assert listing.agent == agent
    assert listing.property == prop
    assert listing.listing_type == "SALE"
    assert listing.status == "ACTIVE"
    assert listing.price == 15000000.00

@pytest.mark.django_db
def test_create_listing_service_already_listed():
    owner = User.objects.create_user(email="owner_fail@example.com", password="Password123!", is_owner=True)
    agent = User.objects.create_user(email="agent_fail@example.com", password="Password123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Office")
    
    location_data = {"city": "Cairo", "district": "Downtown", "address": "1 Main St"}
    prop = create_property_service(owner, ptype.id, 2, 1, 100.0, "Office space", location_data)
    
    # First listing succeeds
    create_listing_service(agent, prop.id, "RENT", 50000.00)
    
    # Second listing fails
    with pytest.raises(Exception, match="already listed"):
        create_listing_service(agent, prop.id, "RENT", 60000.00)