# 19 — Web Frontend Architecture

## Status

Decision: React-based frontend with a simple feature-oriented architecture.

## Frontend Stack

- **React** — UI framework.
- **TypeScript** — static typing.
- **Vite** — development server and frontend build tool.
- **React Router** — client-side routing.
- **Apollo Client** — GraphQL client and server-state/cache management.
- **GraphQL Code Generator** — generate TypeScript types and GraphQL operations from the backend schema.
- **React Hook Form** — form state and submission handling.
- **Zod** — client-side schema validation.
- **Tailwind CSS** — styling.
- **shadcn/ui** — reusable UI components.

## Why This Stack

The frontend is primarily a client for the Django GraphQL backend. We do not need a second backend or a large full-stack framework.

React + TypeScript provides a strong general-purpose frontend stack, while Vite keeps the build simple. Apollo Client fits the project's GraphQL-first API. GraphQL Code Generator keeps frontend types aligned with the backend schema.

## Architecture

```text
Browser
   ↓
React
   ↓
Pages / Routes
   ↓
Feature Components / Hooks
   ↓
Apollo Client
   ↓
GraphQL API
   ↓
Django Backend
```

Real-time communication:

```text
React
  ↕
WebSocket
  ↕
Django
```

## Project Structure

Use a feature-oriented structure rather than one large global components/services directory.

```text
src/
├── app/
├── features/
│   ├── auth/
│   ├── properties/
│   ├── listings/
│   ├── favorites/
│   ├── viewings/
│   ├── messaging/
│   ├── notifications/
│   └── ai/
├── shared/
│   ├── components/
│   ├── hooks/
│   └── utils/
└── graphql/
```

Features should own their UI, hooks, GraphQL operations, and feature-specific logic where practical.

## Routing

Use **React Router** for application routes.

Routes will cover areas such as:

- Home/search
- Property details
- Login/register
- Favorites
- Viewings
- Messages
- Notifications
- Profile
- Listing management
- AI features

Protected routes should enforce authentication at the frontend for UX, while the backend remains the actual security boundary.

## GraphQL

Apollo Client is the primary data layer for communication with Django.

Responsibilities:

- Queries
- Mutations
- Cache management
- Loading/error states
- Refetching and cache updates where appropriate

Use **GraphQL Code Generator** so frontend types and operations are derived from the backend GraphQL schema instead of being manually duplicated.

Do not add a second server-state library unless a real requirement appears. Apollo Client is sufficient initially.

## State Management

Do **not** introduce Redux initially.

Use:

- Apollo Client for server state.
- React state for local component state.
- React Context only for genuinely shared client-side state when appropriate.

Add another state-management library only if the application develops a concrete need that the existing approach cannot handle cleanly.

## Authentication

Web authentication follows the backend decision:

- Authentication uses secure, HttpOnly cookies.
- Do not store authentication tokens in `localStorage`.
- Frontend tracks the current authenticated user/session state.
- Role/permission information can control UI visibility, but backend authorization is authoritative.

## Forms & Validation

Use **React Hook Form + Zod**.

```text
User input
   ↓
React Hook Form
   ↓
Zod validation
   ↓
GraphQL mutation
   ↓
Django validation
```

Client-side validation improves UX; it does not replace backend validation.

## UI & Styling

Use **Tailwind CSS + shadcn/ui**.

Goals:

- Reusable components
- Consistent design
- Responsive layouts
- Accessible controls
- Easy customization

Avoid introducing a large UI framework when the project does not need one.

## Loading, Empty & Error States

Major screens and operations should explicitly handle:

- Loading
- Success
- Empty results
- Validation errors
- Authentication errors
- Authorization errors
- Network/server errors

User-facing messages should follow the backend error-handling strategy while keeping internal error details hidden.

## Real-Time Features

Use WebSockets only where real-time communication is useful:

- Chat messages
- Important notifications
- Viewing status updates
- Long-running AI operation progress/results

Normal property/search/listing operations remain GraphQL requests.

## Images

Property media is image-only for the initial project scope.

Frontend requirements:

- Responsive images
- Lazy loading where appropriate
- Thumbnail/preview usage where useful
- Clear upload validation and feedback

Actual files are handled by the backend/media-storage architecture, not stored in the frontend repository.

## Performance

Initial priorities:

- Code splitting where useful
- Lazy-load non-critical routes/components
- Optimize image loading
- Avoid unnecessary GraphQL requests
- Use Apollo caching appropriately
- Paginate large property/message lists

Do not introduce complex frontend performance infrastructure without evidence that it is needed.

## Accessibility

Follow basic accessibility requirements:

- Semantic HTML
- Keyboard navigation
- Visible focus states
- Proper labels
- Appropriate ARIA usage
- Sufficient contrast
- Accessible loading/error feedback

## Frontend Testing

Frontend testing follows the project's broader testing strategy.

Tools:

- **Vitest** — frontend unit tests.
- **React Testing Library** — component/behavior tests.
- **Playwright** — browser-level E2E tests.

Strategy:

- Unit-test reusable logic.
- Component-test important UI behavior.
- Mock GraphQL in isolated frontend tests.
- Use real backend integration mainly through E2E tests.
- Keep E2E coverage focused on critical user journeys.

## SEO & Social Media Metadata Strategy (SPA Pre-rendering)

Because real estate marketplaces depend heavily on organic search indexing (Google, Bing) and rich link previews on social platforms (WhatsApp, Facebook, Twitter, iMessage), a standard client-rendered SPA requires deliberate SEO handling:

### 1. Dynamic Document Head Management
Use `@unhead/react` or `react-helmet-async` on every property listing page:
- Canonical URLs (`<link rel="canonical" href="...">`)
- Structured JSON-LD metadata for RealEstateListing (`schema.org/Product` or `schema.org/RealEstateListing`)
- OpenGraph tags (`og:title`, `og:description`, `og:image`, `og:price:amount`, `og:price:currency`)

### 2. Bot Detection & Static Snapshot Serving (Pre-rendering)
For search engine bots and social scrapers (`Googlebot`, `bingbot`, `Twitterbot`, `facebookexternalhit`, `WhatsApp`):
- **Caddy / Reverse Proxy Rule:** When a crawler user-agent is detected requesting `/properties/:id`, Caddy either serves a lightweight pre-rendered HTML snapshot generated on property publication/update, or delegates to a serverless edge function / prerender service.
- **Human Visitors:** Receive the full Vite React SPA bundle with rich interactive client hydration, Apollo cache, and instant client-side navigation.

This delivers 100% SEO indexability and rich social cards without abandoning the clean Vite + React SPA architecture.

---

## Build & Deployment

Vite produces the production frontend build (`dist/`).

The frontend should be deployable independently from Django while communicating with the same GraphQL/WebSocket backend.

Development and deployment will use the Docker/infrastructure decisions from the deployment plan.

## Decisions Not to Add Initially

- Next.js (Full-stack framework overhead avoided in favor of Vite SPA + pre-render snapshots)
- Redux
- Another server-state library alongside Apollo Client
- A separate frontend backend-for-frontend
- Microfrontend architecture
- Complex frontend state architecture
- Unnecessary UI frameworks

These can be reconsidered only if the application develops a concrete requirement.
