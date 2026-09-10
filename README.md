# Real Estate Platform

A real-estate marketplace platform where users can discover properties, search and filter listings, save properties, request viewings, communicate with owners/agents, receive notifications, and use AI-powered search, recommendations, analysis, and property predictions.

The project is being designed as a **modular monolith** with a Django backend, PostgreSQL, Redis, a dedicated vector database, background processing, real-time communication, and a web/mobile client architecture.

## Project Status

**Planning & architecture phase**

The product requirements and system architecture have been designed. Implementation will follow the documented decisions in `docs/`.

## Main Technologies

- Python / Django
- GraphQL
- PostgreSQL
- Redis
- Celery
- WebSockets
- Qdrant / vector database
- Docker / Docker Compose
- GitHub Actions
- Prometheus / Grafana
- Sentry
- OpenTelemetry
- pytest / Playwright

Some exact providers and implementation details may be finalized during implementation.

## Documentation

The architecture and engineering plan is split into focused documents:

1. [System Requirements](docs/01_system_requirements.md)
2. [Module Boundaries](docs/02_module_boundaries.md)
3. [Module Communication](docs/03_module_communication.md)
4. [Backend Internal Architecture](docs/04_backend_internal_architecture.md)
5. [API Architecture](docs/05_api_architecture.md)
6. [Authentication & Authorization](docs/06_authentication_authorization.md)
7. [Data & Database Strategy](docs/07_data_database_strategy.md)
8. [Background Processing & Real-Time](docs/08_background_processing_realtime.md)
9. [Reliability & Error Handling](docs/09_reliability_error_handling.md)
10. [AI/ML Architecture](docs/10_ai_ml_architecture.md)
11. [Real-Time Communication](docs/11_realtime_communication.md)
12. [File & Media Storage](docs/12_file_media_storage.md)
13. [Caching Strategy](docs/13_caching_strategy.md)
14. [Observability & Monitoring](docs/14_observability_monitoring.md)
15. [Testing & Quality](docs/15_testing_quality.md)
16. [Security Architecture](docs/16_security_architecture.md)
17. [Deployment & Infrastructure](docs/17_deployment_infrastructure.md)
18. [CI/CD](docs/18_ci_cd.md)
19. [Web Frontend Architecture](docs/19_web_frontend_architecture.md)
20. [Mobile Architecture](docs/20_mobile_architecture.md)
21. [Shared Frontend Strategy](docs/21_shared_frontend_strategy.md)
22. [Product UX & User Flows](docs/22_product_ux_and_user_flows.md)
23. [Frontend & System Testing Strategy](docs/23_frontend_and_system_testing_strategy.md)

## High-Level Architecture

```text
                         Web / Mobile Clients
                                  |
                                  v
                         Django / GraphQL API
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
      PostgreSQL                Redis                 AI Module
          |                       |                       |
          |                 Celery / WebSockets       +--+--+
          |                                             |  |
          |                                          LLM Qdrant
          |                                             |
          +-------------------+-------------------------+
                              |
                       Object Storage
```

The detailed architecture, boundaries, reliability rules, security decisions, testing strategy, and deployment plan are documented in `docs/`.

## Development Philosophy

- Keep the architecture modular without over-engineering.
- Prefer simple solutions that solve real requirements.
- Keep business logic out of HTTP/API layers.
- Keep module boundaries clear.
- Treat PostgreSQL as the source of truth.
- Use background processing only when work actually benefits from it.
- Use real-time communication only where it provides value.
- Make failures observable and client errors clear and safe.
- Test each layer at the appropriate level.
- Keep deployment reproducible with Docker.
