from .models import Property, Location, PropertyType, Listing

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
        raise Exception("Property not found. Are you hallucinating IDs?")

    # Check if the property already has a listing to prevent OneToOne constraint crashes
    if hasattr(prop, 'listing'):
        raise Exception("This property is already listed, ya ghabi.")

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
        raise Exception("Access denied. You do not own this property, ya harami.")

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
        raise Exception("Access denied. You are not the agent for this listing, ya harami.")

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