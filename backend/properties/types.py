import strawberry
import strawberry_django
from .models import PropertyType, Amenity, Location, Property, PropertyMedia, Listing
from users.types import UserType

@strawberry_django.type(PropertyType)
class PropertyTypeNode:
    id: strawberry.auto
    name: strawberry.auto

@strawberry_django.type(Amenity)
class AmenityNode:
    id: strawberry.auto
    name: strawberry.auto

@strawberry_django.type(Location)
class LocationNode:
    id: strawberry.auto
    city: strawberry.auto
    district: strawberry.auto
    address: strawberry.auto
    latitude: strawberry.auto
    longitude: strawberry.auto

@strawberry_django.type(PropertyMedia)
class PropertyMediaNode:
    id: strawberry.auto
    url: strawberry.auto
    media_type: strawberry.auto
    is_primary: strawberry.auto

@strawberry_django.type(Property)
class PropertyNode:
    id: strawberry.auto
    bedrooms: strawberry.auto
    bathrooms: strawberry.auto
    area: strawberry.auto
    description: strawberry.auto
    # Relational fields mapped to the types above
    property_type: PropertyTypeNode
    location: LocationNode
    amenities: list[AmenityNode]
    media: list[PropertyMediaNode]
    owner: UserType

@strawberry_django.type(Listing)
class ListingNode:
    id: strawberry.auto
    listing_type: strawberry.auto
    status: strawberry.auto
    price: strawberry.auto
    property: PropertyNode