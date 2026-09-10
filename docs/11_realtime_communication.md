# 11 — Real-Time Communication

## Decision

Use **WebSockets via Django Channels** for the small number of features that genuinely need real-time updates.

The project will use:

- **Django Channels** for native asynchronous WebSocket handling inside the Django modular monolith
- **Uvicorn / ASGI** as the application server running both HTTP and WebSocket protocols
- **Redis Channel Layer (`channels_redis`)** as the pub/sub backplane for message distribution
- **GraphQL (Strawberry)** for standard request/response mutations and queries
- **Expo Push Notifications (FCM / APNs)** for offline mobile user delivery
- **Celery** for background tasks (e.g. broadcasting async jobs or processing push notifications)

We will **not** introduce a separate external WebSocket microservice (e.g. separate Node.js or Go server).

---

## 1. Why do we need real-time communication?

Normal GraphQL communication is request/response:

```text
Client
  ↓
GraphQL request
  ↓
Django
  ↓
Response
```

The server normally responds only after the client asks for something.

WebSockets keep a connection open so the server can send an update when something happens:

```text
Client ←──────── WebSocket connection ────────→ Django
```

This is useful for chat, notifications, and progress updates.

---

## 2. Where we will use WebSockets

### Chat

When one user sends a message, the receiver can get it immediately.

```text
User A
  ↓
GraphQL mutation
  ↓
Django
  ↓
Save message
  ↓
WebSocket
  ↓
User B
```

The `messages` table remains the source of truth. WebSockets only deliver the update in real time.

### Notifications

Use WebSockets for important notifications such as:

- New message
- Viewing approved/rejected
- Important listing activity
- AI operation completed

Notifications are still stored in the `notifications` table so they are not lost if the user is offline.

### Long-running AI operations

A background AI task can send progress updates when useful:

```text
Client
  ↓
Start AI operation
  ↓
Django
  ↓
Celery
  ↓
AI processing
  ↓
Progress update
  ↓
WebSocket
  ↓
Client
```

Example UI:

```text
Analyzing property...
████████░░ 80%
```

When finished:

```text
✓ Analysis complete
```

Progress should only be reported when the task can provide meaningful progress. Otherwise use states such as `QUEUED`, `RUNNING`, `COMPLETED`, and `FAILED`.

---

## 3. Where we will NOT use WebSockets

Do not use WebSockets for normal CRUD or search operations.

Examples:

- Property search → GraphQL
- Property details → GraphQL
- Add/remove favorite → GraphQL
- Create property → GraphQL
- Create listing → GraphQL
- Request viewing → GraphQL
- Profile changes → GraphQL

The rule is simple:

> Use WebSockets when the server needs to push something to an already-connected client. Otherwise use GraphQL.

---

## 4. WebSockets vs GraphQL

### GraphQL

Best for request/response operations:

```text
Client: Give me this data.
Server: Here is the data.
```

### WebSocket

Best for server-initiated updates:

```text
Server: Something just happened.
Client: Got it.
```

They are complementary, not competing technologies.

---

## 5. Redis's role

Redis is already part of the architecture for caching and Celery.

It can also support communication between Django processes handling WebSocket connections.

Conceptually:

```text
                Django
               /      \
              ↓        ↓
         GraphQL      WebSocket
              \        /
               ↓      ↓
                  Redis
```

Redis is **not** the source of truth for messages or notifications.

PostgreSQL stores the actual data.

---

## 6. Offline users

A WebSocket only works while the client is connected.

Therefore important data must still be persisted.

Example:

```text
User B offline
      ↓
Message / Notification created
      ↓
PostgreSQL
      ↓
Celery background job
      ↓
Expo Push Notification (FCM / APNs)
      ↓
User B's phone displays lock-screen notification
```

When User B clicks the push notification or comes back online, the client retrieves fresh data through GraphQL.

This means WebSockets are a live delivery mechanism for connected clients, while persistent tables and push notifications guarantee no messages are ever lost.

---

## 7. Reconnection

Connections can disappear because of:

- Internet loss
- Phone going to sleep
- Browser closing
- Server restart
- Network changes

The client should automatically attempt to reconnect.

After reconnecting, it should use normal GraphQL requests to synchronize anything it may have missed.

We do not need a complicated custom synchronization system initially.

---

## 8. Authentication

WebSocket connections must be authenticated just like normal API requests.

Conceptually:

```text
Client
  ↓
WebSocket connection + authentication
  ↓
Django identifies user
  ↓
Connection authorized
```

A user must only receive events they are allowed to see.

Examples:

- User A must not receive User B's private messages.
- A buyer must not receive another buyer's notifications.
- Users should only receive updates for conversations/viewings they are authorized to access.

---

## 9. Module boundaries

The modules keep ownership of their data and business rules.

For example:

```text
Communication Module
        ↓
creates message/notification
        ↓
WebSocket delivery
```

The WebSocket layer should not contain business rules such as deciding whether a user is allowed to approve a viewing.

That decision belongs to the appropriate application service/module.

---

## 10. Example: Viewing approval

```text
Agent
  ↓
GraphQL mutation
  ↓
Interactions Service
  ↓
Validate permission/state
  ↓
Update viewing in PostgreSQL
  ↓
Create notification
  ↓
WebSocket
  ↓
Buyer receives:
"Your viewing request was approved."
```

The database update happens first. The real-time message is only a notification to the connected client.

---

## 11. Example: Chat message

```text
User A
  ↓
GraphQL mutation
  ↓
Communication Service
  ↓
Save message in PostgreSQL
  ↓
Create notification
  ↓
WebSocket
  ↓
User B
```

If User B is offline, the message remains in PostgreSQL and can be retrieved later.

---

## 12. Failure handling

Real-time delivery can fail without the underlying operation failing.

For example:

```text
Message saved successfully
        ↓
WebSocket delivery fails
        ↓
User is temporarily offline
```

This should **not** delete or roll back the message.

When the user reconnects, normal API synchronization can retrieve it.

This follows the reliability principle:

> Core data should not depend on successful real-time delivery.

---

## 13. Minimal real-time architecture

Final approach:

```text
                    Django
                 /          \
                ↓            ↓
           GraphQL API    WebSocket
                ↓            ↓
          Normal API      Real-time
                 \           /
                  ↓         ↓
                     Redis
```

### Technologies

| Technology | Purpose |
|---|---|
| GraphQL | Normal API communication |
| WebSockets | Real-time server → client updates |
| Redis | Cache, Celery broker, and real-time support |
| Celery | Background/long-running work |
| PostgreSQL | Source of truth |

---

## 14. Principles

1. Use WebSockets only where real-time updates provide real value.
2. Keep normal CRUD/search operations on GraphQL.
3. Persist important messages and notifications in PostgreSQL.
4. Treat WebSockets as a delivery mechanism, not storage.
5. Authenticate WebSocket connections.
6. Enforce authorization before sending private events.
7. Handle disconnections and reconnect automatically.
8. Synchronize missed data through GraphQL after reconnecting.
9. Do not put business logic inside the WebSocket layer.
10. Do not introduce a separate WebSocket service unless the project actually needs one.
