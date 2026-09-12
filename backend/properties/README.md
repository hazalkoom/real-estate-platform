# Properties Module

## Overview
This module represents the core inventory domain. It manages real-estate properties, geographical locations, metadata (amenities, types), and market listings.

## Key Architectural Decisions
- **Relational Separation**: `Location` is decoupled from `Property` via a `OneToOneField` to allow specialized geospatial indexing (latitude/longitude) without bloating the main property table.
- **Media Handling**: The `PropertyMedia` table strictly stores metadata and URLs (S3/CDN links). Binary files are never stored in the PostgreSQL database.
- **Asynchronous Mutations**: Data creation relies on Django 5's async ORM capabilities (`acreate`, `aget`) within `AsyncGraphQLView` to prevent blocking the ASGI event loop during high-concurrency writes.

## GraphQL APIs
- `Query.properties`: Returns properties with nested locations and amenities.
- `Query.listings`: Returns market listings (Sale/Rent) tied to properties.
- `Mutation.createProperty`: Asynchronously creates a nested `Location` and `Property` linked to a given user and property type.

## Test Scenarios Covered
- **Model Tests**:
  - `__str__` representations format correctly for the admin panel.
  - `Property` soft-deletion triggers correctly.
  - `Listing` initialization binds correctly to properties and agents.
- **API Tests**:
  - GraphQL mutation successfully creates nested records and returns expected JSON.
  - Decimal serialization properly asserts against String returns (preventing floating-point GraphQL errors).
  - Mutation properly rejects invalid foreign keys (e.g., non-existent owner IDs) with coherent error messages.