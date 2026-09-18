from properties.models import Listing
from .models import Favorite

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