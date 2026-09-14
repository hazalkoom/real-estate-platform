import pytest
from django.contrib.auth import get_user_model
from core.schema import schema
from .factories import UserFactory
from users.auth import generate_tokens

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


@pytest.mark.django_db
def test_login_invalid_credentials(client):
    User.objects.create_user(email="valid@example.com", password="RealPassword123!")
    
    mutation = """
        mutation {
          login(input: { email: "valid@example.com", password: "WrongPassword!" }) {
            accessToken
          }
        }
    """
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json')
    data = response.json()
    
    assert "errors" in data
    assert "Invalid credentials" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_register_duplicate_email(client):
    User.objects.create_user(email="taken@example.com", password="RealPassword123!")
    
    mutation = """
        mutation {
          register(input: {
            email: "taken@example.com", password: "AnyPassword123!", firstName: "A", lastName: "B"
          }) { accessToken }
        }
    """
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json')
    data = response.json()
    
    assert "errors" in data
    assert "already exists" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_owner_dashboard_success(client):
    # Create an OWNER
    user = User.objects.create_user(email="realowner@example.com", password="Password123!", is_owner=True)
    access, _ = generate_tokens(user)
    
    query = "{ ownerDashboard }"
    
    response = client.post(
        '/graphql/', 
        {'query': query}, 
        content_type='application/json',
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    
    data = response.json()
    assert "errors" not in data
    assert data["data"]["ownerDashboard"] == "Welcome to the owner dashboard. Here is your sensitive financial data."

@pytest.mark.django_db
def test_owner_dashboard_rejected_for_agent(client):
    # Create an AGENT (is_owner is False)
    user = User.objects.create_user(email="justanagent@example.com", password="Password123!", is_agent=True)
    access, _ = generate_tokens(user)
    
    query = "{ ownerDashboard }"
    
    response = client.post(
        '/graphql/', 
        {'query': query}, 
        content_type='application/json',
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    
    data = response.json()
    # It must fail and return the explicit permission error
    assert "errors" in data
    assert "restricted to Property Owners only" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_change_password_success(client):
    user = User.objects.create_user(email="pwd@example.com", password="OldPassword123!")
    access, _ = generate_tokens(user)
    
    mutation = """
        mutation {
          changePassword(input: {
            oldPassword: "OldPassword123!",
            newPassword: "NewStrongPassword456!"
          })
        }
    """
    
    response = client.post(
        '/graphql/', 
        {'query': mutation}, 
        content_type='application/json',
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    
    data = response.json()
    assert "errors" not in data
    assert data["data"]["changePassword"] is True
    
    # Verify the database actually updated the hash
    user.refresh_from_db()
    assert user.check_password("NewStrongPassword456!") is True

@pytest.mark.django_db
def test_change_password_wrong_old_password(client):
    user = User.objects.create_user(email="failpwd@example.com", password="OldPassword123!")
    access, _ = generate_tokens(user)
    
    mutation = """
        mutation {
          changePassword(input: {
            oldPassword: "WrongPassword!",
            newPassword: "NewStrongPassword456!"
          })
        }
    """
    
    response = client.post(
        '/graphql/', 
        {'query': mutation}, 
        content_type='application/json',
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    
    data = response.json()
    assert "errors" in data
    assert "Incorrect old password" in data["errors"][0]["message"]