import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from users.permissions import IsAgent, IsOwner
from .services import (
    add_property_media_service,
    assign_property_amenities_service,
    create_amenity_service,
    create_listing_service,
    create_property_service,
    create_property_type_service,
    delete_listing_service,
    delete_property_media_service,
    delete_property_service,
    search_listings_service,
    search_properties_service,
    update_listing_service,
    update_property_media_service,
    update_property_service,
)
from .types import (
    AmenityNode,
    ListingNode,
    PropertyMediaNode,
    PropertyNode,
    PropertyTypeNode,
)


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

@strawberry.input
class UpdatePropertyMediaInput:
    media_id: strawberry.ID
    url: str | None = None
    media_type: str | None = None
    is_primary: bool | None = None

@strawberry.input
class AssignPropertyAmenitiesInput:
    property_id: strawberry.ID
    amenity_ids: list[strawberry.ID]

@strawberry.type
class Query:
    property: PropertyNode = strawberry_django.field()
    listing: ListingNode = strawberry_django.field()
    properties: list[PropertyNode] = strawberry_django.field(pagination=True)
    listings: list[ListingNode] = strawberry_django.field(pagination=True)
    amenities: list[AmenityNode] = strawberry_django.field(pagination=True)
    property_types: list[PropertyTypeNode] = strawberry_django.field(pagination=True)

    @strawberry.field
    async def search_properties(
        self,
        city: str | None = None,
        district: str | None = None,
        min_bedrooms: int | None = None,
        max_bedrooms: int | None = None,
        min_area: float | None = None,
        max_area: float | None = None,
        property_type_id: strawberry.ID | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[PropertyNode]:

        # Call the pure Python service (this doesn't hit the DB yet)
        qs = search_properties_service(
            city=city, district=district,
            min_bedrooms=min_bedrooms, max_bedrooms=max_bedrooms,
            min_area=min_area, max_area=max_area,
            property_type_id=property_type_id
        )
        
        # Safely evaluate the queryset in an async context
        evaluate_qs = sync_to_async(list, thread_sensitive=True)
        return await evaluate_qs(qs[offset : offset + limit])

    @strawberry.field
    async def search_listings(
        self,
        listing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        city: str | None = None,
        district: str | None = None,
        min_bedrooms: int | None = None,
        max_bedrooms: int | None = None,
        property_type_id: strawberry.ID | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[ListingNode]:
        
        qs = search_listings_service(
            listing_type=listing_type,
            min_price=min_price, max_price=max_price,
            city=city, district=district,
            min_bedrooms=min_bedrooms, max_bedrooms=max_bedrooms,
            property_type_id=property_type_id
        )
        
        # Safely evaluate the queryset in an async context
        evaluate_qs = sync_to_async(list, thread_sensitive=True)
        return await evaluate_qs(qs[offset : offset + limit])

@strawberry.type
class Mutation:
    
    @strawberry.mutation(permission_classes=[IsOwner])
    async def create_property(self, info: strawberry.Info, input: PropertyInput) -> PropertyNode:
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
        request = info.context.request
        delete_async = sync_to_async(delete_property_service, thread_sensitive=True)
        
        return await delete_async(user=request.user, property_id=property_id)

    @strawberry.mutation(permission_classes=[IsAgent])
    async def update_listing(self, info: strawberry.Info, input: UpdateListingInput) -> ListingNode:
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
        request = info.context.request
        delete_async = sync_to_async(delete_listing_service, thread_sensitive=True)
        
        return await delete_async(user=request.user, listing_id=listing_id)

    @strawberry.mutation(permission_classes=[IsOwner])
    async def add_property_media(self, info: strawberry.Info, input: AddPropertyMediaInput) -> PropertyMediaNode:
        request = info.context.request
        add_async = sync_to_async(add_property_media_service, thread_sensitive=True)
        
        return await add_async(
            user=request.user,
            property_id=input.property_id,
            url=input.url,
            media_type=input.media_type,
            is_primary=input.is_primary
        )

    @strawberry.mutation(permission_classes=[IsOwner])
    async def update_property_media(self, info: strawberry.Info, input: UpdatePropertyMediaInput) -> PropertyMediaNode:
        request = info.context.request
        update_async = sync_to_async(update_property_media_service, thread_sensitive=True)
        
        return await update_async(
            user=request.user,
            media_id=input.media_id,
            url=input.url,
            media_type=input.media_type,
            is_primary=input.is_primary
        )

    @strawberry.mutation(permission_classes=[IsOwner])
    async def delete_property_media(self, info: strawberry.Info, media_id: strawberry.ID) -> bool:
        request = info.context.request
        delete_async = sync_to_async(delete_property_media_service, thread_sensitive=True)
        
        return await delete_async(user=request.user, media_id=media_id)

    @strawberry.mutation(permission_classes=[IsOwner])
    async def assign_property_amenities(self, info: strawberry.Info, input: AssignPropertyAmenitiesInput) -> PropertyNode:
        request = info.context.request
        assign_async = sync_to_async(assign_property_amenities_service, thread_sensitive=True)
        
        return await assign_async(
            user=request.user,
            property_id=input.property_id,
            amenity_ids=input.amenity_ids
        )

    @strawberry.mutation
    async def create_property_type(self, info: strawberry.Info, name: str) -> PropertyTypeNode:
        request = info.context.request
        
        if not request.user.is_authenticated:
            raise Exception("Authentication required.")
            
        create_async = sync_to_async(create_property_type_service, thread_sensitive=True)
        return await create_async(user=request.user, name=name)

    @strawberry.mutation
    async def create_amenity(self, info: strawberry.Info, name: str) -> AmenityNode:
        request = info.context.request
        
        if not request.user.is_authenticated:
            raise Exception("Authentication required.")
            
        create_async = sync_to_async(create_amenity_service, thread_sensitive=True)
        return await create_async(user=request.user, name=name)