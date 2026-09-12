import strawberry
import strawberry_django
from .types import UserType

@strawberry.type
class Query:
    users: list[UserType] = strawberry_django.field()