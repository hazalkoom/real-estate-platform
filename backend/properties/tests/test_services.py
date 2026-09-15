import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType, Property, Location
from properties.services import create_property_service, create_listing_service, add_property_media_service
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

@pytest.mark.django_db
def test_add_property_media_service_success():
    owner = User.objects.create_user(email="media_owner@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Villa Media")
    prop = create_property_service(owner, ptype.id, 2, 2, 100.0, "Desc", {"city": "Cairo", "district": "Maadi", "address": "123"})
    
    media = add_property_media_service(owner, prop.id, "http://image.com/1.jpg", "image", True)
    
    assert media.id is not None
    assert media.property == prop
    assert media.url == "http://image.com/1.jpg"
    assert media.is_primary is True

@pytest.mark.django_db
def test_add_property_media_service_primary_toggle():
    owner = User.objects.create_user(email="media_toggle@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Apartment Media")
    prop = create_property_service(owner, ptype.id, 2, 2, 100.0, "Desc", {"city": "Cairo", "district": "Maadi", "address": "123"})
    
    # Add first image as primary
    media1 = add_property_media_service(owner, prop.id, "http://image.com/old.jpg", "image", True)
    assert media1.is_primary is True
    
    # Add second image as primary
    media2 = add_property_media_service(owner, prop.id, "http://image.com/new.jpg", "image", True)
    
    # Refresh the first one from DB to see if the service demoted it
    media1.refresh_from_db()
    assert media2.is_primary is True
    assert media1.is_primary is False

@pytest.mark.django_db
def test_add_property_media_service_idor():
    owner1 = User.objects.create_user(email="owner1_media@example.com", password="Password123!", is_owner=True)
    owner2 = User.objects.create_user(email="owner2_media@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Studio Media")
    prop = create_property_service(owner1, ptype.id, 1, 1, 50.0, "Desc", {"city": "Cairo", "district": "Maadi", "address": "123"})
    
    # Owner 2 tries to upload to Owner 1's property
    with pytest.raises(Exception, match="can't add pictures to someone else's property"):
        add_property_media_service(owner2, prop.id, "http://image.com/hacker.jpg", "image", True)