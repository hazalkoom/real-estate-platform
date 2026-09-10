# 21 — Shared Frontend Strategy

## Goal

Share platform-independent frontend code between the React web application and React Native mobile application without forcing the two platforms to share UI or platform-specific behavior.

The backend remains the source of truth for business rules.

---

## Repository Strategy

Use a monorepo.

```text
real-estate-platform/
├── backend/
├── web/
├── mobile/
├── shared/
└── docs/
```

Use a simple workspace-based setup such as npm or pnpm workspaces.

Do not introduce Turborepo, Nx, or another monorepo orchestration tool unless the project actually needs it.

---

## Shared Package

Keep the shared package intentionally small.

```text
shared/
├── graphql/
│   ├── queries/
│   └── mutations/
│
├── types/
│
└── validation/
```

Potentially add:

```text
shared/
└── constants/
```

only when genuinely useful.

The shared package must not become a dumping ground for unrelated code.

---

## What Should Be Shared

### GraphQL Operations

Share reusable GraphQL queries, mutations, fragments, and related API definitions where practical.

Examples:

- GetProperties
- GetProperty
- CreateFavorite
- RequestViewing
- SendMessage
- GetNotifications

Both clients communicate with the same Django GraphQL API.

### Generated Types

Use GraphQL Code Generator to generate TypeScript types from the backend GraphQL schema.

```text
Django GraphQL Schema
        ↓
   GraphQL Codegen
        ↓
   TypeScript Types
       /             ↓         ↓
    Web       Mobile
```

Do not manually duplicate API types across web and mobile.

### Validation

Share platform-independent validation schemas where practical.

```text
Shared Zod Schema
       ↓
   ┌───┴───┐
   ↓       ↓
  Web    Mobile
```

Frontend validation is for user experience. Backend validation remains mandatory.

### Platform-Independent Constants

Share constants only when they genuinely represent the same contract on both platforms.

Examples:

- listing status values
- property types
- API-related constants
- shared limits defined by the backend contract

---

## What Should Not Be Shared

Do not force the platforms to share:

- Web UI components
- Mobile UI components
- Layouts
- Navigation
- Styling
- Browser-specific code
- Native device code
- Platform-specific state
- Platform-specific UX

A property card may represent the same domain concept while having completely different implementations.

```text
WebPropertyCard
MobilePropertyCard
```

Sharing the data contract does not require sharing the visual component.

---

## Business Logic

Business rules belong to the Django backend.

Example:

```text
Can this user edit this listing?
```

The backend determines:

```text
Authenticated?
      ↓
Has permission?
      ↓
Owns / controls listing?
      ↓
Listing state allows editing?
```

Frontend checks may improve UX but must never be treated as authorization.

Do not duplicate important business rules independently in web and mobile.

---

## API Contract

The GraphQL schema is the shared contract between:

```text
Backend
   ↓
GraphQL Schema
   ↓
┌───────────────┐
│               │
Web           Mobile
```

When the backend schema changes:

1. Update the backend schema.
2. Regenerate frontend types.
3. Update affected GraphQL operations.
4. Run frontend tests.

Avoid manually maintaining separate API models for each client.

---

## Workspace Structure

The final frontend-oriented repository can look like:

```text
real-estate-platform/
│
├── backend/
│   └── Django
│
├── web/
│   └── React + Vite + TypeScript
│
├── mobile/
│   └── React Native + Expo + TypeScript
│
├── shared/
│   ├── graphql/
│   ├── types/
│   └── validation/
│
└── docs/
```

Web and mobile depend on `shared`.

```text
          shared
          /             ↓      ↓
       web    mobile
```

The backend does not depend on frontend code.

---

## Dependency Rules

- `shared` must remain platform-independent.
- `shared` must not import browser APIs.
- `shared` must not import React Native APIs.
- `web` may use web-specific dependencies.
- `mobile` may use native/mobile-specific dependencies.
- Both clients may consume the same shared package.
- Backend code must not depend on `web`, `mobile`, or `shared` frontend code.

---

## State Management

Do not create shared global frontend state merely to avoid duplication.

Web:

- Apollo Client for server state.
- React state/context for local UI state.

Mobile:

- Apollo Client for server state.
- React state/context for local UI state.

If a platform develops a genuine need for additional state management, solve it locally rather than automatically putting it into `shared`.

---

## Authentication

The API contract is shared, but credential handling remains platform-specific.

```text
Web
  ↓
Secure HttpOnly cookies

Mobile
  ↓
Platform secure storage
```

Do not create a shared token-storage implementation because browsers and mobile devices have different security mechanisms.

---

## Real-Time Communication

The real-time protocol and backend behavior are shared conceptually, but client implementations remain platform-specific.

```text
              Django
             /                  ↓        ↓
      WebSocket    WebSocket
          ↓            ↓
         Web         Mobile
```

Both clients can consume the same event/data contract while using platform-appropriate connection and UI behavior.

---

## Testing

Shared code should have its own tests where appropriate.

Client-specific code is tested in its own application.

```text
Shared tests
     ↓
Web tests
     ↓
Mobile tests
     ↓
End-to-end tests
```

Do not duplicate tests simply because both clients consume the same shared type.

Focus shared tests on actual shared behavior, such as validation.

---

## Code Generation

GraphQL Code Generator is part of the shared API workflow.

Expected flow:

```text
Change Django GraphQL Schema
          ↓
      Run Codegen
          ↓
Update generated TypeScript types
          ↓
   Type-check Web + Mobile
          ↓
       Run Tests
```

Generated files should follow one consistent project policy: either commit them for simple builds and CI, or regenerate them deterministically during CI. Do not mix approaches.

---

## Rules

1. Share contracts before sharing implementation.
2. Keep `shared/` small.
3. Never share UI just because both platforms use React.
4. Keep business rules in Django.
5. Use generated GraphQL types instead of duplicated API models.
6. Keep authentication storage platform-specific.
7. Keep navigation platform-specific.
8. Keep styling platform-specific.
9. Prefer local solutions over expanding the shared package.
10. Do not introduce a complex monorepo tool unless the project needs it.

---

## Final Architecture

```text
                         Django Backend
                              │
                        GraphQL Schema
                              │
                       GraphQL Codegen
                              │
                    ┌─────────┴─────────┐
                    ↓                   ↓
                 shared              shared
                    │                   │
             ┌──────┴──────┐     ┌──────┴──────┐
             ↓             ↓     ↓             ↓
          GraphQL       Types  GraphQL       Types
        Validation            Validation
             │                   │
             ↓                   ↓
            Web               Mobile
      React + Vite       React Native + Expo
```

The goal is **shared contracts and reusable platform-independent code, not a shared UI framework**.
