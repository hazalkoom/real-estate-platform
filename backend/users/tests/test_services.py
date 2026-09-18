import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from users.services import (
    register_user, 
    authenticate_user, 
    change_password,
    request_password_reset,
    confirm_password_reset
)

User = get_user_model()

# --- REGISTER TESTS ---

@pytest.mark.django_db
def test_register_user_service_success():
    user, access, refresh = register_user(
        email="service@example.com",
        password="SecurePassword123!",
        first_name="Test",
        last_name="User",
        is_owner=True
    )
    
    assert user.email == "service@example.com"
    assert user.is_owner is True
    assert access is not None
    assert refresh is not None

@pytest.mark.django_db
def test_register_user_service_duplicate_email():
    User.objects.create_user(email="taken@example.com", password="Password123!")
    
    with pytest.raises(Exception, match="already exists"):
        register_user(
            email="taken@example.com",
            password="NewPassword123!",
            first_name="Test",
            last_name="User"
        )

# --- AUTHENTICATE TESTS ---

@pytest.mark.django_db
def test_authenticate_user_service_success(rf):
    request = rf.post('/graphql/')
    User.objects.create_user(email="authservice@example.com", password="SecurePassword123!")
    
    user, access, refresh = authenticate_user(
        request=request, 
        email="authservice@example.com", 
        password="SecurePassword123!"
    )
    
    assert user.email == "authservice@example.com"
    assert access is not None

@pytest.mark.django_db
def test_authenticate_user_service_invalid_credentials(rf):
    request = rf.post('/graphql/')
    User.objects.create_user(email="authfail@example.com", password="SecurePassword123!")
    
    with pytest.raises(Exception, match="Invalid credentials"):
        authenticate_user(
            request=request, 
            email="authfail@example.com", 
            password="WrongPassword!"
        )

# --- CHANGE PASSWORD TESTS ---

@pytest.mark.django_db
def test_change_password_service_success():
    user = User.objects.create_user(email="pwdservice@example.com", password="OldPassword123!")
    
    result = change_password(user, "OldPassword123!", "NewPassword456!")
    assert result is True
    
    user.refresh_from_db()
    assert user.check_password("NewPassword456!") is True

@pytest.mark.django_db
def test_change_password_service_wrong_old_password():
    user = User.objects.create_user(email="badpwd@example.com", password="OldPassword123!")
    
    with pytest.raises(Exception, match="Incorrect old password"):
        change_password(user, "WrongPassword!", "NewPassword456!")

# --- FORGOT PASSWORD TESTS ---

@pytest.mark.django_db
def test_request_password_reset_service_success():
    User.objects.create_user(email="reset_service@example.com", password="OldPassword123!")
    
    result = request_password_reset(email="reset_service@example.com")
    assert result is True
    
    assert len(mail.outbox) == 1
    assert "reset_service@example.com" in mail.outbox[0].to

@pytest.mark.django_db
def test_confirm_password_reset_service_success():
    user = User.objects.create_user(email="confirm_service@example.com", password="OldPassword123!")
    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    result = confirm_password_reset(uidb64=uid, token=token, new_password="BrandNewPassword789!")
    assert result is True
    
    user.refresh_from_db()
    assert user.check_password("BrandNewPassword789!") is True

@pytest.mark.django_db
def test_confirm_password_reset_service_invalid_token():
    user = User.objects.create_user(email="badtoken_service@example.com", password="OldPassword123!")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    with pytest.raises(Exception, match="invalid or expired"):
        confirm_password_reset(uidb64=uid, token="garbage-token", new_password="BrandNewPassword789!")


@pytest.mark.django_db
def test_authenticate_user_service_inactive_account(rf):
    request = rf.post('/graphql/')
    User.objects.create_user(email="inactive@example.com", password="SecurePassword123!", is_active=False)

    with pytest.raises(Exception, match="This account has been deactivated"):
        authenticate_user(request=request, email="inactive@example.com", password="SecurePassword123!")


@pytest.mark.django_db
def test_register_user_weak_password():
    with pytest.raises(Exception, match="Password validation failed"):
        register_user(
            email="weak_pwd@example.com",
            password="123",
            first_name="Weak",
            last_name="User"
        )


@pytest.mark.django_db
def test_change_password_weak_new_password():
    user = User.objects.create_user(email="weak_new_pwd@example.com", password="OldPassword123!")

    with pytest.raises(Exception, match="Password validation failed"):
        change_password(user, "OldPassword123!", "123")


@pytest.mark.django_db
def test_request_password_reset_non_existent_email():
    mail.outbox.clear()
    result = request_password_reset(email="nonexistent@example.com")
    assert result is True
    # Anti-enumeration: returns True but sends no email
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_confirm_password_reset_corrupted_uid():
    with pytest.raises(Exception, match="Invalid reset link"):
        confirm_password_reset(uidb64="!!!corrupted!!!", token="token123", new_password="BrandNewPassword789!")


@pytest.mark.django_db
def test_confirm_password_reset_weak_password():
    user = User.objects.create_user(email="reset_weak@example.com", password="OldPassword123!")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    with pytest.raises(Exception, match="Password validation failed"):
        confirm_password_reset(uidb64=uid, token=token, new_password="123")