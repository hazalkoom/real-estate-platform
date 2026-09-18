import pytest
from django.contrib.auth import get_user_model
from properties.models import PropertyType
from properties.services import create_property_service, create_listing_service
from interactions.services import toggle_favorite_service, request_tour_service, respond_to_tour_service
from interactions.models import Favorite, TourRequest
from datetime import timedelta
from django.utils import timezone

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

@pytest.mark.django_db
def test_request_tour_service_success():
    buyer = User.objects.create_user(email="buyer_tour_svc@example.com", password="Password123!")
    agent = User.objects.create_user(email="agent_tour_svc@example.com", password="Password123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Tour Test Type")
    
    prop = create_property_service(agent, ptype.id, 1, 1, 50.0, "Test", {"city": "Cairo", "district": "Zamalek", "address": "1"})
    listing = create_listing_service(agent, prop.id, "SALE", 1000)

    future_date = timezone.now() + timedelta(days=2)
    tour = request_tour_service(buyer, listing.id, future_date, "I want to see this.")
    
    assert tour.id is not None
    assert tour.status == TourRequest.TourStatus.PENDING

@pytest.mark.django_db
def test_request_tour_service_past_date():
    buyer = User.objects.create_user(email="buyer_past_svc@example.com", password="Password123!")
    agent = User.objects.create_user(email="agent_past_svc@example.com", password="Password123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Past Tour Type")
    
    prop = create_property_service(agent, ptype.id, 1, 1, 50.0, "Test", {"city": "Cairo", "district": "Zamalek", "address": "2"})
    listing = create_listing_service(agent, prop.id, "SALE", 1000)

    # Try to schedule a tour 2 days ago
    past_date = timezone.now() - timedelta(days=2)
    with pytest.raises(Exception, match="schedule a tour in the past"):
        request_tour_service(buyer, listing.id, past_date, "I want to see this.")

@pytest.mark.django_db
def test_respond_to_tour_service_idor():
    buyer = User.objects.create_user(email="buyer_idor_svc@example.com", password="Password123!")
    real_agent = User.objects.create_user(email="real_agent_svc@example.com", password="Password123!", is_agent=True)
    hacker = User.objects.create_user(email="hacker_svc@example.com", password="Password123!", is_agent=True)
    
    ptype = PropertyType.objects.create(name="IDOR Test Type")
    prop = create_property_service(real_agent, ptype.id, 1, 1, 50.0, "Test", {"city": "Cairo", "district": "Zamalek", "address": "3"})
    listing = create_listing_service(real_agent, prop.id, "SALE", 1000)

    tour = TourRequest.objects.create(buyer=buyer, listing=listing, tour_date=timezone.now() + timedelta(days=1))

    # Hacker tries to accept a tour for a listing they don't own
    with pytest.raises(Exception, match="do not manage this listing"):
        respond_to_tour_service(hacker, tour.id, TourRequest.TourStatus.ACCEPTED)