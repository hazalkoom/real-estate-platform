import strawberry
from asgiref.sync import sync_to_async
import strawberry_django
from datetime import datetime
from .models import TourRequest, Review, Favorite


@strawberry_django.type(TourRequest)
class TourRequestNode:
    id: strawberry.ID
    tour_date: datetime
    status: str
    message: str

@strawberry_django.type(Review)
class ReviewNode:
    id: strawberry.ID
    rating: int
    comment: str

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

    @strawberry.mutation
    async def request_tour(self, info: strawberry.Info, listing_id: strawberry.ID, tour_date: datetime, message: str = "") -> TourRequestNode:
        from .services import request_tour_service
        request = info.context.request
        if not request.user.is_authenticated:
            raise Exception("Access denied. Log in first, ya hmar.")
        
        req_async = sync_to_async(request_tour_service, thread_sensitive=True)
        return await req_async(buyer=request.user, listing_id=listing_id, tour_date=tour_date, message=message)

    @strawberry.mutation
    async def respond_to_tour(self, info: strawberry.Info, tour_id: strawberry.ID, status: str) -> TourRequestNode:
        from .services import respond_to_tour_service
        request = info.context.request
        if not request.user.is_authenticated:
            raise Exception("Access denied. Log in first.")
        
        res_async = sync_to_async(respond_to_tour_service, thread_sensitive=True)
        return await res_async(user=request.user, tour_id=tour_id, new_status=status)

    @strawberry.mutation
    async def create_review(self, info: strawberry.Info, agent_id: strawberry.ID, rating: int, comment: str = "") -> ReviewNode:
        from .services import create_review_service
        request = info.context.request
        
        if not request.user.is_authenticated:
            raise Exception("Access denied. Log in to leave a review.")
            
        rev_async = sync_to_async(create_review_service, thread_sensitive=True)
        return await rev_async(reviewer=request.user, agent_id=agent_id, rating=rating, comment=comment)

@strawberry.type
class Query:
    pass