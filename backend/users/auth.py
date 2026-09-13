import jwt
from django.conf import settings
from django.utils import timezone

def generate_tokens(user):
    """
    Generates an access token and a refresh token for the given user.
    """
    now = timezone.now()

    access_payload = {
        "user_id": str(user.id),
        "email": user.email,
        "role_owner": user.is_owner,
        "role_agent": user.is_agent,
        "type": "access",
        "exp": now + settings.JWT_ACCESS_EXPIRATION,
        "iat": now,
    }

    refresh_payload = {
        "user_id": str(user.id),
        "type": "refresh",
        "exp": now + settings.JWT_REFRESH_EXPIRATION,
        "iat": now,
    }

    # Encode the tokens using the secret key from settings
    access_token = jwt.encode(access_payload, settings.JWT_SECRET, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET, algorithm="HS256")
    
    return access_token, refresh_token