# 22 — Product UX & User Flows

## Goal

Define the main user journeys across web and mobile before implementation.

This document defines product flows, not visual design.

## User Types

- Guest
- Buyer
- Owner
- Agent
- Admin

## Guest Flow

```text
Landing / Home
      ↓
Browse / Search
      ↓
Property Results
      ↓
Property Details
      ↓
├── View Images
├── View Location
├── View Amenities
└── View Listing Information
      ↓
Protected Action
      ↓
Login / Register
```

Guests can browse publicly but must authenticate for personalized or protected actions.

## Buyer Flow

### Discover Property

```text
Home
 ↓
Search / Filters
 ↓
Property Results
 ↓
Property Details
```

Search supports location, buy/rent, property type, price, bedrooms, bathrooms, area, amenities, and AI natural-language search.

### Save Property

```text
Property Details
      ↓
Favorite
      ↓
Favorites
```

### Request Viewing

```text
Property Details
      ↓
Request Viewing
      ↓
Choose Date / Time
      ↓
Submit
      ↓
Pending
      ↓
Approved / Rejected
```

### Messaging

```text
Property Details
      ↓
Contact Agent / Owner
      ↓
Conversation
      ↓
Messages
```

## Owner Flow

```text
Login
  ↓
Owner Dashboard
  ↓
Create / Manage Property
  ↓
Add Images
  ↓
Create Listing
  ↓
Set Sale / Rent + Price
  ↓
Publish
```

Management includes editing, image management, price/status changes, and removal/expiration.

Viewing requests:

```text
Viewing Requests
      ↓
Request Details
      ↓
Approve / Reject
      ↓
Customer Notified
```

## Agent Flow

Agents manage properties and listings they are authorized to manage.

```text
Agent Dashboard
      ↓
Assigned / Managed Listings
      ↓
Property / Listing
      ├── Edit
      ├── Manage Images
      ├── Update Price
      └── Update Status
```

Viewing and communication follow the same interaction model.

## AI Search Flow

```text
User
 ↓
Natural-language search
 ↓
AI interprets request
 ↓
Structured criteria + semantic intent
 ↓
Property Search
 ↓
Ranked Results
```

The backend validates and applies actual filters.

## AI Property Analysis

```text
Property
   ↓
AI Analysis
   ↓
Price / Demand / Investment information
   ↓
Display result
```

AI output is derived information, not authoritative property data.

## Notifications

Important events can produce notifications:

- New message
- Message reply
- Viewing approved/rejected
- Viewing changed/completed
- Important listing activity

```text
Backend Event
     ↓
Notification
     ↓
PostgreSQL
     ↓
WebSocket when online
     ↓
Client UI
```

Offline users retrieve notifications through GraphQL.

## Reporting

```text
Property / User / Content
        ↓
Report
        ↓
Select reason
        ↓
Submit
        ↓
Admin review
```

## Core Navigation

Web:

```text
Home
Search
Property Details
Favorites
Messages
Notifications
Profile
```

Owner/Agent additionally use:

```text
Dashboard
Listings
Viewing Requests
```

Mobile prioritizes the most common actions:

```text
Home
Search
Favorites
Messages
Profile
```

Admin navigation is separate and role-protected.

## Universal UI States

Important screens must support:

- Loading
- Success
- Empty
- Validation Error
- Unauthorized
- Forbidden
- Not Found
- Network Error
- Server Error

Property lists additionally support no-results, loading-more, and end-of-results states.

## Core End-to-End Journeys

Prioritize:

1. Guest searches for a property.
2. User opens property details.
3. User registers/logs in.
4. User favorites a property.
5. User requests a viewing.
6. Owner/agent approves or rejects it.
7. User and owner/agent exchange messages.
8. Owner/agent creates and publishes a listing.
9. User performs AI natural-language search.
10. User receives important notifications.

## UX Principles

- Search and discovery should be fast and obvious.
- Require authentication only when necessary.
- Give clear feedback for important actions.
- Never silently hide failures.
- Web and mobile can use different layouts and navigation.
- Keep common actions reasonably short.
- Do not design features before their product flow is understood.
