import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType
from properties.services import create_property_service, create_listing_service
from users.tests.test_api import generate_tokens  # Assuming you have this helper
from datetime import datetime, timedelta
from django.utils import timezone
from interactions.models import TourRequest

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

@pytest.mark.django_db
def test_request_tour_api(client):
    buyer = User.objects.create_user(email="tour_buyer2@example.com", password="Secure123!")
    agent = User.objects.create_user(email="tour_agent2@example.com", password="Secure123!", is_agent=True)
    access, _ = generate_tokens(buyer)
    
    ptype = PropertyType.objects.create(name="Duplex")
    prop = create_property_service(agent, ptype.id, 2, 1, 100.0, "Test", {"city": "Giza", "district": "Dokki", "address": "456"})
    listing = create_listing_service(agent, prop.id, "SALE", 5000.0)
    
    # Schedule for tomorrow
    future_date = (timezone.now() + timedelta(days=1)).isoformat()
    
    mutation = f"""
        mutation {{
          requestTour(listingId: "{listing.id}", tourDate: "{future_date}", message: "Can't wait!") {{
            id
            status
            message
          }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["requestTour"]["status"] == "PENDING"
    assert data["data"]["requestTour"]["message"] == "Can't wait!"

@pytest.mark.django_db
def test_respond_to_tour_idor_api(client):
    buyer = User.objects.create_user(email="buyer3@example.com", password="Secure123!")
    real_agent = User.objects.create_user(email="real_agent@example.com", password="Secure123!", is_agent=True)
    hacker_agent = User.objects.create_user(email="hacker_agent@example.com", password="Secure123!", is_agent=True)
    hacker_access, _ = generate_tokens(hacker_agent)
    
    ptype = PropertyType.objects.create(name="Office")
    prop = create_property_service(real_agent, ptype.id, 2, 1, 100.0, "Test", {"city": "Cairo", "district": "Zamalek", "address": "789"})
    listing = create_listing_service(real_agent, prop.id, "RENT", 10000.0)
    
    tour = TourRequest.objects.create(
        buyer=buyer, listing=listing, tour_date=timezone.now() + timedelta(days=1), message="Hello"
    )
    
    mutation = f"""
        mutation {{
          respondToTour(tourId: "{tour.id}", status: "ACCEPTED") {{
            id
            status
          }}
        }}
    """
    
    # Hacker tries to accept a tour for a listing they don't own
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {hacker_access}")
    data = response.json()
    
    assert "errors" in data
    assert "do not manage this listing" in data["errors"][0]["message"]