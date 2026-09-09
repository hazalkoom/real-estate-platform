# 15 — Testing & Quality

## Goal

Build a testing strategy that is fast during development, realistic for production behavior, and strong enough to validate business rules, APIs, background jobs, real-time flows, AI integrations, security, and performance without overengineering.

---

## Core Tooling Decisions

| Area | Tool |
|---|---|
| Test framework | `pytest` |
| Django integration | `pytest-django` |
| Test data | `factory_boy` |
| Coverage | `pytest-cov` |
| Linting | `Ruff` |
| Formatting | `Ruff formatter` |
| Type checking | `mypy` |
| Security scanning | `Bandit` |
| Dependency vulnerability scanning | `pip-audit` |
| End-to-end browser testing | `Playwright` |
| Load/performance testing | `Locust` |
| CI execution | `GitHub Actions` |

GraphQL tests will use Django/GraphQL test utilities appropriate to the chosen GraphQL library.

---

## Test Strategy by Layer

### Unit Tests

Unit tests should test pure business logic directly.

They should avoid unnecessary infrastructure such as:

- GraphQL
- PostgreSQL
- Redis
- Celery workers
- WebSockets
- external network calls

Examples:

- viewing state transitions
- permission rules
- ranking/scoring logic
- validation helpers
- recommendation logic
- AI result normalization

Unit tests should be the fastest and most numerous tests in the suite.

---

### Service Tests Without API

Application services should be testable directly without going through GraphQL.

Example flow:

```text
pytest
  ↓
CreateViewingService
  ↓
assert result
```

This keeps business-logic tests independent from the transport/API layer.

GraphQL will be tested separately to verify that resolvers correctly call application services.

---

### Integration Tests

Integration tests should verify that important application components work together.

Typical path:

```text
Service
  ↓
Repository
  ↓
Django ORM
  ↓
PostgreSQL
```

Examples:

- creating and retrieving properties
- creating listings
- favorites
- viewing requests
- authentication persistence
- repository queries
- transactions
- ownership checks involving persisted data

Integration tests should use real PostgreSQL rather than SQLite.

---

## Dedicated Test Database

Testing must never use development or production databases.

Environment separation:

```text
Development → real_estate_dev
Testing     → real_estate_test
Production  → real_estate_prod
```

The test database should be disposable and isolated.

In CI, each run should create a clean test environment.

---

## Database Isolation

Tests must not leak data into each other.

Each test should begin from a predictable state.

Use Django/pytest-django transaction handling and cleanup mechanisms so changes are rolled back or cleaned between tests.

Transaction-specific behavior should use dedicated transactional test configuration when required.

---

## GraphQL/API Testing

GraphQL is the primary API and needs dedicated request-level tests.

Test:

- queries
- mutations
- authentication
- authorization
- validation
- error contracts
- pagination
- filtering
- sorting
- malformed input
- ownership checks
- GraphQL-specific abuse cases

Important API tests should go through the complete request path:

```text
GraphQL Request
      ↓
Resolver
      ↓
Service
      ↓
Repository
      ↓
Database
```

---

## Negative Testing

Tests must verify that invalid and unauthorized actions are rejected correctly.

Examples:

- invalid prices
- missing required fields
- non-existent property IDs
- expired listings
- duplicate favorites
- invalid viewing times
- unauthorized listing edits
- unauthorized message access
- user accessing another user's private data
- malformed GraphQL input

Negative tests should also verify that the client receives the correct error code/message from the reliability plan.

---

## Authentication & Authorization Tests

Dedicated tests should cover all roles:

- Guest
- Buyer
- Owner
- Agent
- Admin

Test both role-based and ownership-based rules.

Example expectations:

```text
Buyer → create property               DENY
Owner → create property               ALLOW
Agent → edit random listing           DENY
Agent → edit assigned listing         ALLOW
Admin → platform management           ALLOW
```

IDOR-style scenarios must be tested explicitly.

---

## Test Data Strategy

Use `factory_boy` for repeatable test data.

Factories will be created for important models such as:

- UserFactory
- PropertyFactory
- ListingFactory
- ViewingFactory
- FavoriteFactory
- MessageFactory
- NotificationFactory

Tests should override only the fields relevant to the scenario.

Avoid large duplicated dictionaries or fixtures unless there is a clear reason.

---

## Mocking Strategy

### Mock external dependencies

Normal tests should not call real external services such as:

- LLM providers
- embedding providers
- email/SMS services
- object storage providers
- third-party APIs

Mock or fake their responses.

Reasons:

- faster tests
- no cost
- deterministic behavior
- no external outages
- no accidental production side effects

### Do not mock everything

Avoid excessive mocking of our own application layers.

For example:

- Unit tests may mock genuine external dependencies.
- Integration tests should use real repositories and real PostgreSQL.

The suite should prove that our internal pieces actually work together.

---

## AI Testing

AI tests should validate contracts and behavior rather than exact generated text.

For natural-language search, test expected structured output such as:

```json
{
  "property_type": "apartment",
  "bedrooms": 3,
  "city": "Cairo",
  "max_price": 5000000
}
```

Test:

- required fields
- valid data types
- ranges
- missing fields
- malformed provider output
- hallucinated/unsupported fields
- provider timeout
- provider failure
- fallback behavior

Real-provider tests, if used, should be a small separate suite and should not run on every commit.

---

## Redis Testing

Pure unit tests should not require Redis.

Use mocks/fakes where Redis behavior itself is not under test.

Dedicated integration tests should use a real Redis instance, preferably via Docker.

Test important behavior such as:

- cache set/get
- TTL behavior
- invalidation
- fallback to PostgreSQL when Redis is unavailable

---

## Celery Testing

Most tests should not require a real Celery worker.

Task logic should be testable directly.

Use dedicated integration tests when actual queue/worker behavior matters.

Example:

```text
pytest
  ↓
Celery
  ↓
Redis broker
  ↓
Worker
  ↓
Task result
```

Test:

- retries
- exponential backoff policy
- idempotency
- failure after retry exhaustion
- result persistence
- duplicate-task safety

---

## WebSocket Testing

WebSocket consumers should be testable without running the entire frontend.

Test directly:

- connection authentication
- message delivery
- notification delivery
- correct recipient isolation
- disconnect/reconnect behavior
- unauthorized subscription attempts

A smaller number of E2E tests will verify the full browser experience.

---

## End-to-End Testing

Use `Playwright` for a small number of critical user journeys.

Examples:

1. Guest browses and searches properties.
2. Buyer logs in and favorites a property.
3. Buyer requests a viewing.
4. Owner/agent manages a listing.
5. Messaging flow works.
6. Real-time notification appears after an important event.

E2E tests should remain limited because they are slower and more fragile than lower-level tests.

---

## Contract Testing

Test important contracts between boundaries.

### GraphQL contract

Verify:

- expected fields
- expected types
- required arguments
- stable error codes
- mutation/query shapes

### AI adapter contract

Each provider adapter should normalize its output into our internal format.

This makes switching providers safer and prevents provider-specific behavior from leaking into the rest of the application.

---

## Deterministic Testing

Tests should produce the same result on every run.

Avoid uncontrolled dependencies on:

- current real time
- random values
- live network calls
- production data
- AI randomness

Control time where required.

Control randomness with fixed seeds or mocks when needed.

---

## Regression Testing

Every significant bug should ideally produce a regression test.

Example:

```text
Bug: Agent could edit another agent's listing.
```

After fixing it, add a test such as:

```text
test_agent_cannot_edit_unauthorized_listing()
```

The test remains permanently to prevent the bug from returning.

---

## Security Testing

Automated tools:

- `Bandit` for Python security issues
- `pip-audit` for vulnerable dependencies

Manual/targeted scenarios should include:

- authentication bypass
- authorization bypass
- IDOR
- injection attempts
- GraphQL abuse
- rate limiting
- file upload validation
- sensitive information leakage
- access-token misuse

The detailed security architecture will be defined separately in the Security plan.

---

## Performance & Load Testing

Use `Locust` for targeted performance testing.

Focus on realistic workflows rather than every endpoint.

Example workload:

```text
users
  ↓
search properties
  ↓
open property details
  ↓
favorite property
  ↓
request viewing
```

Measure:

- requests per second
- response latency
- p95/p99 latency
- error rate
- PostgreSQL behavior
- Redis behavior
- queue growth

AI-heavy workflows should be tested separately because their performance characteristics differ from normal API traffic.

---

## Code Quality

The quality pipeline should include:

```text
Ruff
  ↓
mypy
  ↓
pytest
  ↓
coverage
  ↓
Bandit
  ↓
pip-audit
```

### Ruff

Use for linting and formatting.

### mypy

Use gradually for type safety.

Typing should be strongest around:

- services
- repositories
- domain/application contracts
- AI adapters
- integration boundaries

---

## Coverage Strategy

Use `pytest-cov`.

Do not chase 100% coverage.

Prioritize high coverage for:

- business rules
- services
- authorization
- critical repositories
- GraphQL mutations
- failure/retry logic

Coverage is a signal, not the definition of quality.

---

## Test Pyramid

```text
                 E2E
              Playwright
                 ▲
                 │
          API / GraphQL
                 ▲
                 │
          Integration
      PostgreSQL / Redis
                 ▲
                 │
              Unit
           Pure Python
```

Use many fast unit tests, a moderate number of integration/API tests, and a small number of E2E tests.

---

## Test Execution Modes

### Fast development suite

Used constantly while coding.

```text
pytest tests/unit/
```

No external infrastructure should be required for pure unit tests.

### Normal backend suite

Runs:

- unit tests
- integration tests
- GraphQL/API tests

Uses test PostgreSQL and other dependencies only where required.

### Full suite

Runs before release/deployment:

- unit
- integration
- GraphQL/API
- WebSocket
- Celery integration
- E2E
- security checks

### Periodic/manual suite

Runs separately:

- Locust load tests
- deeper security tests
- optional real AI-provider integration tests

---

## Testing Environments

```text
Development
    ↓
real_estate_dev

Testing
    ↓
real_estate_test

Production
    ↓
real_estate_prod
```

CI should create an isolated test environment for every workflow run.

No test should ever depend on production data.

---

## CI Strategy Connection

The CI plan will later define exactly when each suite runs.

Expected direction:

### Pull request

```text
Ruff
mypy
unit tests
integration/API tests
coverage
Bandit
pip-audit
```

### Before deployment

```text
Full backend suite
E2E
security checks
```

Load testing remains separate and should not block every pull request.

---

## Final Decisions

- `pytest` is the main testing framework.
- `pytest-django` integrates Django and PostgreSQL tests.
- Tests use a dedicated PostgreSQL test database.
- Unit tests should not require API, database, Redis, Celery, or network unless needed.
- Services should be testable directly without GraphQL.
- Integration tests use real PostgreSQL.
- External services are mocked/faked in normal tests.
- Real Redis/Celery are used only in dedicated integration tests.
- GraphQL request-level tests are mandatory.
- Negative, authorization, ownership, and IDOR tests are mandatory.
- `factory_boy` creates reusable test data.
- Tests should be deterministic.
- Significant bugs receive regression tests.
- `Playwright` covers a small number of critical E2E workflows.
- `Locust` handles load/performance testing.
- `Ruff`, `mypy`, `Bandit`, and `pip-audit` are part of quality checks.
- `pytest-cov` tracks useful coverage without targeting 100%.
- CI will use isolated test environments.
- Fast, normal, full, and periodic test suites will be separated so developers do not run expensive tests unnecessarily.
