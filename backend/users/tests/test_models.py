import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email="normal@example.com", password="password123")
    assert user.email == "normal@example.com"
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.check_password("password123") is True

@pytest.mark.django_db
def test_create_user_no_email():
    with pytest.raises(ValueError, match="You must provide an email address."):
        User.objects.create_user(email="", password="password123")

@pytest.mark.django_db
def test_create_superuser():
    admin = User.objects.create_superuser(email="admin@example.com", password="password123")
    assert admin.is_staff is True
    assert admin.is_superuser is True


@pytest.mark.django_db
def test_soft_delete(db):
    user = User.objects.create_user(email="delete_me@example.com", password="password123")
    assert user.is_deleted is False
    assert user.deleted_at is None
    
    user.soft_delete()
    
    user.refresh_from_db()
    assert user.is_deleted is True
    assert user.deleted_at is not None