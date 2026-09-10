# 16 — Security Architecture

## Goal

Protect users, application data, infrastructure, and external integrations without over-engineering security for a solo-developer modular monolith.

## Authentication

- Use Django's password hashing; never implement password hashing ourselves.
- Use access tokens + refresh tokens.
- Web clients: store authentication tokens using HttpOnly + Secure cookies.
- Mobile clients: use platform secure storage.
- Use Django's CSRF protection for cookie-based browser authentication.
- Never store passwords, tokens, or secrets in plaintext.

## Authorization

Authorization is enforced server-side and is based on:

- Role
- Permission
- Resource ownership/assignment
- Resource state

Roles:

- Guest
- Buyer
- Owner
- Agent
- Admin

Rules:

- Never trust frontend authorization checks.
- Protected operations must be authorized in the backend.
- Owners can manage their own/authorized resources.
- Agents can manage assigned/authorized listings.
- Buyers can interact with resources but cannot manage other users' listings.
- Admin has platform-level permissions.

## GraphQL Security

Use GraphQL with:

- Query depth limits
- Query complexity limits
- Pagination with sensible maximum page sizes
- Input validation
- Authentication/authorization checks on protected fields and mutations
- Rate limiting
- Appropriate production introspection policy

Avoid exposing expensive unrestricted queries.

## Rate Limiting

Use Redis-backed rate limiting.

Apply different limits according to operation cost/risk rather than one global limit.

Stricter limits should apply to:

- Login/authentication attempts
- Password-related operations
- AI operations
- Expensive GraphQL queries
- Messaging/reporting operations where abuse is possible

## CSRF

Use Django's built-in CSRF protection for browser cookie authentication.

Configure trusted origins and cookie security correctly for production.

## CORS

Use an explicit allowlist for trusted web origins.

Do not use unrestricted `*` for authenticated browser APIs.

Mobile applications are not subject to browser CORS in the same way.

## HTTPS / TLS

Production uses HTTPS everywhere.

- No plaintext authentication traffic.
- TLS termination can be handled by the reverse proxy, load balancer, or hosting platform.
- Enable HSTS in production when appropriate.

## Admin Panel & Moderation Interface

For platform operations, user moderation, report reviews, and system oversight:
- **Django Built-in Admin:** Leveraged as the primary administrative dashboard (`/admin/`).
- **Security Hardening:**
  - Placed behind Django `is_staff` and `is_superuser` role checks.
  - Rate-limited and protected with brute-force lockout (`django-axes`).
  - Styled and customized using `django-unfold` or `jazzmin` for a modern, high-polish UI.
  - Dedicated audit logs tracking all administrative actions (approvals, user bans, listing removals).

---

## Transactional Email Architecture

Critical communications (welcome verification, password reset, viewing confirmations, offline message notifications) use a decoupled async pipeline:
- **Template System:** HTML email templates using Django's template engine.
- **Provider:** Decoupled behind Django's `EMAIL_BACKEND` abstraction:
  - Local Dev: Console backend / Mailpit container in Docker (`http://localhost:8025`).
  - Production / Demo: Free tier of **Resend** (3,000 emails/month free) or **Brevo** (300 emails/day free, no credit card required).
- **Execution:** Dispatched asynchronously via Celery workers to keep API response times instantaneous.

---

## Secrets

Never commit secrets to Git.

Examples:

- Django secret key
- Database credentials
- Redis credentials
- AI provider keys
- Sentry credentials/configuration

Development:

- `.env` / environment variables

Production:

- Hosting/provider secret or environment-variable system

The existing `.gitignore` must keep local `.env` files out of Git.

## SQL / Database Security

- Prefer Django ORM.
- Avoid raw SQL unless justified.
- Parameterize all user-controlled SQL values.
- Keep PostgreSQL private; it must not be publicly accessible.
- Use least-privilege database credentials where practical.

## XSS Protection

Treat user-generated content as untrusted input.

Relevant data includes:

- Property descriptions
- Comments
- Messages
- Profile data

Do not render untrusted HTML directly. Configure appropriate security headers and content handling.

## File Upload Security

Property media is image-only.

Validate:

- Actual file type
- Allowed formats
- File size
- Image dimensions where appropriate

Additional rules:

- Generate storage filenames ourselves.
- Never trust user-provided paths or filenames.
- Store uploaded files outside PostgreSQL.
- Use isolated object/file storage in production.
- Do not allow uploaded content to become executable code.

## AI Security

AI systems are untrusted external dependencies.

Critical rule:

> LLMs never receive direct database access.

Flow:

```text
User input
   ↓
AI service
   ↓
Structured / generated result
   ↓
Backend validation
   ↓
Normal application logic
   ↓
PostgreSQL / other systems
```

Rules:

- Treat AI output as untrusted input.
- Validate AI-generated structured data before using it.
- Separate system instructions from user/retrieved content.
- Defend against prompt injection where AI features process user-generated or retrieved text.
- Keep AI credentials server-side.

## Vector Database Security

The vector database is a backend dependency and is not publicly exposed.

- Backend-only access.
- Credentials stored as secrets.
- Network access restricted to required application components.

## Infrastructure Security

Keep core infrastructure private where possible:

- PostgreSQL
- Redis
- Vector database
- Celery/internal services

Only required public entry points should be exposed, primarily the web/API endpoint and real-time endpoint through the production edge/reverse proxy.

## Security Headers

Configure appropriate HTTP security headers, including where applicable:

- Content-Security-Policy
- X-Content-Type-Options
- Referrer-Policy
- Strict-Transport-Security in production
- Appropriate framing/clickjacking protection

Use Django/hosting configuration rather than custom implementations where possible.

## Dependency & Code Security

Tools:

- **Bandit** — Python security analysis.
- **pip-audit** — known Python dependency vulnerabilities.
- **OWASP ZAP** — dynamic web security testing against local/staging environments.

Keep dependencies controlled and review major upgrades.

## Security Testing

Automated and manual security tests cover:

- Authentication bypass
- Authorization bypass
- IDOR/resource ownership violations
- Expired/invalid tokens
- CSRF
- Rate-limit enforcement
- GraphQL abuse/expensive queries
- Injection attempts
- XSS-related input handling
- Malicious/oversized file uploads
- Sensitive information leakage
- AI prompt injection scenarios

Use:

- pytest
- Playwright
- Bandit
- pip-audit
- OWASP ZAP
- Manual testing for authorization and business-logic vulnerabilities

## Logging & Security

Never log:

- Passwords
- Access tokens
- Refresh tokens
- API keys
- Session secrets

Avoid unnecessarily logging sensitive personal information.

Security events should remain useful for investigation while following data-minimization principles.

## Security Principles

1. Never trust the client.
2. Authenticate before protected operations.
3. Authorize every protected operation server-side.
4. Combine role checks with ownership/assignment checks.
5. Treat external services and AI output as untrusted.
6. Keep databases and internal infrastructure private.
7. Never expose secrets in source code, API responses, or logs.
8. Validate uploads and user-generated content.
9. Rate-limit abuse-prone operations.
10. Prefer proven framework security features over custom security implementations.
11. Keep the security architecture proportional to the project.
