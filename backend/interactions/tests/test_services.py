import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType
from properties.services import create_property_service, create_listing_service
from interactions.services import toggle_favorite_service
from interactions.models import Favorite

User = get_user_model()

@pytest.mark.django_db
def test_toggle_favorite_service():
    buyer = User.objects.create_user(email="buyer@example.com", password="Password123!")
    owner = User.objects.create_user(email="owner@example.com", password="Password123!", is_owner=True)
    agent = User.objects.create_user(email="agent@example.com", password="Password123!", is_agent=True)
    
    ptype = PropertyType.objects.create(name="Villa")
    prop = create_property_service(owner, ptype.id, 3, 2, 200.0, "Test", {"city": "Cairo", "district": "Maadi", "address": "123"})
    listing = create_listing_service(agent, prop.id, "SALE", 100000.0)
    
    # Toggle ON
    added = toggle_favorite_service(buyer, listing.id)
    assert added is True
    assert Favorite.objects.filter(user=buyer, listing=listing).exists()
    
    # Toggle OFF
    removed = toggle_favorite_service(buyer, listing.id)
    assert removed is False
    assert not Favorite.objects.filter(user=buyer, listing=listing).exists()