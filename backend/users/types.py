import strawberry
import strawberry_django
from .models import User

@strawberry_django.type(User)
class UserType:
    id: strawberry.auto
    email: strawberry.auto
    first_name: strawberry.auto
    last_name: strawberry.auto
    is_owner: strawberry.auto
    is_agent: strawberry.auto