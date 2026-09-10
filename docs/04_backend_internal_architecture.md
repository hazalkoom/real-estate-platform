# System Architecture — Backend Internal Architecture

## Decision

The backend will use a clean layered structure inside the modular monolith, oriented around the **GraphQL primary API** (with secondary REST endpoints reserved for specific concerns like health checks or direct binary uploads).

The standard request flow is:

```text
GraphQL / HTTP Request
     ↓
URL / Routing (/graphql)
     ↓
Middleware (CORS, Logging, Auth Context)
     ↓
GraphQL Resolvers (Queries / Mutations)
     ↓
Input Validation (Pydantic / Strawberry Input Types)
     ↓
Application Service
     ↓
Repository / QuerySet Layer
     ↓
Django Model / ORM
     ↓
PostgreSQL
```

Not every operation must use every layer. The layers exist to keep responsibilities clear.

---

## 1. URL / Routing

Responsible for routing the request to the GraphQL schema endpoint or specialized utility endpoints.

```text
POST /graphql
        ↓
GraphQL View / Handler
```

URLs should not contain business logic.

---

## 2. Middleware

Responsible for processing requests/responses around the main endpoint.

Potential responsibilities include:

- Authentication context extraction (dual-mode: cookies for web, Bearer tokens for mobile)
- Request ID generation (`request_id` propagation)
- CORS
- Rate limiting
- Logging and error capture

---

## 3. GraphQL Resolvers (Queries & Mutations)

Responsible for handling the API contract side of the operation:

- Receive incoming GraphQL query, mutation, or subscription requests
- Unpack arguments / typed input objects
- Check field-level authorization / permissions
- Delegate actual business logic to application services
- Shape and return domain objects matching the GraphQL schema types

Resolvers should **never** contain core business logic or raw SQL queries.

---

## 4. Input Validation

Responsible for validating and transforming incoming data before reaching domain services:

- Required fields and types (enforced by the GraphQL schema)
- Complex field constraints and cross-field validation (via Strawberry input validators or Zod/Pydantic schemas)
- Sanitizing string inputs against XSS and injection

---

## 5. Service

Responsible for application / domain / use-case logic.

Examples:

```text
CreateProperty
RequestViewing
AcceptViewing
AddFavorite
SendMessage
```

A service coordinates the operation and applies business rules.

Example:

```text
Request Viewing
      ↓
Check user identity & permissions
      ↓
Verify property / listing availability
      ↓
Enforce business rules (e.g., no overlapping viewings)
      ↓
Persist viewing via repository / ORM
      ↓
Publish domain event (ViewingRequested)
```

Services remain independent of transport details (they do not know whether the request came from GraphQL, a Celery job, or a test).

---

## 6. Repository / QuerySet Layer

Responsible for data access abstraction and query optimization.

Examples:

```text
get_property(id)
find_active_listings(filters)
create_viewing(data)
save_property(property)
```

Conceptually:

```text
Service
   ↓
Repository / Custom QuerySet
   ↓
Django ORM (select_related / prefetch_related)
   ↓
PostgreSQL
```

The service decides **what business data is needed**.
The repository / custom QuerySet decides **how to query and optimize it** (preventing N+1 queries using `select_related` and `prefetch_related`).

*Note:* Repositories provide a boundary for testability and complex queries, rather than redundant boilerplate around simple one-liner model calls.

---

## 7. Django Model / ORM

Responsible for representing database schema, relations, constraints, and providing the Active Record / QuerySet interface.

Example:

```python
class Property(models.Model):
    ...
```

The model contains entity properties and database-level constraints (`UniqueConstraint`, `CheckConstraint`), but not broad multi-entity business workflows.

---

## 8. PostgreSQL

The authoritative persistent relational database storing all structured platform data.

---

## Example Request

A customer requests a viewing:

```text
POST /graphql (Mutation: requestViewing)
       ↓
URL (/graphql)
       ↓
Middleware (Auth context attached)
       ↓
ViewingResolver (mutation: requestViewing)
       ↓
RequestViewingInput (validation)
       ↓
ViewingService.request_viewing(...)
       ↓
ListingRepository / ORM QuerySet
       ↓
Django ORM
       ↓
PostgreSQL
```

After database commit (`transaction.on_commit`), the service publishes a `ViewingRequested` event for the Communication module to dispatch notifications.

---

## Layer Responsibilities

```text
URL
"What endpoint routes this?"

Middleware
"What cross-cutting concerns wrap the request (auth, CORS, tracing)?"

Resolver
"What GraphQL query/mutation was requested and what schema type do we return?"

Input Validation
"Is the incoming GraphQL payload valid in shape and constraints?"

Service
"What domain action should the application perform?"

Repository / QuerySet
"How do we efficiently retrieve or persist the required data?"

Model / ORM
"How is this data modeled, constrained, and mapped to the database?"

PostgreSQL
"Where is authoritative data stored?"
```

---

## Principles

### Keep Layers Focused

Each layer should have one main responsibility.

### Keep Business Logic Out of Views

Views should coordinate HTTP, not contain large business workflows.

### Keep Database Logic Out of Services

Services should ask repositories for data rather than becoming collections of database queries.

### Avoid Unnecessary Abstraction

Not every operation needs every layer.

If a repository adds no useful separation, we should not create one just for the sake of having a repository.

### Keep Modules and Layers Separate

Modules define **business boundaries**.

Layers define **responsibilities inside those modules**.

For example:

```text
Properties Module
│
├── schema/          (GraphQL Types, Queries, Mutations, Resolvers)
├── services/        (Business use-case logic)
├── repositories/    (Query optimization & data-access abstractions)
├── models/          (Django ORM database models)
└── tests/           (Unit, service, and integration tests)
```

The same consistent structure is used across all 5 modules.

---

## Current Architecture

At this stage:

```text
                    Modular Monolith
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
     Modules            Layers          Communication
       │                  │                  │
       │                  │                  ├── Service Calls
       │                  │                  ├── Events
       │                  │                  └── Background Jobs
       │                  │
       ▼                  ▼
 Users              URL
 Properties         Middleware
 Interactions       View
 Communication      Serializer
 AI                 Service
                    Repository
                    Model / ORM
                    PostgreSQL
```

This is the current backend architecture decision. Further architecture decisions will build on it.
