from .models import Property, Location, PropertyType, Listing, PropertyMedia, Amenity

def create_property_service(user, property_type_id, bedrooms, bathrooms, area, description, location_data):
    """
    Creates a property tied directly to the authenticated user.
    """
    prop_type = PropertyType.objects.get(id=property_type_id)
    
    location = Location.objects.create(
        city=location_data['city'],
        district=location_data['district'],
        address=location_data['address'],
        latitude=location_data.get('latitude'),
        longitude=location_data.get('longitude')
    )
    
    property_obj = Property.objects.create(
        owner=user,
        property_type=prop_type,
        location=location,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        area=area,
        description=description
    )
    return property_obj

def create_listing_service(agent, property_id, listing_type, price):
    """
    Creates a new listing for a property, assigned to the authenticated agent.
    """
    # Grab the property
    try:
        prop = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        raise Exception("Property not found.")

    # Check if the property already has a listing to prevent OneToOne constraint crashes
    if hasattr(prop, 'listing'):
        raise Exception("This property is already listed.")

    # Validate listing type
    if listing_type not in [Listing.ListingType.SALE, Listing.ListingType.RENT]:
        raise Exception("Listing type must be 'SALE' or 'RENT'.")

    listing = Listing.objects.create(
        property=prop,
        agent=agent,
        listing_type=listing_type,
        price=price,
        status=Listing.ListingStatus.ACTIVE  # Default to active when created
    )
    
    return listing

def update_property_service(user, property_id, **kwargs):
    """
    Updates a property, but only if the authenticated user actually owns it.
    """
    try:
        prop = Property.objects.get(id=property_id, is_deleted=False)
    except Property.DoesNotExist:
        raise Exception("Property not found or has been deleted.")

    # Object-level permission check (Prevent IDOR)
    if prop.owner != user:
        raise Exception("Access denied. You do not own this property.")

    # Update only the fields provided
    for key, value in kwargs.items():
        if value is not None:
            setattr(prop, key, value)
            
    prop.save()
    return prop

def delete_property_service(user, property_id):
    """
    Soft deletes a property, but only if the authenticated user owns it.
    """
    try:
        prop = Property.objects.get(id=property_id, is_deleted=False)
    except Property.DoesNotExist:
        raise Exception("Property not found or already deleted.")

    if prop.owner != user:
        raise Exception("Access denied. You cannot delete someone else's property.")

    # We use the soft_delete method you inherited from SoftDeleteModel
    prop.soft_delete()
    return True

def update_listing_service(user, listing_id, **kwargs):
    """
    Updates a listing, but only if the authenticated user is the assigned agent.
    """
    try:
        listing = Listing.objects.get(id=listing_id, is_deleted=False)
    except Listing.DoesNotExist:
        raise Exception("Listing not found or has been deleted.")

    if listing.agent != user:
        raise Exception("Access denied. You are not the agent for this listing.")

    for key, value in kwargs.items():
        if value is not None:
            setattr(listing, key, value)
            
    listing.save()
    return listing

def delete_listing_service(user, listing_id):
    """
    Soft deletes a listing, but only if the authenticated user is the assigned agent.
    """
    try:
        listing = Listing.objects.get(id=listing_id, is_deleted=False)
    except Listing.DoesNotExist:
        raise Exception("Listing not found or already deleted.")

    if listing.agent != user:
        raise Exception("Access denied. You cannot delete another agent's listing.")

    listing.soft_delete()
    return True

def add_property_media_service(user, property_id, url, media_type="image", is_primary=False):
    """
    Adds a media URL to a property. Ensures only one primary image exists.
    """
    try:
        prop = Property.objects.get(id=property_id, is_deleted=False)
    except Property.DoesNotExist:
        raise Exception("Property not found.")

    if prop.owner != user:
        raise Exception("Access denied. You cannot add pictures to someone else's property.")

    # If this new image is the primary one, demote all existing primary images for this property
    if is_primary:
        PropertyMedia.objects.filter(property=prop, is_primary=True).update(is_primary=False)

    media = PropertyMedia.objects.create(
        property=prop,
        url=url,
        media_type=media_type,
        is_primary=is_primary
    )
    return media

def update_property_media_service(user, media_id, **kwargs):
    """
    Updates a media record. Handles primary image demotion if is_primary is set to True.
    """
    try:
        media = PropertyMedia.objects.get(id=media_id)
    except PropertyMedia.DoesNotExist:
        raise Exception("Media not found.")

    # IDOR check crossing the relationship
    if media.property.owner != user:
        raise Exception("Access denied. You do not own this property's media.")

    # If they are promoting this image to primary, demote the others
    if kwargs.get('is_primary') is True:
        PropertyMedia.objects.filter(property=media.property, is_primary=True).update(is_primary=False)

    for key, value in kwargs.items():
        if value is not None:
            setattr(media, key, value)
            
    media.save()
    return media

def delete_property_media_service(user, media_id):
    """
    Hard deletes a media record for a property you own.
    """
    try:
        media = PropertyMedia.objects.get(id=media_id)
    except PropertyMedia.DoesNotExist:
        raise Exception("Media not found.")

    if media.property.owner != user:
        raise Exception("Access denied. You cannot delete this media.")

    # Hard delete because PropertyMedia does not inherit SoftDeleteModel
    media.delete()
    return True

def assign_property_amenities_service(user, property_id, amenity_ids):
    """
    Assigns a list of amenities to a property. Overwrites existing ones.
    """
    try:
        prop = Property.objects.get(id=property_id, is_deleted=False)
    except Property.DoesNotExist:
        raise Exception("Property not found.")

    if prop.owner != user:
        raise Exception("Access denied. You cannot modify amenities for someone else's property.")

    # Django's .set() automatically handles clearing old relationships and adding new ones
    prop.amenities.set(amenity_ids)
    return prop

def search_properties_service(
    city=None, district=None, min_bedrooms=None, max_bedrooms=None,
    min_area=None, max_area=None, property_type_id=None
):
    """
    Searches properties based on advanced filters.
    Returns a Django QuerySet with prefetching to avoid N+1 queries.
    """
    # Start with all non-deleted properties, prefetching relations
    qs = Property.objects.filter(is_deleted=False).select_related(
        'property_type', 'location', 'owner'
    ).prefetch_related('amenities', 'media')
    
    # Text-based location filters (case-insensitive)
    if city:
        qs = qs.filter(location__city__icontains=city)
    if district:
        qs = qs.filter(location__district__icontains=district)
        
    # Numeric range filters
    if min_bedrooms is not None:
        qs = qs.filter(bedrooms__gte=min_bedrooms)
    if max_bedrooms is not None:
        qs = qs.filter(bedrooms__lte=max_bedrooms)
    if min_area is not None:
        qs = qs.filter(area__gte=min_area)
    if max_area is not None:
        qs = qs.filter(area__lte=max_area)
        
    # Exact relational filter
    if property_type_id:
        qs = qs.filter(property_type_id=property_type_id)
        
    # Default ordering is required for consistent pagination
    return qs.order_by('-created_at')

def search_listings_service(
    listing_type=None, min_price=None, max_price=None,
    city=None, district=None, min_bedrooms=None, max_bedrooms=None,
    property_type_id=None
):
    """
    Advanced search for ACTIVE listings joining Property attributes.
    Uses select_related and prefetch_related to prevent N+1 query performance issues.
    """
    # Base query: only active listings for non-deleted properties
    qs = Listing.objects.filter(
        status=Listing.ListingStatus.ACTIVE,
        is_deleted=False,
        property__is_deleted=False
    ).select_related(
        'agent',
        'property',
        'property__location',
        'property__property_type',
        'property__owner'
    ).prefetch_related('property__amenities', 'property__media')
    
    # Listing specific filters
    if listing_type:
        qs = qs.filter(listing_type=listing_type)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
        
    # Property specific filters (joining across the relationship)
    if city:
        qs = qs.filter(property__location__city__icontains=city)
    if district:
        qs = qs.filter(property__location__district__icontains=district)
    if min_bedrooms is not None:
        qs = qs.filter(property__bedrooms__gte=min_bedrooms)
    if max_bedrooms is not None:
        qs = qs.filter(property__bedrooms__lte=max_bedrooms)
    if property_type_id:
        qs = qs.filter(property__property_type_id=property_type_id)
        
    return qs.order_by('-created_at')

def create_property_type_service(user, name):
    if not user.is_staff and not user.is_superuser:
        raise Exception("Access denied. Only admins can create property types.")
    return PropertyType.objects.create(name=name)

def create_amenity_service(user, name):
    if not user.is_staff and not user.is_superuser:
        raise Exception("Access denied. Only admins can create amenities.")
    return Amenity.objects.create(name=name)