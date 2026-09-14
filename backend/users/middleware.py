import jwt
import inspect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import sync_and_async_middleware
from asgiref.sync import sync_to_async

User = get_user_model()

def get_user_from_token(request):
    """Synchronous function to extract and verify the JWT."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return AnonymousUser()
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        
        if not user.is_active:
            return AnonymousUser()
            
        return user
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return AnonymousUser()

@sync_and_async_middleware
def jwt_auth_middleware(get_response):
    """
    Middleware that seamlessly handles both Sync and Async requests, 
    injecting the decoded User into request.user.
    """
    if inspect.iscoroutinefunction(get_response):
        async def middleware(request):
            request.user = await sync_to_async(get_user_from_token, thread_sensitive=True)(request)
            return await get_response(request)
    else:
        def middleware(request):
            request.user = get_user_from_token(request)
            return get_response(request)
            
    return middleware