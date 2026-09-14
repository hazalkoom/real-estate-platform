import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType, Property, Location
from properties.services import create_property_service

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