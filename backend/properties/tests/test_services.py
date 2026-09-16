import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType, Property, Location
from properties.services import create_property_service, create_listing_service, add_property_media_service, update_property_media_service, delete_property_media_service, assign_property_amenities_service, search_properties_service, search_listings_service
from properties.models import Listing, PropertyMedia, Amenity

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

@pytest.mark.django_db
def test_update_property_media_service_success():
    owner = User.objects.create_user(email="media_upd@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Loft")
    prop = create_property_service(owner, ptype.id, 1, 1, 80.0, "Desc", {"city": "Cairo", "district": "Maadi", "address": "123"})
    
    media1 = add_property_media_service(owner, prop.id, "http://image.com/1.jpg", "image", True)
    media2 = add_property_media_service(owner, prop.id, "http://image.com/2.jpg", "image", False)
    
    # Update media2 to be the primary image
    updated_media = update_property_media_service(owner, media2.id, is_primary=True, url="http://image.com/new.jpg")
    
    assert updated_media.url == "http://image.com/new.jpg"
    assert updated_media.is_primary is True
    
    # Prove media1 got demoted
    media1.refresh_from_db()
    assert media1.is_primary is False

@pytest.mark.django_db
def test_delete_property_media_service_success():
    owner = User.objects.create_user(email="media_del@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Mansion")
    prop = create_property_service(owner, ptype.id, 5, 5, 500.0, "Desc", {"city": "Cairo", "district": "Zamalek", "address": "123"})
    
    media = add_property_media_service(owner, prop.id, "http://image.com/1.jpg")
    assert PropertyMedia.objects.count() == 1
    
    result = delete_property_media_service(owner, media.id)
    assert result is True
    assert PropertyMedia.objects.count() == 0  # Hard delete!

@pytest.mark.django_db
def test_assign_property_amenities_success():
    owner = User.objects.create_user(email="amenity_owner@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Condo")
    prop = create_property_service(owner, ptype.id, 2, 2, 100.0, "Desc", {"city": "Cairo", "district": "Maadi", "address": "123"})
    
    a1 = Amenity.objects.create(name="Pool")
    a2 = Amenity.objects.create(name="Gym")
    
    updated_prop = assign_property_amenities_service(owner, prop.id, [a1.id, a2.id])
    
    assert updated_prop.amenities.count() == 2
    assert a1 in updated_prop.amenities.all()

@pytest.mark.django_db
def test_assign_property_amenities_idor():
    owner1 = User.objects.create_user(email="amenity_victim@example.com", password="Password123!", is_owner=True)
    owner2 = User.objects.create_user(email="amenity_hacker@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Penthouse")
    prop = create_property_service(owner1, ptype.id, 2, 2, 100.0, "Desc", {"city": "Cairo", "district": "Maadi", "address": "123"})
    
    a1 = Amenity.objects.create(name="Balcony")
    
    with pytest.raises(Exception, match="cannot modify amenities for someone else's property"):
        assign_property_amenities_service(owner2, prop.id, [a1.id])

@pytest.mark.django_db
def test_search_properties_service():
    owner = User.objects.create_user(email="searcher@example.com", password="Password123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Villa Search")
    
    # Property 1: Cairo, 3 beds, 200 area
    create_property_service(owner, ptype.id, 3, 2, 200.0, "P1", {"city": "Cairo", "district": "Maadi", "address": "1"})
    
    # Property 2: Alex, 5 beds, 400 area
    create_property_service(owner, ptype.id, 5, 4, 400.0, "P2", {"city": "Alex", "district": "Smouha", "address": "2"})
    
    # Test City Filter
    qs_cairo = search_properties_service(city="Cairo")
    assert qs_cairo.count() == 1
    assert qs_cairo.first().location.city == "Cairo"
    
    # Test Bedrooms Filter (gte 4)
    qs_beds = search_properties_service(min_bedrooms=4)
    assert qs_beds.count() == 1
    assert qs_beds.first().bedrooms == 5
    
    # Test Area Filter (lte 300)
    qs_area = search_properties_service(max_area=300.0)
    assert qs_area.count() == 1
    assert qs_area.first().area == 200.0

@pytest.mark.django_db
def test_search_listings_service():
    owner = User.objects.create_user(email="list_search@example.com", password="Password123!", is_owner=True)
    agent = User.objects.create_user(email="list_agent@example.com", password="Password123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Villa Search List")
    
    # Property 1 (Cairo) for Sale at 2,000,000
    prop1 = create_property_service(owner, ptype.id, 3, 2, 200.0, "P1", {"city": "Cairo", "district": "Maadi", "address": "1"})
    create_listing_service(agent, prop1.id, "SALE", 2000000.0)
    
    # Property 2 (Alex) for Rent at 15,000
    prop2 = create_property_service(owner, ptype.id, 5, 4, 400.0, "P2", {"city": "Alex", "district": "Smouha", "address": "2"})
    create_listing_service(agent, prop2.id, "RENT", 15000.0)
    
    # Test Listing Filter (Max Price)
    qs_price = search_listings_service(max_price=50000.0)
    assert qs_price.count() == 1
    assert qs_price.first().price == 15000.0
    
    # Test Joined Property Filter (City)
    qs_cairo = search_listings_service(city="Cairo")
    assert qs_cairo.count() == 1
    assert qs_cairo.first().property.location.city == "Cairo"