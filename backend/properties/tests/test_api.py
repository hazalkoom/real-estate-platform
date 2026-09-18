import pytest
from users.auth import generate_tokens
from django.contrib.auth import get_user_model
from properties.models import Amenity, Listing, PropertyType
from properties.services import create_listing_service, create_property_service

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

@pytest.mark.django_db
def test_update_listing_success(client):
    owner = User.objects.create_user(email="list_owner2@example.com", password="Secure123!", is_owner=True)
    agent = User.objects.create_user(email="list_updater@example.com", password="Secure123!", is_agent=True)
    access, _ = generate_tokens(agent)
    
    ptype = PropertyType.objects.create(name="Villa")
    from properties.services import create_property_service, create_listing_service
    prop = create_property_service(
        user=owner, property_type_id=ptype.id, bedrooms=3, bathrooms=2, area=200.0, description="Test",
        location_data={"city": "Cairo", "district": "Zamalek", "address": "123"}
    )
    listing = create_listing_service(agent=agent, property_id=prop.id, listing_type="SALE", price=5000000.00)
    
    mutation = f"""
        mutation {{
          updateListing(input: {{
            listingId: "{listing.id}",
            price: 4500000.00,
            status: "PENDING"
          }}) {{ id price status }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    # Cast to float because GraphQL serializes Decimals to Strings!
    assert float(data["data"]["updateListing"]["price"]) == 4500000.00
    assert data["data"]["updateListing"]["status"] == "PENDING"

@pytest.mark.django_db
def test_delete_listing_idor_prevention(client):
    owner = User.objects.create_user(email="list_owner3@example.com", password="Secure123!", is_owner=True)
    agent1 = User.objects.create_user(email="good_agent@example.com", password="Secure123!", is_agent=True)
    agent2 = User.objects.create_user(email="bad_agent@example.com", password="Secure123!", is_agent=True)
    
    # Authenticate as the BAD agent
    access, _ = generate_tokens(agent2)
    
    ptype = PropertyType.objects.create(name="Apartment")
    from properties.services import create_property_service, create_listing_service
    prop = create_property_service(
        user=owner, property_type_id=ptype.id, bedrooms=1, bathrooms=1, area=50.0, description="Test",
        location_data={"city": "Cairo", "district": "Maadi", "address": "123"}
    )
    
    # Agent 1 creates the listing
    listing = create_listing_service(agent=agent1, property_id=prop.id, listing_type="RENT", price=10000.00)
    
    # Agent 2 tries to delete Agent 1's listing
    mutation = f"""
        mutation {{
          deleteListing(listingId: "{listing.id}")
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" in data
    assert "cannot delete another agent's listing" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_add_property_media_success(client):
    owner = User.objects.create_user(email="api_media@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(owner)
    
    ptype = PropertyType.objects.create(name="Cabin")
    from properties.services import create_property_service
    prop = create_property_service(
        user=owner, property_type_id=ptype.id, bedrooms=1, bathrooms=1, area=50.0, description="Test",
        location_data={"city": "Cairo", "district": "Maadi", "address": "123"}
    )
    
    mutation = f"""
        mutation {{
          addPropertyMedia(input: {{
            propertyId: "{prop.id}",
            url: "https://mybucket.com/house.jpg",
            isPrimary: true
          }}) {{ id url isPrimary }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["addPropertyMedia"]["url"] == "https://mybucket.com/house.jpg"
    assert data["data"]["addPropertyMedia"]["isPrimary"] is True

@pytest.mark.django_db
def test_add_property_media_idor_prevention(client):
    owner1 = User.objects.create_user(email="real_media_owner@example.com", password="Secure123!", is_owner=True)
    owner2 = User.objects.create_user(email="fake_media_owner@example.com", password="Secure123!", is_owner=True)
    
    # Authenticate as the FAKE owner
    access, _ = generate_tokens(owner2)
    
    ptype = PropertyType.objects.create(name="Flat")
    from properties.services import create_property_service
    prop = create_property_service(
        user=owner1, property_type_id=ptype.id, bedrooms=1, bathrooms=1, area=50.0, description="Test",
        location_data={"city": "Cairo", "district": "Maadi", "address": "123"}
    )
    
    mutation = f"""
        mutation {{
          addPropertyMedia(input: {{
            propertyId: "{prop.id}",
            url: "https://mybucket.com/hacker.jpg",
            isPrimary: true
          }}) {{ id }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" in data
    assert "cannot add pictures to someone else's property" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_update_property_media_success(client):
    owner = User.objects.create_user(email="api_media_upd@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(owner)
    
    ptype = PropertyType.objects.create(name="Cabin 2")
    from properties.services import create_property_service, add_property_media_service
    prop = create_property_service(
        user=owner, property_type_id=ptype.id, bedrooms=1, bathrooms=1, area=50.0, description="Test",
        location_data={"city": "Cairo", "district": "Maadi", "address": "123"}
    )
    media = add_property_media_service(owner, prop.id, "http://old.com/pic.jpg")
    
    mutation = f"""
        mutation {{
          updatePropertyMedia(input: {{
            mediaId: "{media.id}",
            url: "http://new.com/pic.jpg"
          }}) {{ id url }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["updatePropertyMedia"]["url"] == "http://new.com/pic.jpg"

@pytest.mark.django_db
def test_delete_property_media_idor_prevention(client):
    owner1 = User.objects.create_user(email="real_owner_del@example.com", password="Secure123!", is_owner=True)
    owner2 = User.objects.create_user(email="hacker_del@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(owner2)
    
    ptype = PropertyType.objects.create(name="Flat 2")
    from properties.services import create_property_service, add_property_media_service
    prop = create_property_service(
        user=owner1, property_type_id=ptype.id, bedrooms=1, bathrooms=1, area=50.0, description="Test",
        location_data={"city": "Cairo", "district": "Maadi", "address": "123"}
    )
    media = add_property_media_service(owner1, prop.id, "http://pic.com/1.jpg")
    
    mutation = f"""
        mutation {{
          deletePropertyMedia(mediaId: "{media.id}")
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" in data
    assert "Access denied" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_assign_property_amenities_success(client):
    owner = User.objects.create_user(email="api_amenity@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(owner)
    
    ptype = PropertyType.objects.create(name="Townhouse")
    from properties.services import create_property_service
    prop = create_property_service(
        user=owner, 
        property_type_id=ptype.id, 
        bedrooms=1, 
        bathrooms=1, 
        area=50.0, 
        description="Test", 
        location_data={"city": "Cairo", "district": "Maadi", "address": "123"}
    )
    
    a1 = Amenity.objects.create(name="WiFi")
    a2 = Amenity.objects.create(name="Parking")
    
    mutation = f"""
        mutation {{
          assignPropertyAmenities(input: {{
            propertyId: "{prop.id}",
            amenityIds: ["{a1.id}", "{a2.id}"]
          }}) {{
            id
            amenities {{ name }}
          }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    assert len(data["data"]["assignPropertyAmenities"]["amenities"]) == 2

@pytest.mark.django_db
def test_assign_property_amenities_idor(client):
    owner = User.objects.create_user(email="real_amenity_owner@example.com", password="Secure123!", is_owner=True)
    hacker = User.objects.create_user(email="fake_amenity_owner@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(hacker)
    
    ptype = PropertyType.objects.create(name="Villa 2")
    from properties.services import create_property_service
    prop = create_property_service(
        user=owner, 
        property_type_id=ptype.id, 
        bedrooms=1, 
        bathrooms=1, 
        area=50.0, 
        description="Test", 
        location_data={"city": "Cairo", "district": "Maadi", "address": "123"}
    )
    a1 = Amenity.objects.create(name="Garden")
    
    mutation = f"""
        mutation {{
          assignPropertyAmenities(input: {{
            propertyId: "{prop.id}",
            amenityIds: ["{a1.id}"]
          }}) {{ id }}
        }}
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" in data
    assert "cannot modify amenities" in data["errors"][0]["message"]

@pytest.mark.django_db
def test_search_properties_api(client):
    owner = User.objects.create_user(email="api_search@example.com", password="Secure123!", is_owner=True)
    ptype = PropertyType.objects.create(name="Chalet Search")
    
    from properties.services import create_property_service
    create_property_service(owner, ptype.id, 2, 1, 100.0, "Small", {"city": "Giza", "district": "Dokki", "address": "1"})
    create_property_service(owner, ptype.id, 6, 4, 500.0, "Big", {"city": "Giza", "district": "Zayed", "address": "2"})
    
    query = """
        query {
          searchProperties(city: "Giza", minBedrooms: 4) {
            id
            bedrooms
            area
            location { city }
          }
        }
    """
    
    # Notice we don't need HTTP_AUTHORIZATION here. Searching is public.
    response = client.post('/graphql/', {'query': query}, content_type='application/json')
    data = response.json()
    
    assert "errors" not in data
    results = data["data"]["searchProperties"]
    
    # Should only return the "Big" property in Zayed
    assert len(results) == 1
    assert results[0]["bedrooms"] == 6

@pytest.mark.django_db
def test_search_listings_api(client):
    owner = User.objects.create_user(email="api_list_search@example.com", password="Secure123!", is_owner=True)
    agent = User.objects.create_user(email="api_list_agent@example.com", password="Secure123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Chalet List Search")
    
    
    prop = create_property_service(owner, ptype.id, 2, 1, 100.0, "Small", {"city": "Giza", "district": "Dokki", "address": "1"})
    create_listing_service(agent, prop.id, "SALE", 5000000.0)
    
    query = """
        query {
          searchListings(city: "Giza", maxPrice: 6000000.0) {
            id
            price
            listingType
            property {
              bedrooms
              location { city }
            }
          }
        }
    """
    
    # Unauthenticated users can search listings
    response = client.post('/graphql/', {'query': query}, content_type='application/json')
    data = response.json()
    
    assert "errors" not in data
    results = data["data"]["searchListings"]
    
    assert len(results) == 1
    assert float(results[0]["price"]) == 5000000.0
    assert results[0]["property"]["location"]["city"] == "Giza"

@pytest.mark.django_db
def test_single_item_fetching(client):
    owner = User.objects.create_user(email="single_owner@example.com", password="Secure123!", is_owner=True)
    agent = User.objects.create_user(email="single_agent@example.com", password="Secure123!", is_agent=True)
    ptype = PropertyType.objects.create(name="Single Test Type")
    
    from properties.services import create_property_service, create_listing_service
    prop = create_property_service(owner, ptype.id, 2, 2, 150.0, "Desc", {"city": "Cairo", "district": "Maadi", "address": "1"})
    listing = create_listing_service(agent, prop.id, "SALE", 3000000.0)
    
    query = f"""
        query {{
          listing(pk: "{listing.id}") {{
            id
            price
            property {{ bedrooms }}
          }}
        }}
    """
    
    response = client.post('/graphql/', {'query': query}, content_type='application/json')
    data = response.json()
    
    assert "errors" not in data
    assert float(data["data"]["listing"]["price"]) == 3000000.0

@pytest.mark.django_db
def test_admin_mutations_success(client):
    # Create an admin user
    admin = User.objects.create_user(email="admin@example.com", password="Secure123!", is_superuser=True, is_staff=True)
    access, _ = generate_tokens(admin)
    
    mutation = """
        mutation {
          createAmenity(name: "Jacuzzi") { id name }
        }
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["createAmenity"]["name"] == "Jacuzzi"

@pytest.mark.django_db
def test_admin_mutations_rejected_for_normal_users(client):
    hacker = User.objects.create_user(email="hacker_admin@example.com", password="Secure123!", is_owner=True)
    access, _ = generate_tokens(hacker)
    
    mutation = """
        mutation {
          createPropertyType(name: "Penthouse") { id name }
        }
    """
    
    response = client.post('/graphql/', {'query': mutation}, content_type='application/json', HTTP_AUTHORIZATION=f"Bearer {access}")
    data = response.json()
    
    assert "errors" in data
    assert "Only admins can create property types" in data["errors"][0]["message"]


@pytest.mark.django_db
def test_admin_mutations_rejected_for_unauthenticated_users(client):
    mutation_pt = """
        mutation {
          createPropertyType(name: "Penthouse Unauth") { id name }
        }
    """
    res_pt = client.post('/graphql/', {'query': mutation_pt}, content_type='application/json')
    assert "Authentication required" in res_pt.json()["errors"][0]["message"]

    mutation_am = """
        mutation {
          createAmenity(name: "Sauna Unauth") { id name }
        }
    """
    res_am = client.post('/graphql/', {'query': mutation_am}, content_type='application/json')
    assert "Authentication required" in res_am.json()["errors"][0]["message"]