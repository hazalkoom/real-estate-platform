from django.contrib.auth import authenticate
from .auth import generate_tokens

def authenticate_user(request, email, password):
    """
    Handles the business logic for verifying credentials and generating tokens.
    """
    user = authenticate(request=request, email=email, password=password)
    
    if not user:
        raise Exception("Invalid credentials. Learn to type your password, ya ghabi.")
    
    if not user.is_active:
        raise Exception("This account has been deactivated.")

    access, refresh = generate_tokens(user)
    
    return user, access, refresh