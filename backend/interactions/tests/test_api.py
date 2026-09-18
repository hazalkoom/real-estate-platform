import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType
from properties.services import create_property_service, create_listing_service
from users.tests.test_api import generate_tokens  # Assuming you have this helper

User = get_user_model()

@pytest.mark.django_db
def test_toggle_favorite_api(client):
    buyer = User.objects.create_user(email="buyer_api@example.com", password="Secure123!")
    owner = User.objects.create_user(email="owner_api@example.com", password="Secure123!", is_owner=True)
    agent = User.objects.create_user(email="agent_api@example.com", password="Secure123!", is_agent=True)
    access, _ = generate_tokens(buyer)
    
    ptype = PropertyType.objects.create(name="Apartment")
    prop = create_property_service(owner, ptype.id, 2, 1, 100.0, "Test", {"city": "Giza", "district": "Dokki", "address": "456"})
    listing = create_listing_service(agent, prop.id, "RENT", 5000.0)
    
    mutation = f"""
        mutation {{
          toggleFavorite(listingId: "{listing.id}")
        }}
    """
    
    # Add Favorite
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    assert response.json()["data"]["toggleFavorite"] is True
    
    # Remove Favorite
    response2 = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    assert response2.json()["data"]["toggleFavorite"] is False