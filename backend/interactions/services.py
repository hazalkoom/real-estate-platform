from properties.models import Listing
from .models import Favorite, TourRequest, Review
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def toggle_favorite_service(user, listing_id):
    """
    Toggles a listing in the user's favorites.
    Returns True if added, False if removed.
    """
    try:
        # Only allow favoriting active, non-deleted listings
        listing = Listing.objects.get(id=listing_id, is_deleted=False, status=Listing.ListingStatus.ACTIVE)
    except Listing.DoesNotExist:
        raise Exception("Listing not found or not active. You can't favorite a ghost, ya hmar.")

    # Check if it already exists
    favorite = Favorite.objects.filter(user=user, listing=listing).first()
    
    if favorite:
        favorite.delete()
        return False  # Return False meaning it was removed
    else:
        Favorite.objects.create(user=user, listing=listing)
        return True   # Return True meaning it was added

def request_tour_service(buyer, listing_id, tour_date, message=""):
    """
    Buyer requests a tour for a specific listing.
    """
    try:
        listing = Listing.objects.get(id=listing_id, is_deleted=False, status=Listing.ListingStatus.ACTIVE)
    except Listing.DoesNotExist:
        raise Exception("Listing not found or is no longer active.")

    if tour_date < timezone.now():
        raise Exception("You cannot schedule a tour in the past, ya ghabi. Get a time machine.")

    tour = TourRequest.objects.create(
        buyer=buyer,
        listing=listing,
        tour_date=tour_date,
        message=message,
        status=TourRequest.TourStatus.PENDING
    )
    return tour

def respond_to_tour_service(user, tour_id, new_status):
    """
    Agent responds to a tour request (Accept/Reject).
    """
    try:
        tour = TourRequest.objects.get(id=tour_id)
    except TourRequest.DoesNotExist:
        raise Exception("Tour request not found.")

    # IDOR Protection: Only the agent who owns the listing can respond
    if tour.listing.agent != user:
        raise Exception("Access denied. You do not manage this listing, ya harami.")

    valid_statuses = [TourRequest.TourStatus.ACCEPTED, TourRequest.TourStatus.REJECTED, TourRequest.TourStatus.CANCELLED]
    if new_status not in valid_statuses:
        raise Exception("Invalid status update.")

    tour.status = new_status
    tour.save()
    return tour

def create_review_service(reviewer, agent_id, rating, comment=""):
    """
    Creates a review for an agent. Prevents duplicate reviews.
    """
    if not (1 <= rating <= 5):
        raise Exception("Rating must be between 1 and 5, ya ghabi.")

    try:
        agent = User.objects.get(id=agent_id, is_agent=True)
    except User.DoesNotExist:
        raise Exception("Target user is not an agent or does not exist.")

    if reviewer.id == agent.id:
        raise Exception("You cannot review yourself, ya nargesi (يا نرجسي).")

    try:
        review = Review.objects.create(
            reviewer=reviewer,
            agent=agent,
            rating=rating,
            comment=comment
        )
        return review
    except IntegrityError:
        raise Exception("You have already reviewed this agent. Stop spamming.")