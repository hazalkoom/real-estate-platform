from .models import Property, Location, PropertyType

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