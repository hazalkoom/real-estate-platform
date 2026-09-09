# 08 — Background Processing & Real-Time Communication

## Decision

The application will use a minimal combination of synchronous operations, events, background jobs, and real-time communication.

Core choices:
- Celery + Redis for background jobs
- Events for announcing important domain changes
- Jobs for explicit background work
- WebSockets for important real-time updates
- Synchronous processing when the client needs the result immediately

## Synchronous vs Background

Use synchronous processing when the result is needed immediately:
- property search/details
- favorites
- viewing requests
- sending messages
- normal listing/profile operations
- natural-language search when results are expected immediately

Use background jobs when work is expensive, slow, or can happen after the request:
- generate property embeddings
- update the vector database
- heavy AI analysis
- image processing
- recommendations
- emails
- large reports
- batch operations

## Celery + Redis

```text
Django
  ↓
Celery
  ↓
Redis / Queue
  ↓
Celery Worker
  ↓
Task
```

Redis can serve both caching and Celery infrastructure, while keeping the two responsibilities logically separate.

## Events vs Jobs

**Event:** "Something happened."

Example: `PropertyCreated`

```text
PropertyCreated
      ├── AI module
      ├── Notification module
      └── Analytics
```

**Job:** "Perform this specific work."

Example: `GeneratePropertyEmbedding(property_id)`

Events and jobs can be combined:

```text
PropertyCreated
      ↓
AI module receives event
      ↓
Create background job
      ↓
GeneratePropertyEmbedding
      ↓
Vector Database
```

Rules:
- Direct service call when another module must act immediately and return a result.
- Event when other modules may react to something that happened.
- Background job when work can happen later or is expensive.
- Event + job when an event should trigger expensive asynchronous work.

Avoid unnecessary event chains.

## Real-Time Communication

Important live updates will use WebSockets.

```text
Normal data:
Client ←→ GraphQL API

Real-time updates:
Client ←→ WebSocket connection
```

Likely real-time features:
- chat messages
- important notifications
- viewing decisions where immediate feedback is useful

Normal request/response remains appropriate for:
- search
- property details
- favorites
- listing management
- profile updates
- normal CRUD operations

## Messages vs Notifications

A **message** is the actual communication between users.

A **notification** is an alert that something happened.

Example:

```text
Message created
      ↓
Create notification
      ↓
Real-time notification
      ↓
User opens conversation
      ↓
Reads actual message
```

The notification does not replace the message.

## Long-Running AI Operations

Slow AI operations should run asynchronously rather than keeping a client request open.

```text
Client
  ↓
Start AI operation
  ↓
Operation ID
  ↓
Immediate response
  ↓
Celery worker
  ↓
AI processing
  ↓
Save progress/result
  ↓
Real-time update
```

A long-running operation can expose:

```text
operation_id
status
progress
current_step
result
error
```

Example states:

```text
QUEUED
RUNNING
COMPLETED
FAILED
```

A percentage can be provided when a meaningful estimate is possible. We should not invent fake progress for tasks whose completion cannot be estimated reliably.

## Example: Property Creation + AI

```text
User creates property
        ↓
GraphQL mutation
        ↓
Property Service
        ↓
PostgreSQL
        ↓
PropertyCreated event
        ↓
Immediate response
        ↓
AI listener
        ↓
Celery job
        ↓
Generate embedding
        ↓
Vector Database
        ↓
Generate AI analysis
        ↓
Save result
        ↓
Real-time notification
```

The user does not wait for the AI pipeline to finish.

## Minimality Principle

We will not introduce Kafka, RabbitMQ, multiple queues, or microservices simply because large systems use them.

Current infrastructure:

```text
Django Modular Monolith
        │
        ├── PostgreSQL
        ├── Redis
        ├── Celery Worker
        └── Vector Database
```

Add infrastructure only when there is a real requirement.

## Reliability

Detailed failure handling is separated into **09 — Reliability & Error Handling**.

That stage will cover retries, timeouts, exponential backoff, idempotency, failed jobs, database/Redis/vector DB/AI/external API failures, graceful degradation, and error reporting.

## Final Decision

```text
                    Django
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
     PostgreSQL     Redis      Vector DB
                      │
                   Celery
                      │
                   Workers
                      │
               Background Jobs

Client ←──── GraphQL ────→ Django

Client ←──── WebSocket ──→ Django
              real-time
```

The architecture favors simple, understandable mechanisms and uses events, jobs, and real-time communication only where they provide a clear benefit.
