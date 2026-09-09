# 10 — AI/ML Architecture

## Decision

The project will have a dedicated **AI module** inside the modular monolith.

AI is treated as another dependency/service of the backend. It helps the application understand language, search by meaning, make recommendations, and produce predictions. AI does not replace the core backend or become the source of truth.

## AI vs ML — simple explanation

- **AI** is the broader idea of software performing tasks that normally require human-like understanding.
- **Machine Learning (ML)** is one way of building AI by learning patterns from data.
- **LLMs** are AI models that are especially useful for understanding and generating natural language.
- **Embeddings** turn text into vectors that represent meaning. Similar meanings produce similar vectors.

The backend engineer does not need to build every model from scratch. Existing models/providers can be used behind our own application interfaces.

## AI responsibilities

The AI module will initially support:

1. Natural-language property search
2. Semantic property search using embeddings
3. Property questions / analysis
4. Property recommendations
5. ML-based price estimation
6. Future demand/investment predictions

## High-level architecture

```text
                    AI MODULE
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
 Natural Language   Embeddings       ML Models
       │               │                │
       ↓               ↓                ↓
      LLM          Vector DB        Predictions
       │                                │
       └──────────────┬─────────────────┘
                      ↓
                 AI Services
                      ↓
                 Django Modules
```

## 1. Natural-language search

A user can write something such as:

> "I want a cheap 2-bedroom apartment in Cairo with parking and a balcony."

The LLM converts the request into structured search criteria:

```text
property_type = apartment
listing_type = RENT
bedrooms >= 2
city = Cairo
parking = true
balcony = true
price = low
```

The **Properties module** then performs the actual database search.

The LLM must not directly query PostgreSQL.

### Flow

```text
User
 ↓
GraphQL
 ↓
AI Module
 ↓
LLM
 ↓
Structured criteria
 ↓
Properties Module
 ↓
PostgreSQL
 ↓
Results
```

## 2. Embeddings and semantic search

An embedding converts text into a vector representing its meaning.

For example:

```text
"peaceful family home"
        ↓
     Embedding
        ↓
   [many numbers]
```

A property description can also be embedded and stored in the vector database.

Later, a search such as:

> "somewhere quiet for my family"

can find properties with similar meaning even when the exact words do not match.

### Flow

```text
Property description
 ↓
Embedding model
 ↓
Vector
 ↓
Vector DB
```

For a search:

```text
User query
 ↓
Embedding model
 ↓
Query vector
 ↓
Vector DB
 ↓
Similar properties
```

## 3. Hybrid search

The project will combine normal structured filtering with semantic search.

Example:

> "3 bedroom apartment in Cairo under 5 million, somewhere quiet."

The AI can separate this into:

```text
Structured:
- 3 bedrooms
- apartment
- Cairo
- price <= 5,000,000

Semantic:
- "somewhere quiet"
```

Then:

```text
             Search query
                  ↓
                 AI
                  ↓
       ┌──────────┴──────────┐
       ↓                     ↓
Structured criteria      Semantic text
       ↓                     ↓
 PostgreSQL              Vector DB
       └──────────┬──────────┘
                  ↓
             Merge / rank
                  ↓
               Results
```

This allows the application to use PostgreSQL for exact filters and the vector database for meaning.

## 4. Recommendations

Recommendations will start simple rather than using a complicated recommendation system.

Possible inputs:

- Properties the user viewed
- Favorites
- Search preferences
- Similar properties

Initial approach:

```text
User activity/preferences
        ↓
Similar properties
        ↓
Vector search / filtering
        ↓
Ranking
        ↓
Recommendations
```

More advanced ML recommendation models can be added later if the project has enough useful data.

## 5. ML price estimation

The project can use historical property data to estimate a property's price.

Example inputs:

```text
area
bedrooms
bathrooms
location
property type
furnished
parking
...
```

The ML model learns patterns from existing property data and produces an estimate.

```text
Historical property data
        ↓
     ML model
        ↓
 Learned patterns
        ↓
    Prediction
```

For a new property:

```text
Property
 ↓
ML model
 ↓
Estimated price
 ↓
Save prediction
```

Predictions belong in the existing `ai_predictions` table rather than modifying the core property data.

## 6. Synchronous vs background AI

AI operations that are small and need an immediate answer can run synchronously.

Examples:

- Natural-language search
- Simple property question

Expensive operations should run in the background with Celery.

Examples:

- Generate property embeddings
- Heavy property analysis
- Batch recommendations
- ML batch processing
- Large AI reports

### Background flow

```text
Django
 ↓
AI Service
 ↓
Celery
 ↓
AI Provider / Model
 ↓
Result
 ↓
PostgreSQL / Vector DB
 ↓
Notification / real-time update
```

## 7. AI provider abstraction

Application modules should not directly depend on a specific AI provider everywhere.

Instead:

```text
Application
    ↓
AI Service / Interface
    ↓
Provider implementation
    ↓
LLM / Embedding / ML system
```

For example, application code should conceptually request:

```text
generate_search_query(...)
```

rather than spreading provider-specific API calls throughout the codebase.

This makes it easier to change providers or models later.

## 8. AI is not the source of truth

PostgreSQL remains the source of truth for application data.

The vector database contains derived AI data such as embeddings.

AI predictions are derived data stored in `ai_predictions`.

If an AI provider or vector database is temporarily unavailable:

- Properties still work
- Listings still work
- Favorites still work
- Viewings still work
- Messaging still works
- Normal search still works

Only affected AI features should degrade or become temporarily unavailable.

## 9. AI failures

AI failures follow the reliability rules from section 09.

Examples of transient failures:

- AI provider timeout
- Temporary provider outage
- Vector DB unavailable
- Network failure

These can be retried where appropriate, especially in background jobs.

Permanent errors should not be repeatedly retried.

Client-facing errors should remain safe and understandable, while detailed provider/model errors go to logs.

## 10. Security and control

The AI layer must not be allowed to bypass normal application authorization.

For example, an AI request asking about a property must still go through the same permission rules that apply to normal property access.

The LLM should not receive unrestricted access to:

- PostgreSQL
- Internal services
- User accounts
- Secrets
- Administrative operations

The backend controls what information is provided to the model and what actions can be performed.

## 11. Initial scope

To keep the project manageable, the first AI implementation should focus on:

1. Natural-language property search
2. Embeddings + vector search
3. Basic property recommendations
4. One useful ML prediction, such as price estimation

More advanced AI features can be added after the core system works.

## Final architecture

```text
                         Web / Mobile
                              ↓
                         GraphQL API
                              ↓
                    Django Modular Monolith
                              │
       ┌──────────────────────┼──────────────────────┐
       ↓                      ↓                      ↓
   Core Modules           AI Module              Celery
       │                      │                      │
       ↓              ┌───────┼───────┐              ↓
  PostgreSQL          ↓       ↓       ↓         Background AI
   (source)          LLM  Embeddings  ML             │
                           │          │               │
                           ↓          ↓               ↓
                       Vector DB  Predictions   PostgreSQL /
                                                  Vector DB
```

## Principles

1. AI assists the backend; it does not replace it.
2. LLMs handle language-related tasks.
3. Embeddings + vector DB handle semantic similarity/search.
4. ML models handle data-driven predictions.
5. PostgreSQL remains the source of truth.
6. AI does not directly access the database.
7. Expensive AI work runs through Celery.
8. AI providers are hidden behind our own interfaces.
9. AI failures must not break core property functionality.
10. Start simple and add more advanced AI only when justified.
