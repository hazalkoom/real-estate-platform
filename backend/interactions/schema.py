import strawberry
from asgiref.sync import sync_to_async

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def toggle_favorite(self, info: strawberry.Info, listing_id: strawberry.ID) -> bool:
        from .services import toggle_favorite_service
        
        request = info.context.request
        if not request.user.is_authenticated:
            raise Exception("Access denied. You must be logged in to favorite a listing.")

        toggle_async = sync_to_async(toggle_favorite_service, thread_sensitive=True)
        return await toggle_async(user=request.user, listing_id=listing_id)
        
@strawberry.type
class Query:
    # We will add queries here later, leave it empty for now
    pass