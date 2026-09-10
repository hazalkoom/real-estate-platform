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

## Framework Choice: Strawberry GraphQL

We choose **Strawberry GraphQL (`strawberry-graphql-django`)** as our Python GraphQL framework.

### Why Strawberry:
- **Type-Hint Native:** Built around modern Python dataclasses and type annotations, perfectly aligning with `mypy`.
- **First-class Django Integration:** Offers automatic filter generation, permission classes, and integration with Django ORM through `strawberry-django`.
- **Async & Subscriptions:** Seamlessly supports ASGI/async resolvers and WebSocket subscriptions (`graphql-ws`).
- **DataLoaders:** Native built-in DataLoader support for batching queries and eliminating N+1 database bottlenecks.

---

## Solving N+1 Queries: DataLoaders

GraphQL resolvers execute independently for each nested field, which naturally causes N+1 queries if unmanaged.

We address this with two complementary patterns:
1. **Strawberry DataLoaders:** For relation fields resolved across multiple entities (e.g., fetching property owner info or location details in a single `SELECT ... WHERE id IN (...)` batch query).
2. **ORM Pre-fetching:** Using `select_related()` (for foreign keys) and `prefetch_related()` (for many-to-many like amenities) at the repository / service query root.

---

## Pagination Standard

All large collections (properties, listings, messages, notifications) will use **Connection / Cursor-based Pagination** (Relay-style):
- Fields: `edges { cursor node }`, `pageInfo { hasNextPage endCursor }`
- Arguments: `first: Int`, `after: String`
- Max limit: Enforce a server-side maximum (e.g., `first <= 50`) to prevent abuse and denial-of-service.

---

## File & Media Uploads

While standard GraphQL mutations handle data, binary media uploads will use:
- Direct S3-compatible pre-signed URLs (or dedicated REST endpoint `/api/media/upload/`), with the resulting URL/ID registered via a GraphQL mutation `addPropertyMedia`.

---

## Principles

1. Keep the schema understandable and type-safe.
2. Keep business logic outside resolvers — resolvers only adapt GraphQL to Application Services.
3. Reuse application services across GraphQL queries, mutations, and background jobs.
4. Do not expose internal database models directly as public API types; use explicit GraphQL types.
5. Protect expensive queries using query depth (max depth 7) and complexity limits.
6. Paginate large collections using cursor-based pagination.
7. Make authorization explicit at both resolver and service levels.
8. Resolve relation fields with DataLoaders or ORM prefetching to prevent N+1 issues.
