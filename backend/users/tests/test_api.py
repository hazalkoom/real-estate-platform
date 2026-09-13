import pytest
from django.contrib.auth import get_user_model
from core.schema import schema
from .factories import UserFactory

User = get_user_model()

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

@pytest.mark.django_db
def test_login_mutation_success(client):
    User.objects.create_user(email="testlogin@example.com", password="SecurePassword123!")

    mutation = """
        mutation {
          login(input: {
            email: "testlogin@example.com",
            password: "SecurePassword123!"
          }) {
            accessToken
            refreshToken
            user {
              email
            }
          }
        }
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json')
    data = response.json()
    
    assert response.status_code == 200
    assert "errors" not in data, f"GraphQL Errors: {data.get('errors')}"
    
    result = data["data"]["login"]
    assert result["accessToken"] is not None
    assert result["refreshToken"] is not None
    assert result["user"]["email"] == "testlogin@example.com"

@pytest.mark.django_db
def test_register_mutation_success(client):
    mutation = """
        mutation {
          register(input: {
            email: "newagent_test@example.com",
            password: "StrongPassword123!",
            firstName: "Ahmed",
            lastName: "Agent",
            isAgent: true
          }) {
            accessToken
            refreshToken
            user {
              email
              isAgent
            }
          }
        }
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json')
    data = response.json()
    
    assert response.status_code == 200
    assert "errors" not in data, f"GraphQL Errors: {data.get('errors')}"
    
    result = data["data"]["register"]
    assert result["accessToken"] is not None
    assert result["user"]["email"] == "newagent_test@example.com"
    assert result["user"]["isAgent"] is True