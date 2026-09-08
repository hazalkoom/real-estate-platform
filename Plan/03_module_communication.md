# System Architecture — Module Communication

## Decision

The modular monolith will use different communication mechanisms depending on the type of operation.

We will use:

1. **Synchronous service calls** for operations that need an immediate result.
2. **Events** when a module needs to announce that something happened and other modules may react.
3. **Background jobs** for expensive or non-urgent work.

Modules should not randomly access another module's internal implementation or database logic.

---

## 1. Synchronous Service Calls

A module can call another module through a defined service/use-case interface.

```text
Interactions
     │
     │ service call
     ▼
Properties
```

Example:

A viewing request may need to verify that a property/listing exists and is available.

### Advantages

- Simple
- Fast
- Easy to understand
- Easy to debug
- Suitable for operations that require an immediate result

### Disadvantages

- Creates some coupling between modules
- Excessive use can make modules heavily dependent on each other
- The called module must be available for the operation to complete

### Usage

Use synchronous calls when the caller needs an answer immediately.

---

## 2. Events

A module can publish an event when something important happens.

```text
Interactions
     │
     │ ViewingAccepted
     ▼
   Event
     │
     └──────► Communication
```

The event describes what happened without requiring the original module to know every consumer.

Examples:

```text
PropertyCreated
ListingUpdated
ViewingRequested
ViewingAccepted
ListingSold
MessageSent
```

### Advantages

- Lower coupling
- Multiple modules can react to the same event
- Useful for notifications and future analytics/AI features
- Can make future service extraction easier

### Disadvantages

- More difficult to trace and debug
- The execution flow is less obvious
- Requires handling failures and duplicate events
- Can become unnecessarily complicated if used everywhere

### Usage

Use events when another part of the system needs to react to an action that has already happened.

---

## 3. Background Jobs

Expensive or non-urgent work can be placed into a background queue.

```text
User
  ↓
Django
  ↓
Queue
  ↓
Worker
  ↓
Perform work
```

Potential examples:

- ML predictions
- AI processing
- Image processing
- Sending emails
- Large notification tasks
- Recommendation calculations

The exact background-job technology will be decided later.

### Advantages

- Keeps user-facing requests fast
- Suitable for expensive operations
- Jobs can be retried
- Helps handle workload spikes

### Disadvantages

- Adds infrastructure
- More difficult to debug
- Results are not necessarily immediate
- Requires failure/retry handling

### Usage

Use background jobs when the user does not need the operation to finish before receiving the response.

---

## Communication Rules

### Rule 1 — Prefer simple synchronous calls

Do not use events or queues when a normal service call is enough.

### Rule 2 — Use events for reactions

If the important idea is:

> "Something happened, and other modules may care."

an event is appropriate.

### Rule 3 — Use background jobs for expensive work

If an operation is slow, expensive, or non-urgent, consider a background job.

### Rule 4 — Protect module boundaries

A module should communicate through another module's public services/interfaces rather than directly manipulating its internal logic.

### Rule 5 — Do not over-engineer

Not every function needs a service, event, or background job.

The simplest mechanism that correctly solves the problem should be preferred.

---

## Example

A customer requests a viewing:

```text
Customer
   ↓
Interactions
   │
   │ service call
   ▼
Properties
   │
   │ validate listing
   ▼
Interactions
   │
   │ create viewing
   ▼
ViewingRequested event
   │
   ▼
Communication
   │
   ▼
Notification
```

If additional expensive work is required:

```text
ViewingRequested
       ↓
Background Job
       ↓
AI / Analytics / Other Processing
```

The exact implementation of events and background jobs will be decided later.

---

## Decision Summary

```text
Immediate result needed
        ↓
Synchronous service call

Something happened
        ↓
Event

Expensive / non-urgent work
        ↓
Background job
```

This gives the modular monolith a simple communication model without prematurely introducing microservices or unnecessary infrastructure.
