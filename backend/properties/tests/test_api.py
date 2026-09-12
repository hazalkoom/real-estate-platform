import pytest
from users.tests.factories import UserFactory
from properties.tests.factories import PropertyTypeFactory, PropertyFactory, LocationFactory
from properties.models import Property, Listing

@pytest.mark.django_db
def test_create_property_mutation_success(client):
    user = UserFactory(is_owner=True)
    prop_type = PropertyTypeFactory(name="Villa")

    mutation = """
        mutation CreateTestProperty($ownerId: ID!, $propTypeId: ID!) {
          createProperty(
            input: {
              ownerId: $ownerId, 
              propertyTypeId: $propTypeId, 
              bedrooms: 5, 
              bathrooms: 4, 
              area: 350.5, 
              description: "Massive test villa", 
              location: { city: "Alexandria", district: "Smouha", address: "123 Test Ave" }
            }
          ) { id area location { city } owner { email } }
        }
    """
    response = client.post('/graphql/', {'query': mutation, 'variables': {"ownerId": str(user.id), "propTypeId": str(prop_type.id)}}, content_type='application/json')
    
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    
    result = data["data"]["createProperty"]
    # Notice the string comparison, you absolute moron
    assert result["area"] == "350.5"
    assert result["location"]["city"] == "Alexandria"
    assert Property.objects.count() == 1

@pytest.mark.django_db
def test_create_property_mutation_invalid_owner(client):
    prop_type = PropertyTypeFactory(name="Apartment")
    
    mutation = """
        mutation CreateTestProperty($propTypeId: ID!) {
          createProperty(
            input: { ownerId: "99999", propertyTypeId: $propTypeId, bedrooms: 1, bathrooms: 1, area: 50.0, description: "Fake", location: { city: "Cairo", district: "Maadi", address: "123 Fake" } }
          ) { id }
        }
    """
    response = client.post('/graphql/', {'query': mutation, 'variables': {"propTypeId": str(prop_type.id)}}, content_type='application/json')
    
    data = response.json()
    # It should fail because user 99999 doesn't exist
    assert "errors" in data
    assert "User matching query does not exist" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_query_properties_list(client):
    user = UserFactory(is_owner=True)
    prop_type = PropertyTypeFactory(name="Duplex")
    PropertyFactory(owner=user, property_type=prop_type, area=200.00)
    PropertyFactory(owner=user, property_type=prop_type, area=250.00)

    query = """
        query {
            properties { id area owner { email } propertyType { name } }
        }
    """
    response = client.post('/graphql/', {'query': query}, content_type='application/json')
    data = response.json()
    
    assert "errors" not in data
    assert len(data["data"]["properties"]) == 2