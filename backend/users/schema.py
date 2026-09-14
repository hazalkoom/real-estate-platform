import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from .types import UserType
from .services import authenticate_user, register_user
from .permissions import IsAuthenticated, IsOwner, IsAgent

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

@strawberry.input
class ChangePasswordInput:
    old_password: str
    new_password: str

@strawberry.input
class PasswordResetRequestInput:
    email: str

@strawberry.input
class PasswordResetConfirmInput:
    uid: str
    token: str
    new_password: str

# --- QUERIES ---
@strawberry.type
class Query:
    users: list[UserType] = strawberry_django.field()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def me(self, info: strawberry.Info) -> UserType:
        # The middleware already loaded the user, so we just return it
        return info.context.request.user

    @strawberry.field(permission_classes=[IsOwner])
    def owner_dashboard(self, info: strawberry.Info) -> str:
        return "Welcome to the owner dashboard. Here is your sensitive financial data."

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

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def change_password(self, info: strawberry.Info, input: ChangePasswordInput) -> bool:
        from .services import change_password
        request = info.context.request
        
        # Wrap the synchronous database operation
        change_pwd_async = sync_to_async(change_password, thread_sensitive=True)
        
        # Execute it using the user object injected by our JWT middleware
        result = await change_pwd_async(
            user=request.user, 
            old_password=input.old_password, 
            new_password=input.new_password
        )
        
        return result

    @strawberry.mutation
    async def request_password_reset(self, input: PasswordResetRequestInput) -> bool:
        from .services import request_password_reset
        
        # Wrap the synchronous database and email sending operations
        reset_async = sync_to_async(request_password_reset, thread_sensitive=True)
        return await reset_async(email=input.email)

    @strawberry.mutation
    async def confirm_password_reset(self, input: PasswordResetConfirmInput) -> bool:
        from .services import confirm_password_reset
        
        confirm_async = sync_to_async(confirm_password_reset, thread_sensitive=True)
        return await confirm_async(
            uidb64=input.uid, 
            token=input.token, 
            new_password=input.new_password
        )