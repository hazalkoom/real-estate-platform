# 06 — Authentication & Authorization

## Goal

Define how users prove their identity and what each role is allowed to do.

- **Authentication:** Who are you?
- **Authorization:** What are you allowed to do?

## Roles & Persona Model

- Guest (unauthenticated)
- Buyer / Customer
- Owner / Seller
- Agent
- Admin

### Multi-Role Flexibility
In real estate marketplaces, a user can simultaneously act as a **Buyer** (searching and favoriting homes) and an **Owner** (listing a property for sale).
Rather than restricting an account to a single mutually-exclusive enum:
- Users have a base account (`User`).
- Role capabilities are represented via user profile flags or permissions (`is_agent`, `is_owner`, `is_staff`).
- Any registered user can register as an Owner by submitting a property listing.
- Agent accounts require an administrative verification workflow.

## Dual-Mode Authentication Architecture

The Django backend serves both the Web frontend (React SPA) and Mobile app (React Native / Expo). To maximize security and compatibility on each platform, Django implements a **Dual-Mode Authentication Middleware**:

```text
Incoming Request
       │
       ├── Web Browser?
       │   └── Extracts JWT from HttpOnly, Secure, SameSite=Lax Cookie
       │       └── Protected against XSS attacks
       │
       └── Mobile App (Expo)?
           └── Extracts JWT from "Authorization: Bearer <token>" Header
               └── Token stored in Expo SecureStore (Keychain / Keystore)
       │
       ▼
Authentication Middleware
       │
       ├── Validate JWT signature and expiration
       ├── Check token blacklist in Redis (for revoked tokens / logout)
       ▼
Attach `user` to GraphQL Context (`info.context.user`)
```

### Real-Time WebSocket Authentication
WebSocket handshakes cannot easily set custom HTTP headers on native browser connections:
- **Web:** Browser automatically forwards the `HttpOnly` cookie during the WebSocket upgrade request (`ws://` / `wss://`). Django Channels ASGI auth middleware inspects the cookie.
- **Mobile:** Mobile client sends a ticket or the JWT token in query parameters during connection handshake (e.g. `wss://api.example.com/graphql?token=<jwt>`). The token is immediately validated and discarded from the URL.

Passwords are securely hashed using Django's default PBKDF2 / Argon2 algorithm and never stored as plaintext.

## Permission matrix

| Capability | Guest | Buyer | Owner | Agent | Admin |
|---|---:|---:|---:|---:|---:|
| Browse properties | ✅ | ✅ | ✅ | ✅ | ✅ |
| Search/filter properties | ✅ | ✅ | ✅ | ✅ | ✅ |
| View property details/media | ✅ | ✅ | ✅ | ✅ | ✅ |
| View public listings | ✅ | ✅ | ✅ | ✅ | ✅ |
| Save favorites | ❌ | ✅ | ✅ | ✅ | ✅ |
| Request a viewing | ❌ | ✅ | ✅ | ✅ | ✅ |
| View own viewing requests | ❌ | ✅ | ✅ | ✅ | ✅ |
| Cancel own viewing | ❌ | ✅ | ✅ | ✅ | ✅ |
| Send/read own messages | ❌ | ✅ | ✅ | ✅ | ✅ |
| Create property submission | ❌ | ❌ | ✅ | ✅ | ✅ |
| Create/manage listing | ❌ | ❌ | Own/authorized | Assigned/authorized | ✅ |
| Edit property data | ❌ | ❌ | Own/authorized | Authorized | ✅ |
| Upload property media | ❌ | ❌ | Own/authorized | Authorized | ✅ |
| Change listing price/status | ❌ | ❌ | Own/authorized | Authorized | ✅ |
| Approve/reject managed viewings | ❌ | ❌ | Own/authorized | Authorized | ✅ |
| Complete/cancel managed viewings | ❌ | ❌ | Own/authorized | Authorized | ✅ |
| Receive notifications | ❌ | ✅ | ✅ | ✅ | ✅ |
| Submit ratings/comments | ❌ | ✅ | ✅ | ✅ | ✅ |
| Edit/delete own ratings/comments | ❌ | ✅ | ✅ | ✅ | ✅ |
| Report property/user | ❌ | ✅ | ✅ | ✅ | ✅ |
| Use AI features | Limited/public | ✅ | ✅ | ✅ | ✅ |
| View/edit own profile | ❌ | ✅ | ✅ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ❌ | ✅ |
| Moderate reports | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage property types/amenities | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage platform-wide data | ❌ | ❌ | ❌ | ❌ | ✅ |

## Ownership rules

### Owner

Can manage their own properties/listings, subject to platform rules.

### Agent

Can manage properties/listings they are authorized or assigned to manage. Being an Agent does not grant access to every listing.

### Buyer

Can interact with properties but cannot manage other users' listings.

### Admin

Has platform-level management permissions, implemented through explicit authorization checks.

## Guest permissions

Guests can browse, search, filter, and view public property/listing information and media.

Guests cannot favorite, request viewings, message users, submit ratings/comments, manage listings, or access private user data.

## Authorization flow

```text
GraphQL Mutation
      ↓
Authentication
      ↓
Role / permission check
      ↓
Ownership / state check
      ↓
Service
      ↓
Repository
```

Role checks alone are not enough.

Example: an Agent may edit listings, but the system must also verify that the Agent is authorized to manage that specific listing.

## Security topics for later

The Security stage will cover:

- Password hashing
- Token expiration
- Refresh-token security
- Token revocation
- Account recovery
- Email verification
- Rate limiting
- Brute-force protection
- Object-level authorization
- Sensitive-data exposure
- Token storage
- Audit logging
- Admin protection

## Scope

This document defines authentication and authorization architecture and role permissions.

Detailed security implementation and security testing will be handled in the Security and Testing stages.
