from django.contrib.auth import authenticate, get_user_model
from .auth import generate_tokens
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

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

def change_password(user, old_password, new_password):
    """
    Verifies the old password and sets the new one.
    """
    if not user.check_password(old_password):
        raise Exception("Incorrect old password. Are you having a stroke?")
    
    user.set_password(new_password)
    user.save()
    return True

def request_password_reset(email):
    """
    Generates a secure token and emails the reset link.
    """
    user = User.objects.filter(email=email).first()
    
    # We return True even if the user doesn't exist to prevent email enumeration attacks.
    # If we threw an error, hackers could use this endpoint to guess registered emails.
    if not user:
        return True
        
    # Encode the user ID securely
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # Generate a one-time use token
    token = default_token_generator.make_token(user)
    
    # We assume your frontend (Angular) will run on port 4200 and have a /reset-password route
    reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
    
    send_mail(
        subject='Real Estate Platform - Password Reset',
        message=f'Click the link to reset your password: {reset_link}\n\nIf you did not request this, ignore this email, ya ghabi.',
        from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return True

def confirm_password_reset(uidb64, token, new_password):
    """
    Validates the token and updates the password.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise Exception("Invalid reset link. The UID is corrupted.")

    if not default_token_generator.check_token(user, token):
        raise Exception("Token is invalid or expired. Request a new one.")

    user.set_password(new_password)
    user.save()
    return True