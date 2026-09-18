# 🏡 Properties Module

## Overview

The **Properties Module** serves as the core inventory and marketplace engine for the Real Estate Platform. It encapsulates property profiles, geographical location details, multi-image media storage, amenity associations, and active market listings (Sale/Rent).

---

## 🏗️ Architectural & Directory Structure

```text
backend/properties/
├── admin.py          # Django Admin configuration for Property & Listing models
├── apps.py           # Properties AppConfig
├── models.py         # Property, Listing, Location, PropertyMedia, Amenity, PropertyType
├── README.md         # Module documentation
├── schema.py         # Strawberry GraphQL Queries & Mutations
├── services.py       # Domain service layer (business logic, IDOR checks, search filters)
├── types.py          # Strawberry GraphQL type definitions (Nodes)
└── tests/            # Automated test suite
    ├── factories.py  # FactoryBoy factories for test data generation
    ├── test_api.py   # GraphQL integration tests (queries, mutations, permissions)
    ├── test_models.py# Model unit tests (string formatting, soft deletion)
    └── test_services.py # Service layer unit tests (CRUD, IDOR protection, primary media toggle)
```

---

## 🔑 Key Architectural & Security Decisions

1. **Relational Decoupling & Geospatial Readiness (`models.py`)**
   - `Location` is decoupled from `Property` via a `OneToOneField`, isolating coordinate attributes (`latitude`, `longitude`) for future PostGIS geospatial indexing.
   - `Listing` is linked via `OneToOneField` to `Property`, strictly separating physical real estate attributes from dynamic marketplace pricing and listing statuses (`ACTIVE`, `PENDING`, `SOLD`, `RENTED`).
   - `PropertyMedia` stores external asset URLs (S3/Cloudflare R2/CDN) and metadata, ensuring binary payloads never bloat the relational database.

2. **Decoupled Service Layer (`services.py`)**
   - Business workflows are isolated into clean Python functions (`create_property_service`, `create_listing_service`, `search_listings_service`, etc.).
   - GraphQL resolvers remain lightweight orchestration wrappers around domain services using `sync_to_async`.

3. **IDOR Prevention & Object-Level Permissions**
   - Every mutating service enforces strict ownership checks:
     - **Properties & Media**: Only the authenticated property owner (`user == property.owner`) can update, delete, or modify amenities/media.
     - **Listings**: Only authorized agents (`IsAgent` guard and `user == listing.agent`) can manage listings.
     - **Metadata**: Property types and amenities can only be created by staff/administrators.

4. **N+1 Query Prevention & Search Optimization**
   - `search_listings_service` leverages `.select_related('property', 'property__location', 'property__property_type')` to guarantee optimal database query plans when executing complex relational filters across prices, cities, and bedroom counts.

5. **Soft Deletion (`models.py`)**
   - `Property` and `Listing` inherit from `SoftDeleteModel`, retaining historical data and audit trails for past transactions while filtering out deleted records from public search queries.

---

## 📡 GraphQL Operations

### Queries
- `property(pk: ID!)`: Retrieves a single property by primary key.
- `listing(pk: ID!)`: Retrieves a single listing by primary key.
- `properties(pagination: Boolean)`: Paginated query for all active properties.
- `listings(pagination: Boolean)`: Paginated query for all market listings.
- `amenities`: List of all available amenities.
- `propertyTypes`: List of all configured property types.
- `searchProperties(city, district, minBedrooms, maxBedrooms, minArea, maxArea, propertyTypeId, limit, offset)`: Advanced multi-filter property search.
- `searchListings(listingType, minPrice, maxPrice, city, district, minBedrooms, maxBedrooms, propertyTypeId, limit, offset)`: Marketplace search for active listings.

### Mutations
- `createProperty(input: PropertyInput)`: Creates a property with nested location data (`IsOwner`).
- `updateProperty(input: UpdatePropertyInput)`: Updates property attributes with ownership verification (`IsOwner`).
- `deleteProperty(propertyId: ID!)`: Soft deletes a property (`IsOwner`).
- `createListing(input: ListingInput)`: Creates a market listing for a property (`IsAgent`).
- `updateListing(input: UpdateListingInput)`: Updates listing price, type, or status (`IsAgent`).
- `deleteListing(listingId: ID!)`: Soft deletes an active listing (`IsAgent`).
- `addPropertyMedia(input: AddPropertyMediaInput)`: Attaches a media URL and automatically manages primary image designation (`IsOwner`).
- `updatePropertyMedia(input: UpdatePropertyMediaInput)`: Updates media attributes or primary status (`IsOwner`).
- `deletePropertyMedia(mediaId: ID!)`: Hard deletes a media record (`IsOwner`).
- `assignPropertyAmenities(input: AssignPropertyAmenitiesInput)`: Syncs amenity IDs to a property (`IsOwner`).
- `createPropertyType(name: String!)`: Admin mutation to register new property types.
- `createAmenity(name: String!)`: Admin mutation to register new amenities.

---

## 🧪 Testing Strategy

The `properties` test suite contains **34 comprehensive tests** executed via `pytest-django`:

- **`test_models.py`**: Validates string formatting, default field values, soft deletion, and foreign key bindings.
- **`test_services.py`**: Verifies business logic, IDOR protections, primary media toggle behavior, amenity assignment, and search filter querysets.
- **`test_api.py`**: End-to-end GraphQL integration tests validating permissions (`IsOwner`, `IsAgent`, unauthenticated access), payload serializations, and error handling.