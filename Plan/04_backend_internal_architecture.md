# System Architecture — Backend Internal Architecture

## Decision

The backend will use a simple layered structure inside the modular monolith.

The initial request flow is:

```text
HTTP Request
     ↓
URL
     ↓
Middleware
     ↓
View / Controller
     ↓
Serializer / Validation
     ↓
Service
     ↓
Repository
     ↓
Django Model / ORM
     ↓
PostgreSQL
```

Not every operation must use every layer. The layers exist to keep responsibilities clear.

---

## 1. URL

Responsible for routing a request to the correct endpoint.

```text
POST /properties/
        ↓
Property View
```

URLs should not contain business logic.

---

## 2. Middleware

Responsible for processing requests/responses around the main endpoint.

Potential responsibilities include:

- Authentication-related processing
- Logging
- CORS
- Rate limiting
- Other cross-cutting request concerns

Request-specific data validation will generally be handled by serializers rather than custom middleware.

---

## 3. View / Controller

Responsible for handling the HTTP/API side of the operation.

It should:

- Receive the request
- Pass validated data to the appropriate service
- Return the HTTP response
- Select the appropriate status code

It should not contain large amounts of business logic.

In Django REST Framework, DRF Views and ViewSets fill this role.

---

## 4. Serializer / Validation

Responsible for validating and transforming API data.

For incoming data, serializers can check:

- Required fields
- Data types
- Field constraints
- Relationships
- Request-specific validation

For outgoing data, serializers transform application objects into API responses.

---

## 5. Service

Responsible for application/use-case logic.

Examples:

```text
CreateProperty
RequestViewing
AcceptViewing
AddFavorite
SendMessage
```

A service coordinates the operation and applies the necessary business rules.

Example:

```text
Request Viewing
      ↓
Check user
      ↓
Check property/listing
      ↓
Check business rules
      ↓
Create viewing
      ↓
Publish event if necessary
```

Services should not be responsible for HTTP details.

---

## 6. Repository

Responsible for data access.

The repository provides a clear interface for retrieving and storing data.

Examples:

```text
get_property(id)
find_active_listing(property_id)
create_viewing(data)
save_property(property)
```

Conceptually:

```text
Service
   ↓
Repository
   ↓
Django ORM
   ↓
PostgreSQL
```

The service decides **what the application needs**.

The repository decides **how to retrieve or store it**.

Repositories will only be introduced where they provide a useful boundary. We will avoid creating pointless wrappers around simple ORM operations.

---

## 7. Django Model / ORM

Responsible for representing database data and providing the database abstraction.

Example:

```python
class Property(models.Model):
    ...
```

Django's ORM handles communication with PostgreSQL.

The model should not become a dumping ground for unrelated application logic.

---

## 8. PostgreSQL

The main persistent database.

It stores the application's relational data defined by the project database schema.

---

## Example Request

A customer requests a viewing:

```text
POST /viewings/
       ↓
URL
       ↓
Middleware
       ↓
ViewingView
       ↓
ViewingSerializer
       ↓
ViewingService
       ↓
ListingRepository
       ↓
Django ORM
       ↓
PostgreSQL
```

The service may then create the viewing and publish a `ViewingRequested` event for the Communication module.

---

## Layer Responsibilities

```text
URL
"What endpoint handles this?"

Middleware
"What should happen around the request?"

View / Controller
"What HTTP request did we receive and what response should we return?"

Serializer
"Is the API data valid and how should it be represented?"

Service
"What should the application actually do?"

Repository
"How do we get or save the required data?"

Model / ORM
"How is this data represented and persisted?"

PostgreSQL
"Where is the data stored?"
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
├── views
├── serializers
├── services
├── repositories
└── models
```

The same basic structure can be used by other modules where appropriate.

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
