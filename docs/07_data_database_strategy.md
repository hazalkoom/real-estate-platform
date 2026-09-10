# 07 — Data & Database Strategy

## Decision

The platform will use:

- **PostgreSQL** as the primary source of truth
- **Redis** for selective caching
- A **dedicated vector database** for semantic/AI search
- **Docker** for local database infrastructure
- Django ORM + repositories for normal application data access

The goal is not to add databases everywhere. Each storage technology must have a clear responsibility.

---

## 1. PostgreSQL — Primary Database

PostgreSQL stores the authoritative application data:

- `users` (managed by Django `AbstractBaseUser`, email as username, password hashing)
- `properties` (core property specifications)
- `property_types` (apartments, villas, offices, etc.)
- `locations` (city, district, address, latitude/longitude with GIS indexes)
- `amenities` & `property_amenities` (many-to-many features)
- `property_media` (metadata & URLs pointing to object storage)
- `listings` (status, price, listing type, assigned agent & owner FKs)
- `favorites` (user-property saves with unique constraints & timestamps)
- `viewings` (request status, scheduled times, audit timestamps)
- `conversations` (chat threads linking buyer, seller/agent, and property)
- `messages` (in-thread chat messages with delivery state & timestamps)
- `notifications` (user activity & system alerts with read receipts)
- `reviews` (authenticated buyer reviews & star ratings per property)
- `reports` (moderation queue for fake listings / suspicious users)
- `failed_jobs` (Celery background job retry exhaustion dead-letter records)
- `ai_predictions` & `ai_interactions` (AI outputs & user prompt metadata)

PostgreSQL remains the single source of truth.

### Database Audit & Integrity Standards
1. **Universal Timestamps:** All primary and association tables include `created_at` and `updated_at` (managed via a shared Django `TimeStampedModel` abstract base class).
2. **Soft Deletes:** Critical business records (`properties`, `listings`, `users`) include `is_deleted` and `deleted_at` to preserve referential history and audit trails.
3. **No Redundant Hash Columns:** User passwords are managed by Django's native authentication framework; no raw `password_hash` column is declared independently.
4. **Geospatial Capabilities:** Property `locations` store `latitude` and `longitude` with PostgreSQL indexes (or PostGIS `PointField`) enabling radius queries ("find properties within 5km").

```text
Django
  ↓
Repository / QuerySet
  ↓
Django ORM
  ↓
PostgreSQL
```

### Why PostgreSQL

The domain is highly relational and needs:

- joins
- constraints
- transactions
- indexing
- filtering
- reliable persistence

A document database such as MongoDB is not needed for the core data.

---

## 2. PostgreSQL in Docker

PostgreSQL will run locally in Docker instead of being installed directly on the development machine.

```text
Developer Machine
      ↓
Docker
      ↓
PostgreSQL Container
      ↓
Persistent Docker Volume
```

The container can be recreated without losing database data because PostgreSQL data is stored in a persistent volume.

Benefits:

- isolated development environment
- reproducible setup
- easy cleanup
- easier onboarding
- no full local PostgreSQL installation

Production deployment will be decided later.

---

## 3. Redis — Cache

Redis will be used selectively for data that is expensive or repetitive to fetch or calculate.

Possible cache candidates:

- popular property lists
- frequently viewed property data
- selected search results
- property types and amenities
- expensive AI results
- short-lived derived data

PostgreSQL remains authoritative.

```text
Request
   ↓
Check Redis
   ↓
Cache hit? ── Yes ──> Return
   │
   No
   ↓
PostgreSQL / computation
   ↓
Store temporary result in Redis
   ↓
Return
```

### Rules

- Do not cache everything.
- Use TTLs where appropriate.
- Do not treat Redis as the source of truth.
- Cache only after there is a real reason.
- Cache invalidation must be considered when underlying data changes.

---

## 4. Dedicated Vector Database

A separate vector database will be used to study and implement semantic search.

This is intentionally different from using `pgvector` inside PostgreSQL.

Architecture:

```text
                     ┌── PostgreSQL
Django / AI Layer ───┼── Redis
                     └── Vector Database
```

### Responsibility

The vector database stores embeddings used for semantic similarity search.

Example:

```text
Property description
       ↓
Embedding Model
       ↓
Vector
       ↓
Vector Database
```

A user query follows the same process:

```text
"bright modern apartment suitable for a family"
       ↓
Embedding Model
       ↓
Query Vector
       ↓
Vector Similarity Search
       ↓
Most semantically similar properties
```

### Why use a dedicated vector database

The project intentionally chooses this option for learning purposes.

It allows us to study:

- embeddings
- vector similarity
- semantic search
- vector indexing
- nearest-neighbor search
- metadata filtering
- ranking
- synchronization between relational and vector stores
- vector database operations
- AI search architecture

This adds complexity, but the complexity is intentional because learning vector databases is part of the project goal.

---

## 5. PostgreSQL vs Vector Database

They solve different problems.

### PostgreSQL

Good for structured conditions:

```text
city = Cairo
bedrooms = 3
price <= 4,000,000
listing_type = SALE
status = ACTIVE
```

### Vector Database

Good for semantic meaning:

```text
"family friendly"
"quiet and modern"
"lots of natural light"
"good for working from home"
"similar to this property"
```

Neither replaces the other.

---

## 6. Hybrid Property Search

The long-term AI search can combine both systems.

Example user query:

> Find a 3-bedroom apartment in New Cairo under 4 million that is bright, quiet, and good for a family.

The query contains two kinds of requirements.

### Structured

```text
bedrooms = 3
location = New Cairo
price <= 4,000,000
```

Handled by PostgreSQL.

### Semantic

```text
bright
quiet
good for a family
```

Handled by the vector database.

Possible flow:

```text
Natural-language query
        ↓
AI / Query Parser
        ↓
┌─────────────────────┐
│ Structured filters  │
│ Semantic text       │
└──────────┬──────────┘
           ↓
     ┌─────┴─────┐
     ↓           ↓
PostgreSQL   Vector DB
     ↓           ↓
     └─────┬─────┘
           ↓
    Merge / rank
           ↓
     Final results
```

Exact ranking strategy will be designed in the AI/ML architecture stage.

---

## 7. Vector Database Product

A dedicated product will be selected during AI implementation.

Candidates include:

- Qdrant
- Weaviate
- Milvus
- Pinecone

For local development, preference should be given to a system that can run easily with Docker.

The exact choice is intentionally not frozen yet.

---

## 8. Smart Indexing

Indexes will be added based on actual query patterns.

We do **not** index every column.

Likely areas to investigate:

- active listings
- listing type
- price ranges
- location
- property type
- common combinations of search fields
- foreign keys
- frequently sorted columns

Example:

```text
Search:
ACTIVE + SALE + location + price range

Possible result:
A composite or partial index may be more useful
than many unrelated single-column indexes.
```

Index decisions should be supported by query inspection and measurement.

Tools:

- PostgreSQL `EXPLAIN`
- PostgreSQL `EXPLAIN ANALYZE`
- Django `QuerySet.explain()`

---

## 9. ORM Query Optimization

Before adding caching, queries should first be written efficiently.

Important Django ORM tools include:

- `select_related()`
- `prefetch_related()`

These help avoid unnecessary repeated queries, especially for GraphQL where N+1 query problems can occur easily.

Optimization order:

```text
1. Correct query design
2. Efficient ORM usage
3. Appropriate indexes
4. Measure/profile
5. Redis caching when useful
```

---

## 10. Transactions and Constraints

Important multi-step operations should use database transactions where atomic behavior is required.

PostgreSQL constraints should protect important invariants where possible.

Examples:

- unique favorites per user/property
- valid foreign-key relationships
- required fields
- operations that must succeed or fail together

Business validation still belongs in the application/service layer.

---

## 11. Migrations

Database schema changes will be managed using Django migrations.

```text
Model change
   ↓
Django migration
   ↓
PostgreSQL schema update
```

Migration files are committed to Git.

---

## 12. File and Media Data

Actual images and videos will not be stored directly in PostgreSQL.

PostgreSQL stores metadata and URLs.

```text
PostgreSQL
  └── media metadata + URL

Object/File Storage
  └── actual image/video bytes
```

The exact file-storage solution will be selected in the File & Media Storage architecture stage.

---

## 13. Source-of-Truth Rules

### PostgreSQL

Authoritative application state.

### Redis

Temporary cache. Can be deleted and rebuilt.

### Vector Database

Derived semantic-search representation.

Its embeddings should be reproducible from authoritative property data. The vector database should not become the only location containing important property information.

---

## 14. Data Synchronization

Because vectors are stored separately, the system must keep PostgreSQL and the vector database synchronized.

Example:

```text
Property updated
      ↓
PostgreSQL updated
      ↓
Event / background job
      ↓
Generate new embedding
      ↓
Update Vector DB
```

This is an important reason the project already supports events and background jobs.

Exact synchronization, retries, and failure handling will be designed later.

---

## Final Architecture

```text
                    Django Modular Monolith
                             │
             ┌───────────────┼───────────────┐
             ↓               ↓               ↓
        PostgreSQL         Redis         Vector DB
      Source of truth      Cache       Semantic search
```

Local infrastructure will be Docker-based where practical.

The system starts simple, but the dedicated vector database is intentionally included so the project can explore semantic search and vector-storage architecture in depth.
