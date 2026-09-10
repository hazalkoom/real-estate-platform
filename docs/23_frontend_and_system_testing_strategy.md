# 23 — Frontend & System Testing Strategy

## Goal

Define how the completed system is validated across backend, web, mobile, API, real-time communication, and critical user journeys.

This complements `15_testing_quality.md`.

## Testing Layers

```text
                 E2E
              /       \
           Web         Mobile
             \       /
            API / GraphQL
                 ↓
        Integration Tests
                 ↓
            Unit Tests
```

Most tests should remain unit and integration tests. E2E covers critical journeys.

## Backend

Follow `15_testing_quality.md`.

Cover:

- Services
- GraphQL queries/mutations
- Authentication
- Authorization
- Ownership checks
- Database behavior
- Background jobs
- WebSockets
- AI adapters
- Error handling
- Security cases

## Web Frontend

Tools:

- Vitest
- React Testing Library
- Playwright

Component tests cover components, hooks, forms, validation, loading/error states, and user interactions.

Mock GraphQL/network behavior for isolated tests.

Playwright covers critical browser journeys:

1. Login
2. Property search
3. Property details
4. Favorite
5. Viewing request
6. Messaging
7. Listing management

Do not create E2E tests for every component.

## Mobile Frontend

Tools:

- **Jest + React Native Testing Library (RNTL)** for component, screen, hook, and navigation unit/integration tests
- **Maestro** (or Detox) for critical mobile E2E flows on Expo / emulators (Playwright is reserved strictly for web browser testing)

Test:

- Screens and interactive components
- Navigation stack & tab transitions
- Form input and Zod schema validation
- SecureStore token persistence
- GraphQL mutation/query loading, error, and empty states
- Offline banner and reconnect UX

Real-device / simulator testing should cover device-specific capabilities:

- Secure storage (biometric / keychain)
- Image selection and photo picker
- Expo push notifications reception
- WebSocket reconnection upon foregrounding

Do not require every test to run on physical devices.

## Shared Package

Test actual shared behavior:

- Validation schemas
- Shared utilities
- GraphQL helpers
- Platform-independent constants

Generated GraphQL types do not need extensive hand-written tests.

## GraphQL Contract Testing

The GraphQL schema is the contract between Django, web, and mobile.

CI should detect:

- Invalid queries
- Type mismatches
- Breaking field changes
- Broken generated types
- Invalid mutations

Run GraphQL code generation and type checking in CI.

## Real-Time Testing

Test:

- Authentication
- User-specific channels
- Authorization
- Message delivery
- Notification delivery
- Viewing status updates
- Reconnection
- Synchronization after reconnect

Persistent state must also be verified through GraphQL/database behavior.

## AI Testing

Normal CI must not depend on external AI providers.

Test:

- Input parsing
- Structured output validation
- Invalid AI output
- Provider failures
- Timeouts
- Retry behavior
- Prompt-injection defenses
- Search integration
- Prediction storage

Mock external providers for deterministic tests.

Use separate controlled tests for real providers when necessary.

## Security Testing

Include:

- Authentication bypass
- Authorization bypass
- IDOR/resource ownership
- GraphQL abuse
- Input validation
- Rate limiting
- File upload validation
- XSS-related behavior
- AI prompt injection
- Sensitive-data leakage

Security tooling:

- Bandit
- pip-audit
- Trivy
- OWASP ZAP periodically

## Performance Testing

Use Locust for backend/API load testing.

Focus on:

- Property search
- Property details
- Authentication
- Favorites
- Viewing requests
- Messaging
- AI search

Measure throughput, error rate, latency, p95 latency, database behavior, and queue behavior.

Do not continuously load-test every endpoint.

## CI Test Levels

### Pull Request

```text
Lint
 ↓
Type Check
 ↓
Unit Tests
 ↓
Relevant Integration Tests
 ↓
Security Checks
```

### Main Branch

```text
All normal tests
 ↓
Integration Tests
 ↓
GraphQL Generation / Type Checks
 ↓
Docker Build
 ↓
Trivy
 ↓
Selected E2E
```

### Periodic

```text
Full E2E
Performance Tests
OWASP ZAP
Real-provider AI tests where appropriate
Dependency / Security Review
```

## Test Data

Use deterministic test data and factories.

Tests must not depend on:

- Production data
- Personal data
- External production services
- Uncontrolled AI responses
- Existing developer databases

Integration tests use disposable infrastructure.

## Definition of Done

A feature is complete when appropriate:

- Backend behavior is implemented and tested.
- GraphQL contract is updated.
- Web behavior is tested.
- Mobile behavior is tested if applicable.
- Authorization/security cases are covered.
- Loading/error/empty states are handled.
- Critical E2E flow is covered when applicable.
- CI passes.
- No unnecessary test duplication is introduced.

## Final Principle

Test behavior and contracts rather than implementation details.

Prefer:

```text
User performs action
        ↓
Expected behavior
```

over tests tightly coupled to internal component structure.
