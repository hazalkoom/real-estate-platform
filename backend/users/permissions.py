from strawberry.permission import BasePermission
from strawberry.types import Info

class IsAuthenticated(BasePermission):
    message = "You must be logged in with a valid token to perform this action."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        request = info.context.request
        return bool(request.user and request.user.is_authenticated)

class IsOwner(BasePermission):
    message = "Access denied. This endpoint is restricted to Property Owners only."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        request = info.context.request
        # They must be logged in AND have the is_owner flag set to True
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'is_owner', False))

class IsAgent(BasePermission):
    message = "Access denied. This endpoint is restricted to Real Estate Agents only."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        request = info.context.request
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'is_agent', False))