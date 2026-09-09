# System Requirements — User Story

## Overview

The application is a real-estate marketplace where customers can discover properties, search for homes and other real-estate listings, contact sellers or agents, save properties, arrange viewings, and receive notifications.

The platform also provides AI-powered search, property analysis, and recommendations.

The following describes the intended user experience and core system requirements. Technical architecture and implementation decisions will be planned separately.

---

## Customer Journey

### 1. Open the Application

A customer opens the application and sees:

- A welcome screen
- Information about what the platform is
- An option to log in
- An option to continue as a guest

Guests can browse and search properties without creating an account.

---

### 2. Discover Properties

The customer can enter the property discovery experience and browse available listings.

They can:

- Discover properties
- Search for homes and other real-estate listings
- Filter properties
- View property details
- View property images and media
- See property amenities
- See ratings and comments
- Save properties
- Contact the seller or agent
- Request a property viewing

Some actions require authentication.

For example:

- Browsing and searching → available to guests
- Saving a property → login required
- Commenting/rating → login required
- Contacting a seller/agent → login required
- Requesting a viewing → login required

---

## Property Search

Customers can search and filter properties using different criteria.

Possible filters include:

- Property type
- Buy or rent
- Price range
- Location
- Number of bedrooms
- Number of bathrooms
- Area
- Furnished
- Parking
- Elevator
- Balcony
- Garden
- Swimming pool
- Other amenities

The search system should allow customers to combine multiple filters.

---

## Property Details

A customer can open a property and see information such as:

- Title
- Description
- Price
- Location
- Property type
- Bedrooms
- Bathrooms
- Area
- Amenities
- Images/videos
- Listing information
- Seller/agent information
- Ratings and comments

The customer can also save the property, contact the seller/agent, or request a viewing if logged in.

---

## Sellers and Property Owners

Property owners/sellers can submit their property details and preferred contact method.

The platform can connect sellers with verified agents active in their area.

A possible seller flow is:

### 1. Submit Your Details

The seller provides information about their property and preferred contact method.

### 2. Get Matched with Verified Agents

The platform can share the seller's details with suitable verified agents active in the relevant area.

### 3. Agents Reach Out

Verified agents can contact the seller to discuss:

- Property valuation
- Marketing
- Representation
- Listing the property

### 4. Choose an Agent and List the Property

The seller chooses the agent they want to work with.

The selected agent can then create/manage the property's listing on the platform.

---

## Listing Management

Sellers/owners or authorized agents can manage their listings.

They can:

- Create a listing
- Edit listing information
- Add or remove property media
- Update the price
- Change listing status
- Remove a listing
- Mark a property as sold
- Mark a property as rented

---

## Viewings

Logged-in customers can request a viewing for a property.

The seller or agent can:

- View viewing requests
- Accept a request
- Reject a request
- Manage the scheduled time
- Mark a viewing as completed
- Cancel a viewing

Customers can see the status of their viewing requests.

---

## Communication

Logged-in customers can contact sellers or agents.

Users can:

- Send messages
- Receive replies
- See message history
- Receive notifications for new messages

The system should provide real-time notifications when appropriate, such as when:

- Someone contacts a seller/agent
- A seller/agent replies
- A viewing request is accepted or rejected
- Other important activity occurs

---

## Ratings and Comments

Customers can see ratings and comments associated with properties.

Authenticated users can potentially:

- Leave a rating
- Leave a comment
- Edit or remove their own comment

The exact rating/comment rules will be decided during later system design.

---

## Favorites

Authenticated customers can save properties to their favorites.

They can:

- Add a property to favorites
- Remove a property from favorites
- View their saved properties

---

## AI Features

The platform will include AI-powered functionality.

### AI Search

Customers can describe what they want using normal language.

For example:

> "Find me a three-bedroom apartment in New Cairo under 5 million with parking and furnished."

The AI can understand the request and turn it into structured search criteria.

### Property Analysis

AI can analyze property information and provide useful insights.

### Recommendations

The system can recommend properties based on available property data and customer activity.

The exact AI architecture and models will be decided later.

---

## Reports and Safety

Users should be able to report problematic content or users.

Possible reasons include:

- Fake property
- Scam
- Incorrect information
- Inappropriate content
- Suspicious user

Reported content can later be reviewed by administrators.

---

## Guest vs. Authenticated User

### Guest

A guest can:

- Browse properties
- Search properties
- Filter properties
- View property details
- View ratings/comments
- Use available public AI search functionality

A guest cannot:

- Save properties
- Contact sellers/agents
- Request viewings
- Comment or rate
- Access private account features

### Authenticated Customer

An authenticated customer can do everything a guest can do, plus:

- Save properties
- Contact sellers/agents
- Request viewings
- Send and receive messages
- Rate properties
- Comment
- Manage their account

### Seller / Owner / Agent

Authorized sellers, owners, and agents can:

- Manage properties/listings
- Receive customer inquiries
- Communicate with customers
- Manage viewing requests
- Update listing information
- Manage listing status

---

## Scope Boundary

This document describes **what the system should do**, not how it will be built.

The following decisions are intentionally left for later:

- Monolith vs. modular monolith vs. microservices
- Backend architecture
- System architecture
- Design patterns
- API design
- Authentication implementation
- AI/ML architecture
- Infrastructure
- Deployment
- Caching
- Background processing
- Real-time implementation

These will be designed after the requirements are established.
