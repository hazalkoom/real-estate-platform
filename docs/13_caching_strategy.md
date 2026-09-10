# 13 — Caching Strategy

## Decision

Use **Redis** as the application's cache.

Redis is already part of the system for **Celery** and real-time infrastructure, so we will not introduce another caching technology.

Caching is **selective**, not global. PostgreSQL remains the source of truth.

---

## What We Will Cache

### 1. Read-heavy, relatively stable data

Cache data that is requested frequently and changes infrequently:

- Property types
- Amenities
- Common location data
- Public configuration/reference data

### 2. Expensive read operations

Cache selected expensive operations when profiling shows they benefit from caching:

- Popular property searches
- Expensive recommendation results
- Selected AI-generated results where appropriate

Do not cache these automatically from the beginning. Add caching based on actual query/usage patterns.

### 3. Short-lived user-specific data

Where useful:

- Temporary recommendation/search results
- Rate-limit counters or similar short-lived state

Do not use Redis as permanent storage for user data.

---

## What We Will Not Cache Initially

- Individual property records by default
- Listing prices/status by default
- Favorites
- Viewings
- Messages
- Notifications
- Authentication/session-critical data unless specifically required by the chosen auth implementation

These areas can become stale or require complicated invalidation. PostgreSQL is fast enough for the initial system when queries and indexes are designed correctly.

---

## Cache Strategy

Use **cache-aside**:

```text
Request
  ↓
Check Redis
  ↓
┌───────────────┐
│ Cache exists? │
└───────┬───────┘
     yes│       │no
        ↓       ↓
      Return  PostgreSQL
                ↓
              Redis
                ↓
              Return
```

Application code controls when data is read from and written to the cache.

---

## TTL

Every cached item should have an explicit TTL.

Initial approach:

- Reference data → longer TTL
- Search results → short TTL
- AI/recommendation results → short or moderate TTL depending on freshness requirements
- Temporary state → very short TTL

Exact TTL values will be decided during implementation and adjusted based on usage.

Avoid indefinite cache entries unless there is a specific reason.

---

## Cache Invalidation

For data that can change, invalidation is preferred over trying to keep multiple cached copies perfectly synchronized.

Example:

```text
Listing price changes
       ↓
Update PostgreSQL
       ↓
Invalidate affected cache entries
```

For search caches, changes to a property/listing may invalidate relevant search-result keys. We should avoid attempting a complicated global invalidation system.

When invalidation becomes difficult, short TTLs are preferred over excessive complexity.

---

## Cache Keys

Use predictable, namespaced keys.

Examples:

```text
property_types:v1
amenities:v1
property_search:v1:<hash>
recommendations:v1:<user_id>
```

Search/filter parameters should be normalized before generating the key so equivalent requests do not create unnecessary duplicate entries.

---

## Redis Failure

Redis is **not a source of truth**.

If Redis becomes unavailable:

```text
Redis unavailable
      ↓
Skip/fail cache operation safely
      ↓
Use PostgreSQL / normal application path
```

The core application should continue working where possible.

A cache failure should not normally turn a successful database operation into a user-visible failure.

---

## Database Optimization Before Caching

Caching is not a substitute for good PostgreSQL queries.

Before adding a cache:

1. Add appropriate indexes.
2. Inspect generated SQL.
3. Use Django `select_related()` / `prefetch_related()` where appropriate.
4. Use `EXPLAIN ANALYZE` / Django `QuerySet.explain()` for expensive queries.
5. Measure the actual problem.
6. Cache only if it provides a meaningful benefit.

---

## Interaction With Celery

Redis has two roles:

```text
                 Redis
                /     \
               ↓       ↓
            Cache    Celery
                     broker
```

These are logically separate uses even though the same Redis deployment may serve both.

If the project grows, they can be separated without changing the application's overall architecture.

---

## Redis Multi-Role Resource Partitioning

Because Redis serves 4 distinct workloads (Cache, Celery Broker, Django Channels backplane, Rate Limiting), we must prevent cache evictions from dropping Celery tasks or disconnecting active WebSockets.

### Logical Database Partitioning:
- **`db 0` — Application Cache:** Uses `volatile-lru` eviction policy (only keys with an explicit TTL can be evicted under memory pressure).
- **`db 1` — Celery Broker:** Never evicted (`noeviction`). Jobs remain safe in queues.
- **`db 2` — Channels Channel Layer:** Ephemeral pub/sub message groups.
- **`db 3` — Rate Limiting & Blacklisted Tokens:** Security counters with short TTLs.

In Docker Compose and staging, a single Redis server with distinct DB indices provides total operational isolation without extra infrastructure costs.

---

## Main Rules

1. PostgreSQL is the source of truth.
2. Redis is the cache.
3. Use cache-aside with `volatile-lru` eviction.
4. Separate Celery broker, cache, and channels across distinct Redis DB numbers.
5. Cache selectively based on real usage.
6. Every cache entry gets an explicit TTL.
7. Invalidate changed data where practical.
8. Prefer short TTLs over complicated invalidation systems.
9. Optimize PostgreSQL queries before introducing caching.
10. Redis failure should degrade performance, not break core functionality.

---

## Final Decision

```text
Django Modular Monolith
        │
        ├── PostgreSQL → source of truth
        │
        └── Redis
             ├── db 0: Cache (volatile-lru)
             ├── db 1: Celery broker (noeviction)
             ├── db 2: Django Channels (WebSockets)
             └── db 3: Rate limits & token revocation
```

Caching will remain intentionally small and focused. We will expand it only when measurements show a real performance need.
