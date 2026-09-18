import pytest
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyType, Listing, Location
from interactions.models import Favorite, TourRequest, Review

User = get_user_model()

@pytest.mark.django_db
def test_favorite_creation_and_constraint():
    user = User.objects.create_user(email="fav_user@example.com", password="Password123!")
    agent = User.objects.create_user(email="fav_owner@example.com", password="Password123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Studio")
    
    # You need a location, ya hmar!
    loc = Location.objects.create(city="Cairo", district="Maadi", address="123")
    prop = Property.objects.create(owner=agent, property_type=ptype, location=loc, bedrooms=1, bathrooms=1, area=50.0)
    listing = Listing.objects.create(property=prop, agent=agent, listing_type="SALE", price=1000)

    fav = Favorite.objects.create(user=user, listing=listing)
    assert fav.id is not None

    # Test Unique Constraint (User cannot favorite the same listing twice)
    with pytest.raises(IntegrityError):
        Favorite.objects.create(user=user, listing=listing)

@pytest.mark.django_db
def test_tour_request_creation():
    buyer = User.objects.create_user(email="tour_buyer@example.com", password="Password123!")
    agent = User.objects.create_user(email="tour_owner@example.com", password="Password123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Loft")
    
    loc = Location.objects.create(city="Alex", district="Smouha", address="456")
    prop = Property.objects.create(owner=agent, property_type=ptype, location=loc, bedrooms=1, bathrooms=1, area=50.0)
    listing = Listing.objects.create(property=prop, agent=agent, listing_type="SALE", price=1000)

    tour = TourRequest.objects.create(
        buyer=buyer, 
        listing=listing, 
        tour_date="2026-10-01T10:00:00Z", 
        message="Looking forward to it"
    )
    assert tour.status == "PENDING"
    assert tour.id is not None

@pytest.mark.django_db
def test_review_creation_and_constraint():
    reviewer = User.objects.create_user(email="rev_user@example.com", password="Password123!")
    agent = User.objects.create_user(email="rev_agent@example.com", password="Password123!", is_agent=True)

    rev = Review.objects.create(reviewer=reviewer, agent=agent, rating=5, comment="Great agent!")
    assert rev.id is not None

    # Test Unique Constraint (User cannot review the same agent twice)
    with pytest.raises(IntegrityError):
        Review.objects.create(reviewer=reviewer, agent=agent, rating=1)