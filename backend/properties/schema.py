import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from .types import PropertyNode, ListingNode, AmenityNode, PropertyTypeNode
from users.permissions import IsOwner

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
    bedrooms: int
    bathrooms: int
    area: float
    description: str
    location: LocationInput

@strawberry.type
class Query:
    properties: list[PropertyNode] = strawberry_django.field()
    listings: list[ListingNode] = strawberry_django.field()
    amenities: list[AmenityNode] = strawberry_django.field()
    property_types: list[PropertyTypeNode] = strawberry_django.field()

@strawberry.type
class Mutation:
    
    @strawberry.mutation(permission_classes=[IsOwner])
    async def create_property(self, info: strawberry.Info, input: PropertyInput) -> PropertyNode:
        from .services import create_property_service
        
        request = info.context.request
        
        # Convert the Strawberry input into a standard Python dictionary for the service layer
        location_dict = {
            'city': input.location.city,
            'district': input.location.district,
            'address': input.location.address,
            'latitude': input.location.latitude,
            'longitude': input.location.longitude,
        }
        
        create_async = sync_to_async(create_property_service, thread_sensitive=True)
        return await create_async(
            user=request.user,
            property_type_id=input.property_type_id,
            bedrooms=input.bedrooms,
            bathrooms=input.bathrooms,
            area=input.area,
            description=input.description,
            location_data=location_dict
        )