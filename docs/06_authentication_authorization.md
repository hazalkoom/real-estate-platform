# 06 — Authentication & Authorization

## Goal

Define how users prove their identity and what each role is allowed to do.

- **Authentication:** Who are you?
- **Authorization:** What are you allowed to do?

## Roles

- Guest
- Buyer
- Owner
- Agent
- Admin

Guests are unauthenticated visitors, not database users.

## Authentication plan

Use token-based authentication suitable for web and mobile.

```text
Login
  ↓
Access token + Refresh token
  ↓
Client sends access token with GraphQL requests
  ↓
Django identifies the user
  ↓
Authorization checks permissions
```

The exact token library, expiration values, storage, refresh/revocation mechanism, and optional social login will be finalized during implementation.

Passwords are securely hashed and never stored as plaintext.

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
