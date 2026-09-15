import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from .types import PropertyNode, ListingNode, AmenityNode, PropertyTypeNode
from users.permissions import IsOwner, IsAgent

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

@strawberry.input
class ListingInput:
    property_id: strawberry.ID
    listing_type: str
    price: float

@strawberry.input
class UpdatePropertyInput:
    property_id: strawberry.ID
    bedrooms: int | None = None
    bathrooms: int | None = None
    area: float | None = None
    description: str | None = None


@strawberry.input
class UpdateListingInput:
    listing_id: strawberry.ID
    listing_type: str | None = None
    status: str | None = None
    price: float | None = None

@strawberry.input
class AddPropertyMediaInput:
    property_id: strawberry.ID
    url: str
    media_type: str = "image"
    is_primary: bool = False

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

    @strawberry.mutation(permission_classes=[IsAgent])
    async def create_listing(self, info: strawberry.Info, input: ListingInput) -> ListingNode:
        from .services import create_listing_service
        
        request = info.context.request
        
        create_async = sync_to_async(create_listing_service, thread_sensitive=True)
        return await create_async(
            agent=request.user,  # Injected securely by the IsAgent guard
            property_id=input.property_id,
            listing_type=input.listing_type,
            price=input.price
        )

    @strawberry.mutation(permission_classes=[IsOwner])
    async def update_property(self, info: strawberry.Info, input: UpdatePropertyInput) -> PropertyNode:
        from .services import update_property_service
        
        request = info.context.request
        update_async = sync_to_async(update_property_service, thread_sensitive=True)
        
        # We pass the input fields as kwargs. Strawberry unwraps them nicely.
        return await update_async(
            user=request.user,
            property_id=input.property_id,
            bedrooms=input.bedrooms,
            bathrooms=input.bathrooms,
            area=input.area,
            description=input.description
        )

    @strawberry.mutation(permission_classes=[IsOwner])
    async def delete_property(self, info: strawberry.Info, property_id: strawberry.ID) -> bool:
        from .services import delete_property_service
        
        request = info.context.request
        delete_async = sync_to_async(delete_property_service, thread_sensitive=True)
        
        return await delete_async(user=request.user, property_id=property_id)

    @strawberry.mutation(permission_classes=[IsAgent])
    async def update_listing(self, info: strawberry.Info, input: UpdateListingInput) -> ListingNode:
        from .services import update_listing_service
        
        request = info.context.request
        update_async = sync_to_async(update_listing_service, thread_sensitive=True)
        
        return await update_async(
            user=request.user,
            listing_id=input.listing_id,
            listing_type=input.listing_type,
            status=input.status,
            price=input.price
        )

    @strawberry.mutation(permission_classes=[IsAgent])
    async def delete_listing(self, info: strawberry.Info, listing_id: strawberry.ID) -> bool:
        from .services import delete_listing_service
        
        request = info.context.request
        delete_async = sync_to_async(delete_listing_service, thread_sensitive=True)
        
        return await delete_async(user=request.user, listing_id=listing_id)

    @strawberry.mutation(permission_classes=[IsOwner])
    async def add_property_media(self, info: strawberry.Info, input: AddPropertyMediaInput) -> PropertyMediaNode:
        from .services import add_property_media_service
        
        request = info.context.request
        add_async = sync_to_async(add_property_media_service, thread_sensitive=True)
        
        return await add_async(
            user=request.user,
            property_id=input.property_id,
            url=input.url,
            media_type=input.media_type,
            is_primary=input.is_primary
        )