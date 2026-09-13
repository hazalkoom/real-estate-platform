import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from .types import UserType
from .services import authenticate_user

# --- INPUTS & PAYLOADS ---
@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    user: UserType

@strawberry.input
class RegisterInput:
    email: str
    password: str
    first_name: str
    last_name: str
    is_owner: bool = False
    is_agent: bool = False

# --- QUERIES ---
@strawberry.type
class Query:
    users: list[UserType] = strawberry_django.field()

# --- MUTATIONS ---
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, info: strawberry.Info, input: LoginInput) -> AuthPayload:
        request = info.context.request
        
        auth_async = sync_to_async(authenticate_user, thread_sensitive=True)
        
        # Await the execution
        user, access, refresh = await auth_async(
            request=request,
            email=input.email, 
            password=input.password
        )
        
        return AuthPayload(
            access_token=access,
            refresh_token=refresh,
            user=user
        )


    @strawberry.mutation
    async def register(self, input: RegisterInput) -> AuthPayload:
        from .services import register_user
        
        # Wrap the synchronous database creation in a thread
        register_async = sync_to_async(register_user, thread_sensitive=True)
        
        user, access, refresh = await register_async(
            email=input.email,
            password=input.password,
            first_name=input.first_name,
            last_name=input.last_name,
            is_owner=input.is_owner,
            is_agent=input.is_agent
        )
        
        return AuthPayload(
            access_token=access,
            refresh_token=refresh,
            user=user
        )