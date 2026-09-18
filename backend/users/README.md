# 👤 Users Module

## Overview

The **Users Module** manages core identity, authentication, role-based authorization, and account lifecycles for the Real Estate Platform. Built with a decoupled **Service Layer** and a **Strawberry GraphQL API**, it provides secure JWT-based authentication for both web and mobile clients.

---

## 🏗️ Architectural Overview & File Structure

```text
backend/users/
├── admin.py          # Django Admin configuration for User management
├── apps.py           # Users AppConfig
├── auth.py           # JWT token generation & verification helpers
├── middleware.py     # Sync/Async JWT authentication middleware
├── models.py         # Custom User model & manager
├── permissions.py    # Strawberry GraphQL permission classes (IsAuthenticated, IsOwner, IsAgent)
├── schema.py         # Strawberry GraphQL Queries & Mutations
├── services.py       # Domain service layer (business logic & security rules)
├── types.py          # Strawberry GraphQL UserType definitions
└── tests/            # Test suite (models, services, API)
    ├── factories.py  # FactoryBoy user factories
    ├── test_api.py   # GraphQL integration tests
    ├── test_models.py# Model & manager unit tests
    └── test_services.py # Service layer unit tests
```

---

## 🔑 Key Architectural & Security Decisions

1. **Custom User Model (`models.py`)**
   - Extends `AbstractBaseUser` and `PermissionsMixin`.
   - Uses `email` as `USERNAME_FIELD` (no separate username required).
   - Inherits from `TimeStampedModel` for `created_at` / `updated_at` audit fields.
   - Inherits from `SoftDeleteModel` (`is_deleted`, `deleted_at`) to preserve relational integrity with properties and viewings.

2. **Role Capability Flags**
   - Uses boolean flags (`is_owner`, `is_agent`, `is_staff`) rather than complex role joins.
   - Allows users to act simultaneously as buyers and property owners.

3. **Decoupled Service Layer (`services.py`)**
   - Encapsulates domain workflows (`register_user`, `authenticate_user`, `change_password`, `request_password_reset`, `confirm_password_reset`).
   - Keeps GraphQL resolvers thin by moving validation and database operations into reusable functions.
   - Enforces Django's `AUTH_PASSWORD_VALIDATORS` during registration, password changes, and resets.

4. **JWT Authentication & Middleware (`auth.py` & `middleware.py`)**
   - Issues short-lived access tokens (15 minutes) and long-lived refresh tokens (7 days).
   - `jwt_auth_middleware` runs on both sync and async HTTP requests, decoding `Authorization: Bearer <token>` headers and attaching the user to `request.user`.

5. **Granular Permissions (`permissions.py`)**
   - Declarative Strawberry permission guards: `IsAuthenticated`, `IsOwner`, `IsAgent`.

---

## 📡 GraphQL Operations

### Queries
- `me`: Returns the profile of the currently authenticated user (`IsAuthenticated`).
- `users`: Returns a list of active users. Sensitive fields (password hash, admin flags) are strictly omitted.
- `owner_dashboard`: Protected query restricted to property owners (`IsOwner`).

### Mutations
- `login(input: LoginInput)`: Authenticates credentials and returns `access_token`, `refresh_token`, and `user`.
- `register(input: RegisterInput)`: Creates a new user, validates password strength, and auto-logs in returning tokens.
- `changePassword(input: ChangePasswordInput)`: Changes password for the logged-in user after verifying the current password (`IsAuthenticated`).
- `requestPasswordReset(input: PasswordResetRequestInput)`: Generates a secure single-use reset token and emails a reset link.
- `confirmPasswordReset(input: PasswordResetConfirmInput)`: Validates reset token and sets a new password.

---

## 🧪 Testing Strategy

The `users` module is covered by **36 automated tests** with **100% test coverage** across models, services, permissions, and GraphQL schemas:

- **`test_models.py` (6 tests)**: Verifies user creation, superuser creation, staff/superuser flag validation, email normalization, string representations, and soft-delete behaviors.
- **`test_services.py` (15 tests)**: Tests domain business logic, authentication failures, deactivated account handling, duplicate email detection, password validation rules (`validate_password`), and anti-enumeration reset link generation.
- **`test_api.py` (15 tests)**: Integration testing of GraphQL mutations (`login`, `register`, `changePassword`, `requestPasswordReset`, `confirmPasswordReset`), `me` query, RBAC guards (`IsOwner`, `IsAgent`), and JWT middleware invalid/inactive token rejection.