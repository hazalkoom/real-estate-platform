import pytest
from users.auth import generate_tokens
from django.contrib.auth import get_user_model
from properties.models import PropertyType
from properties.models import Listing

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

@pytest.mark.django_db
def test_create_listing_success_as_agent(client):
    owner = User.objects.create_user(email="owner_listing@example.com", password="Secure123!", is_owner=True)
    agent = User.objects.create_user(email="agent_listing@example.com", password="Secure123!", is_agent=True)
    access, _ = generate_tokens(agent)
    
    ptype = PropertyType.objects.create(name="Studio")
    
    # We bypass the API and use the service directly just to set up the property fast
    from properties.services import create_property_service
    prop = create_property_service(
        user=owner, 
        property_type_id=ptype.id, 
        bedrooms=1, bathrooms=1, area=50.0, description="Test", 
        location_data={"city": "Cairo", "district": "Maadi", "address": "St 9"}
    )
    
    mutation = f"""
        mutation {{
          createListing(input: {{
            propertyId: "{prop.id}",
            listingType: "SALE",
            price: 2500000.00
          }}) {{
            id
            listingType
            price
            property {{ id }}
          }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    assert float(data["data"]["createListing"]["price"]) == 2500000.00
    assert data["data"]["createListing"]["listingType"] == "SALE"

@pytest.mark.django_db
def test_create_listing_rejected_as_owner(client):
    owner = User.objects.create_user(email="greedy_owner@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(owner)
    
    mutation = """
        mutation {
          createListing(input: {
            propertyId: "999",
            listingType: "RENT",
            price: 5000.00
          }) { id }
        }
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" in data
    assert "restricted to Real Estate Agents" in data["errors"][0]["message"]


@pytest.mark.django_db
def test_update_property_success(client):
    owner = User.objects.create_user(email="updater@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(owner)
    
    ptype = PropertyType.objects.create(name="Duplex")
    from properties.services import create_property_service
    prop = create_property_service(
        user=owner, property_type_id=ptype.id, bedrooms=2, bathrooms=2, area=150.0, description="Old desc",
        location_data={"city": "Cairo", "district": "Zamalek", "address": "123 Street"}
    )
    
    mutation = f"""
        mutation {{
          updateProperty(input: {{
            propertyId: "{prop.id}",
            description: "Brand new description!"
          }}) {{ id description area }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    # Description updated, but area should remain the same
    assert data["data"]["updateProperty"]["description"] == "Brand new description!"
    assert float(data["data"]["updateProperty"]["area"]) == 150.0

@pytest.mark.django_db
def test_delete_property_idor_prevention(client):
    owner1 = User.objects.create_user(email="victim@example.com", password="Secure123!", is_owner=True)
    owner2 = User.objects.create_user(email="hacker@example.com", password="Secure123!", is_owner=True)
    
    # Authenticate as owner2 (the hacker)
    access, _ = generate_tokens(owner2)
    
    ptype = PropertyType.objects.create(name="Chalet")
    from properties.services import create_property_service
    
    # Property belongs to owner1
    prop = create_property_service(
        user=owner1, property_type_id=ptype.id, bedrooms=1, bathrooms=1, area=50.0, description="Nice",
        location_data={"city": "Alex", "district": "Gleem", "address": "Sea"}
    )
    
    # Hacker tries to delete Victim's property
    mutation = f"""
        mutation {{
          deleteProperty(propertyId: "{prop.id}")
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" in data
    assert "cannot delete someone else's property" in data["errors"][0]["message"]
    
    # Prove it wasn't deleted
    prop.refresh_from_db()
    assert prop.is_deleted is False