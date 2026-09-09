# 09 — Reliability & Error Handling

## Decision

The system should handle failures predictably, retry only when appropriate, degrade gracefully when non-critical dependencies fail, and provide clear error messages to both users and developers.

The design should stay simple and avoid unnecessary reliability infrastructure.

---

## 1. What Can Fail?

Potential failure points include:

```text
Frontend
   ↓
GraphQL API
   ↓
Services
   ↓
PostgreSQL
   ↓
Redis
   ↓
Celery
   ↓
Vector DB
   ↓
AI / external APIs
   ↓
File storage
```

Examples:

- Network failures
- Invalid requests
- Authentication/authorization failures
- PostgreSQL unavailable
- Redis unavailable
- Celery worker crashes
- Vector database unavailable
- AI provider timeout/error
- File upload failure
- External API failure
- Unexpected application bugs

---

## 2. Errors vs Failures

Not every error should be retried.

### Permanent errors

These are unlikely to succeed if repeated without changing something:

- Invalid credentials
- Unauthorized action
- Invalid property data
- Property not found
- User does not own a resource
- Invalid state transition

Return an appropriate API error immediately.

### Transient failures

These may succeed later:

- Temporary database connection failure
- AI timeout
- Vector DB unavailable
- External service returning 503
- Temporary network failure

These may be retried when appropriate.

### Rule

**Do not retry permanent errors. Retry transient failures.**

---

## 3. Retries

Background tasks should support controlled retries for transient failures.

Example:

```text
GeneratePropertyEmbedding
        ↓
Vector DB timeout
        ↓
Retry
        ↓
Still failing
        ↓
Retry with backoff
        ↓
Maximum attempts reached
        ↓
FAILED
```

Use exponential backoff rather than immediately retrying repeatedly:

```text
1s → 2s → 4s → 8s → ...
```

Retries should have a maximum attempt count and maximum delay.

Do not blindly retry every error.

---

## 4. Timeouts

External and potentially slow operations should have appropriate timeouts.

Potential timeout boundaries:

- GraphQL/API requests
- PostgreSQL operations where appropriate
- Redis operations
- AI requests
- Vector DB requests
- File storage
- Celery tasks
- External APIs

Timeout values should depend on the operation. Do not use one arbitrary timeout everywhere.

---

## 5. Idempotency

Important operations should avoid accidentally performing the same action twice when a request is retried.

Example:

```text
Client sends viewing request
        ↓
Server creates viewing
        ↓
Response is lost
        ↓
Client retries
```

Without protection, two viewings could be created.

For important mutations, an idempotency key can be used:

```text
Idempotency-Key: abc123
```

The server can recognize the repeated request and return the original result.

Use this selectively for important operations such as:

- Viewing requests
- Future payment operations
- Other mutations where duplicate execution is harmful

Do not add idempotency mechanisms to every operation unnecessarily.

---

## 6. Failed Background Jobs

When a background task exhausts its retries, it should become a tracked failed job.

Useful information includes:

```text
job_id
 task
 module
 entity_id
 status
 attempts
 error
 created_at
 last_attempt_at
```

Example:

```text
job_id: abc123
 task: GeneratePropertyEmbedding
 module: AI
 entity_id: property-123
 status: FAILED
 attempts: 3
 error: Vector database timeout
```

Failed jobs should be inspectable and, where appropriate, manually retryable.

We do not need a large distributed dead-letter infrastructure for the initial project.

---

## 7. Graceful Degradation

Non-critical features should not break core functionality when they fail.

Example:

```text
Create Property
      ↓
PostgreSQL
      ↓
Property successfully created
      ↓
AI embedding fails
      ↓
Property still exists
      ↓
Retry embedding later
```

AI, vector search, caching, analytics, and notifications should generally be treated as secondary to the core property marketplace.

The exact dependency classification can vary by operation.

---

## 8. Critical vs Non-Critical Dependencies

### Critical

Usually required for the operation to succeed:

- PostgreSQL
- Authentication/authorization for protected operations

### Usually non-critical

Can often fail without breaking the core operation:

- Redis cache
- AI services
- Vector database
- Analytics
- Notifications

Example:

```text
Redis unavailable
      ↓
Do not crash property search
      ↓
Use PostgreSQL directly
```

Caching should improve performance, not become the source of truth.

---

## 9. Client-Facing Error Messages

Errors shown to users should be clear, safe, and actionable.

Avoid exposing technical implementation details.

### Standard categories

| Error | Example message |
|---|---|
| Authentication | You need to log in to continue. |
| Authorization | You don't have permission to perform this action. |
| Validation | Please correct the highlighted information. |
| Not Found | The property you're looking for wasn't found. |
| Conflict | This property has already been added to your favorites. |
| Rate Limited | Too many requests. Please try again later. |
| Dependency Failure | This service is temporarily unavailable. Please try again. |
| Internal | Something went wrong. Please try again later. |

Messages should explain what happened and, when possible, what the user can do next.

---

## 10. Validation Errors

Validation errors should identify the actual fields that need correction.

Instead of:

```text
Invalid input.
```

Return field-level errors such as:

```text
title: "Title is required."
price: "Price must be greater than 0."
bedrooms: "Bedrooms cannot be negative."
```

This makes the API easier for both web and mobile clients to consume.

---

## 11. Machine-Readable Error Codes

API errors should include stable error codes in addition to human-readable messages.

Examples:

```text
PROPERTY_NOT_FOUND
INVALID_PROPERTY_PRICE
UNAUTHORIZED
VIEWING_ALREADY_EXISTS
AI_SERVICE_UNAVAILABLE
INTERNAL_ERROR
```

Conceptually:

```text
code: PROPERTY_NOT_FOUND
message: "The property you're looking for wasn't found."
```

The frontend should use the code for programmatic behavior and the message for user communication.

---

## 12. Request IDs / Correlation IDs

Each API request should have a request ID.

Example:

```text
request_id: 8f31c2...
```

The same ID should appear in relevant logs so a reported client error can be traced back to the exact request.

Example:

```text
Client:
"Something went wrong. Reference: 8f31c2"

Developer logs:
request_id = 8f31c2
operation = CreateProperty
module = Properties
error = PostgreSQL connection timeout
```

This becomes especially useful as the application grows.

---

## 13. Never Expose Internal Errors

Never expose information such as:

- Stack traces
- SQL queries
- Database credentials
- Internal hostnames/IPs
- Internal service URLs
- File paths
- Secret keys
- Raw third-party error details

These belong in internal logs, not client responses.

---

## 14. Logging

Use structured logs containing useful debugging context.

Useful request fields:

```text
timestamp
request_id
user_id (where appropriate)
module
operation
status
error_code
duration
```

Useful background-job fields:

```text
job_id
task
module
entity_id
attempt
duration
status
error
```

### Logging levels

```text
DEBUG    → development/debugging details
INFO     → normal important events
WARNING  → unusual condition
ERROR    → operation failed
CRITICAL → major system failure
```

Do not log sensitive information unnecessarily.

---

## 15. Monitoring

Logging tells us what happened. Monitoring tells us whether the system is healthy.

Important metrics include:

- API error rate
- API latency
- Database latency/errors
- Celery failed jobs
- Celery queue length
- Redis availability
- AI failures/timeouts
- Vector DB latency/errors
- External API failures

The exact monitoring stack will be decided later during observability/deployment planning.

---

## 16. Frontend Error Handling

Web and mobile clients should handle at least:

- No network connection
- Request timeout
- Validation errors
- Authentication expiration
- Authorization errors
- Not found
- Rate limiting
- Server errors
- Temporary dependency failures

The UI should show a useful state instead of crashing or displaying a blank screen.

---

## 17. Overall Error Flow

```text
Request
   ↓
Validation
   ↓
Authorization
   ↓
Service
   ↓
Database / External Service
   ↓
      ┌───────────────┐
      │     Error?    │
      └───────┬───────┘
              ↓
        Classify error
          ↙         ↘
   Permanent       Transient
       ↓               ↓
 Return safe       Retry when
 client error      appropriate
                       ↓
                 Still failing?
                       ↓
                  Log details
                       ↓
              Safe client message
```

---

## Core Principles

1. Do not retry permanent errors.
2. Retry transient failures when appropriate.
3. Use exponential backoff and retry limits.
4. Use appropriate timeouts.
5. Make important operations idempotent where necessary.
6. Track failed background jobs.
7. Let non-critical dependencies fail without breaking core functionality.
8. Return consistent, clear client-facing errors.
9. Give API errors stable machine-readable codes.
10. Use request IDs for debugging.
11. Log detailed internal information but never expose it to clients.
12. Monitor system health and important failure metrics.
13. Keep the reliability architecture simple and avoid unnecessary infrastructure.

---

## Current Reliability Architecture

```text
                   Request
                      ↓
                 Validation
                      ↓
                 Authorization
                      ↓
                   Service
                      ↓
              ┌───────┴───────┐
              ↓               ↓
          PostgreSQL        External
              │             systems
              │          ┌────┼─────┐
              │          ↓    ↓     ↓
              │        Redis AI  Vector DB
              │
              ↓
            Result

Failures at every boundary
             ↓
       classify failure
        ↙           ↘
  permanent       transient
      ↓                ↓
 safe API error      retry
 + detailed logs       ↓
                  eventual success
                    or FAILED
```
