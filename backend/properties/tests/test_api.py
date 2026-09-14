import pytest
from users.auth import generate_tokens
from django.contrib.auth import get_user_model
from properties.models import PropertyType

User = get_user_model()

@pytest.mark.django_db
def test_create_property_success_as_owner(client):
    owner = User.objects.create_user(email="owner@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(owner)
    
    ptype = PropertyType.objects.create(name="Villa")
    
    mutation = f"""
        mutation {{
          createProperty(input: {{
            propertyTypeId: "{ptype.id}",
            bedrooms: 4,
            bathrooms: 3,
            area: 250.5,
            description: "Beautiful place",
            location: {{
              city: "Cairo",
              district: "New Cairo",
              address: "Street 10"
            }}
          }}) {{
            id
            area
            owner {{ email }}
          }}
        }}
    """
    
    response = client.post(
        '/graphql/', 
        {'query': mutation}, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    
    data = response.json()
    assert "errors" not in data
    assert data["data"]["createProperty"]["owner"]["email"] == "owner@example.com"

@pytest.mark.django_db
def test_create_property_rejected_as_agent(client):
    agent = User.objects.create_user(email="agent@example.com", password="Secure123!", is_agent=True)
    access, _ = generate_tokens(agent)
    
    ptype = PropertyType.objects.create(name="Apartment")
    
    mutation = f"""
        mutation {{
          createProperty(input: {{
            propertyTypeId: "{ptype.id}",
            bedrooms: 2,
            bathrooms: 1,
            area: 100.0,
            description: "Should fail",
            location: {{
              city: "Cairo",
              district: "Maadi",
              address: "Street 9"
            }}
          }}) {{ id }}
        }}
    """
    
    response = client.post(
        '/graphql/', 
        {'query': mutation}, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    
    data = response.json()
    assert "errors" in data
    assert "restricted to Property Owners only" in data["errors"][0]["message"]