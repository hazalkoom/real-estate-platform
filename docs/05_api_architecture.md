# 05 — API Architecture

## Decision

The platform will use **GraphQL as its primary API**.

GraphQL is chosen because the application exposes highly connected property data to multiple clients with potentially different data requirements. Learning GraphQL is also an explicit project goal.

REST remains a valid alternative, but is not the primary API. gRPC is not needed for the current modular monolith.

## Why GraphQL fits

Property data is highly connected:

- Property
- Listing
- Location
- Media
- Amenities
- AI predictions
- Owner/agent information
- Favorites
- Viewings
- Messages

Web and mobile may need different subsets of the same data. GraphQL lets each client request the exact fields and relationships it needs through one schema.

## Why not REST

REST could implement the entire platform successfully. The reason for choosing GraphQL is flexibility when client data requirements diverge.

This is a trade-off, not a claim that GraphQL is universally better.

## Why not gRPC

gRPC is well suited to service-to-service communication and distributed systems. Our application is currently a modular monolith, so network-based gRPC communication would add unnecessary complexity.

It can be reconsidered if a module is later extracted into an independent service.

## API responsibilities

The GraphQL API will define:

- Queries
- Mutations
- Types
- Relationships
- Input types
- Validation
- Error handling
- Authentication context
- Authorization
- Pagination
- Filtering
- Sorting
- Query complexity/depth protection

Real-time communication will be considered separately.

## Architectural position

```text
Web / Mobile
     ↓
GraphQL API
     ↓
Resolvers
     ↓
Application Services
     ↓
Repositories
     ↓
Django ORM
     ↓
PostgreSQL
```

Resolvers should not contain core business logic. They translate GraphQL operations into application/service calls.

## Important concerns

GraphQL introduces concerns that must be handled deliberately:

- N+1 database queries
- Query depth and complexity
- Authorization
- Pagination
- Caching
- Rate limiting
- Error handling
- File/media upload strategy

## Principles

1. Keep the schema understandable.
2. Keep business logic outside resolvers.
3. Reuse application services.
4. Do not expose database structure directly as the public API.
5. Protect expensive queries.
6. Paginate large collections.
7. Make authorization explicit.
8. Prefer simple solutions before adding infrastructure.
