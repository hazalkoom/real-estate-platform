from django.contrib.auth import authenticate
from .auth import generate_tokens
from django.contrib.auth import get_user_model

User = get_user_model()

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


def register_user(email, password, first_name, last_name, is_owner=False, is_agent=False):
    """
    Handles registering a new user and auto-generating their initial JWT tokens.
    """
    # Check if the idiot is trying to use an email that already exists
    if User.objects.filter(email=email).exists():
        raise Exception("A user with this email already exists, ya hmar.")
    
    # Create the user using the manager we built earlier
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_owner=is_owner,
        is_agent=is_agent
    )
    
    # Auto-login the user after registration
    access, refresh = generate_tokens(user)
    
    return user, access, refresh