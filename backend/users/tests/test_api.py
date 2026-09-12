import pytest
from core.schema import schema
from .factories import UserFactory

@pytest.mark.django_db
def test_users_query():
    UserFactory(email="agent@example.com", is_agent=True)
    UserFactory(email="owner@example.com", is_owner=True)

    query = """
        query {
            users {
                email
                isAgent
                isOwner
            }
        }
    """

    result = schema.execute_sync(query)

    assert result.errors is None
    assert len(result.data["users"]) >= 2

    emails = [user["email"] for user in result.data["users"]]
    assert "agent@example.com" in emails
    assert "owner@example.com" in emails