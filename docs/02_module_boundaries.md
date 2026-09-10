# System Architecture — Module Boundaries

## Architecture Decision

The application will initially use a **Modular Monolith** architecture.

This means the system will be one application/deployment unit, while the code is divided into modules with clear responsibilities and boundaries.

The architecture can be changed later if the application's real requirements justify it.

---

## Modules

The initial backend will be divided into five main modules:

```text
Backend
│
├── Users
│
├── Properties
│
├── Interactions
│
├── Communication
│
└── AI
```

### 1. Users

Responsible for:

- User accounts
- Registration
- Login
- User profiles
- Roles
- Permissions

Owns:

```text
users
```

---

### 2. Properties

Responsible for the real-estate inventory and its information.

Responsible for:

- Properties
- Listings
- Locations
- Property types
- Amenities
- Property media
- Listing management

Owns:

```text
properties
property_types
locations
amenities
property_amenities
property_media
listings
```

---

### 3. Interactions

Responsible for actions customers perform with properties.

Responsible for:

- Favorites
- Viewing requests
- Viewing management
- Property reviews and ratings

Owns:

```text
favorites
viewings
reviews
```

---

### 4. Communication

Responsible for communication between users, system notifications, and reporting/moderation.

Responsible for:

- Conversations and threaded messages
- System and user notifications
- User / property reports for administrative moderation

Owns:

```text
conversations
messages
notifications
reports
```

---

### 5. AI

Responsible for AI and machine-learning functionality.

Responsible for:

- Natural-language property search
- Property analysis
- Recommendations
- ML predictions
- AI-related processing

Owns:

```text
ai_predictions
ai_interactions
```

The exact AI architecture, models, and services will be decided later.

---

## Module Boundary Principles

### Clear Responsibility

Each module should have a clear business responsibility.

For example:

```text
Properties → manages properties and listings
Communication → manages messages and notifications
AI → manages AI/ML functionality
```

### Low Coupling

Modules should avoid unnecessary dependencies on each other.

Changing one module should not require changing many unrelated modules.

### High Cohesion

Things that belong to the same business responsibility should stay together.

For example, property types, amenities, media, and listings belong naturally to the Properties module.

### Data Ownership

Each module owns the data related to its responsibility.

Other modules can use that data through defined interfaces or services rather than directly changing another module's internal logic.

### Database Tables ≠ Modules

A database table does not automatically require its own module.

Modules are grouped according to **business responsibility**, not simply by the number of database tables.

---

## Initial Module Relationship

At a high level:

```text
                         Users
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Properties    Interactions  Communication
             │             │             │
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                           AI
```

This is only a high-level conceptual relationship. The exact communication mechanisms between modules have not been decided yet.

---



## Next Architecture Discussion

The next question is:

> **How should the modules communicate with each other?**

We need to decide when a module should:

- Call another module directly
- Use a service/use-case interface
- Publish an event
- Trigger an asynchronous background task

This decision will help us design the internal structure of the modular monolith without over-engineering it