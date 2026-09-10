# 20 — Mobile Architecture

## Goal

Build a mobile client for the real-estate platform without creating a second backend or duplicating business logic.

The mobile application is a client of the existing Django GraphQL API.

---

## Technology Choices

| Area | Choice |
|---|---|
| Framework | React Native |
| Development / Build | Expo |
| Language | TypeScript |
| API | GraphQL |
| GraphQL Client | Apollo Client |
| Navigation | React Navigation |
| Forms | React Hook Form |
| Validation | Zod |
| Styling | NativeWind |
| Testing | React Native Testing Library + Jest/Vitest |
| Push Notifications | Expo Notifications |
| Secure Storage | Expo SecureStore |

### Why React Native + Expo

- Reuses React and TypeScript knowledge from the web frontend.
- Avoids learning a completely separate UI ecosystem.
- Expo simplifies development, device testing, builds, and native functionality.
- The backend/API remains completely independent of the mobile framework.

---

## High-Level Architecture

```text
Mobile App
    ↓
React Native + Expo
    ↓
Screens
    ↓
Features / Components
    ↓
Apollo Client
    ↓
GraphQL API
    ↓
Django Backend
```

Real-time communication:

```text
React Native
     ↕
 WebSocket
     ↕
   Django
```

The mobile app does not contain backend business logic.

---

## Project Structure

```text
mobile/
└── src/
    ├── app/
    │   ├── navigation/
    │   └── providers/
    │
    ├── features/
    │   ├── auth/
    │   ├── properties/
    │   ├── listings/
    │   ├── favorites/
    │   ├── viewings/
    │   ├── messaging/
    │   ├── notifications/
    │   └── ai/
    │
    ├── components/
    ├── hooks/
    ├── graphql/
    └── utils/
```

Use feature-based organization rather than organizing the entire application only by technical type.

---

## API Communication

The mobile application communicates with Django through GraphQL.

```text
Mobile
  ↓
Apollo Client
  ↓
GraphQL
  ↓
Django
  ↓
Application Services
  ↓
PostgreSQL
```

Use GraphQL for:

- Property search
- Property details
- Authentication
- Favorites
- Viewings
- Listings
- Messaging
- Notifications
- AI features
- User profiles

Do not create a separate mobile API.

---

## Authentication

Mobile authentication uses access and refresh tokens.

```text
Login
  ↓
Django
  ↓
Access + Refresh Token
  ↓
Secure device storage
```

Rules:

- Never store authentication tokens in ordinary local storage.
- Use platform-secure storage such as Expo SecureStore.
- Refresh access tokens when required.
- Clear stored credentials on logout.
- Re-authenticate when the refresh mechanism is no longer valid.

The exact token implementation follows the backend authentication architecture.

---

## Navigation

Use React Navigation.

Main customer navigation can contain:

```text
Home
Search
Favorites
Messages
Profile
```

Example property flow:

```text
Home
  ↓
Property Details
  ↓
Request Viewing
```

Authenticated and role-specific screens should be protected through navigation guards and backend authorization.

Navigation protection is only a client-side UX layer. The backend remains the source of truth for permissions.

---

## Core Mobile Features

### Customer

- Registration/login
- Browse properties
- Search and filtering
- Property details
- Property images
- Favorites
- Request viewing
- Messages
- Notifications
- AI search

### Owner / Agent

- Manage properties
- Manage listings
- Upload property images
- Manage viewing requests
- Messages
- Notifications

Do not require the mobile application to implement every feature of the web application immediately.

---

## Device Capabilities

Use native device functionality only where it provides real value.

Potential features:

- Camera → property photos
- Photo library → image selection
- Push notifications
- GPS/location
- Maps
- Deep links
- Secure credential storage

Do not add native functionality without a product requirement.

---

## Images

The backend stores image metadata and URLs.

The mobile application:

1. Requests property media through GraphQL.
2. Loads images from their URLs.
3. Uses lazy/loading-friendly image handling.
4. Uploads images through the backend's supported media flow.

Images should be optimized for mobile bandwidth and screen sizes.

---

## Real-Time Features

Use WebSockets only where real-time behavior is useful:

- Chat messages
- Important notifications
- Viewing status changes
- Long-running AI operation progress/results

Normal property browsing and search continue to use GraphQL.

WebSocket messages are not the permanent source of truth. Important data remains stored in PostgreSQL and can be synchronized through GraphQL after reconnecting.

---

## State Management

Do not introduce Redux by default.

Use:

- Apollo Client → server/API state
- React state → local component state
- React Context → small application-wide UI state where appropriate

Add another state-management library only if real complexity appears that these tools cannot handle cleanly.

---

## Forms and Validation

Use:

```text
React Hook Form
      ↓
Zod
      ↓
GraphQL Mutation
      ↓
Django Validation
```

Client validation improves UX.

Backend validation remains mandatory and authoritative.

---

## Error / Loading / Empty States

Every important screen should account for:

- Loading
- Successful result
- Empty result
- Validation errors
- Authentication errors
- Authorization errors
- Network failures
- Server errors
- Offline/reconnection states where relevant

Do not assume the network is always available on mobile.

---

## Testing

Use a testing pyramid similar to the web frontend.

### Component / Unit Tests

- React Native Testing Library
- Jest/Vitest

Test:

- Components
- Hooks
- UI behavior
- Form validation
- Local logic

Mock GraphQL/network communication where appropriate.

### End-to-End

Use Playwright where applicable to the overall application strategy, and use an appropriate mobile E2E solution if real-device/mobile-specific testing becomes necessary.

Prioritize critical journeys:

- Login
- Search property
- View property
- Favorite property
- Request viewing
- Send message

Do not attempt exhaustive E2E coverage.

---

## Security Rules

- Store tokens only in secure device storage.
- Never trust client-side role checks.
- Backend authorization is authoritative.
- Never embed secrets/API keys that must remain private inside the mobile application.
- Validate uploaded images.
- Use HTTPS in deployed environments.
- Treat all API responses as untrusted input.
- Avoid sensitive information in logs.

---

## Offline / Connectivity

The app should tolerate temporary network failures.

Initial approach:

- Apollo cache for useful previously fetched data.
- Show clear network/error states.
- Retry safe requests when appropriate.
- Reconnect WebSockets automatically.
- Synchronize important data from the backend after reconnecting.

Do not build a full offline-first architecture unless the product later requires it.

---

## Performance

Priorities:

- Efficient image loading.
- Pagination for property lists and messages.
- Avoid unnecessary GraphQL fields.
- Avoid rendering huge lists at once.
- Use appropriate list virtualization.
- Cache useful GraphQL data.
- Keep WebSocket usage limited to real-time features.

Measure before introducing complex mobile performance infrastructure.

---

## Development Principles

- Mobile is a client, not a second backend.
- Reuse React + TypeScript knowledge from the web.
- Keep business logic in Django.
- Keep UI logic in the mobile application.
- Reuse API contracts, not entire UIs.
- Prefer Expo/native capabilities only when needed.
- Avoid unnecessary state-management libraries.
- Avoid full offline-first architecture.
- Keep mobile architecture consistent with the web and backend architecture.
