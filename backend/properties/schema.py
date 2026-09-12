import strawberry
import strawberry_django
from .types import PropertyNode, ListingNode, AmenityNode, PropertyTypeNode
from django.contrib.auth import get_user_model
from .models import Property, Location, PropertyType


User = get_user_model()

# --- INPUT TYPES ---
@strawberry.input
class LocationInput:
    city: str
    district: str
    address: str
    latitude: float | None = None
    longitude: float | None = None


@strawberry.input
class PropertyInput:
    property_type_id: strawberry.ID
    owner_id: strawberry.ID  # Temporary! We will use JWT auth context for this later.
    bedrooms: int
    bathrooms: int
    area: float
    description: str
    location: LocationInput

# --- QUERIES ---
@strawberry.type
class Query:
    properties: list[PropertyNode] = strawberry_django.field()
    listings: list[ListingNode] = strawberry_django.field()
    amenities: list[AmenityNode] = strawberry_django.field()
    property_types: list[PropertyTypeNode] = strawberry_django.field()

# --- MUTATIONS ---
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_property(self, input: PropertyInput) -> PropertyNode:
        # 1. Fetch relations using aget() instead of get()
        owner = await User.objects.aget(id=input.owner_id)
        prop_type = await PropertyType.objects.aget(id=input.property_type_id)
        
        # 2. Create the nested Location object using acreate()
        location = await Location.objects.acreate(
            city=input.location.city,
            district=input.location.district,
            address=input.location.address,
            latitude=input.location.latitude,
            longitude=input.location.longitude
        )
        
        # 3. Create the actual Property using acreate()
        property_obj = await Property.objects.acreate(
            owner=owner,
            property_type=prop_type,
            location=location,
            bedrooms=input.bedrooms,
            bathrooms=input.bathrooms,
            area=input.area,
            description=input.description
        )
        
        return property_obj