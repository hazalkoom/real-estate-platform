# 17 — Deployment & Infrastructure

## Decision
The project must remain **100% free and require no credit/debit card**.

We will prioritize a complete local Docker environment and use only free/no-card services for any public deployment. Paid infrastructure is explicitly out of scope unless this requirement changes later.

## 1. Containerization

### Docker
- Docker is the standard way we package and run the application.
- Development and integration environments use containers.
- Containers are disposable; persistent data belongs in volumes or external storage.

### Docker Compose
Use Docker Compose for the complete local stack:

```text
Django / ASGI
Celery Worker
PostgreSQL
Redis
Qdrant
```

Celery Beat is added only when scheduled jobs are actually needed.

### Docker images
- Multi-stage builds.
- Python slim images for development/build stages.
- Production image should be minimal and non-root.
- Distroless production image is the target after the normal image is working and easy to debug.
- No secrets inside images.
- No development dependencies in the production image.

### Image security
- Use controlled/pinned base image versions.
- Scan production images with **Trivy**.
- Keep containers on private Docker networks where possible.

## 2. Local architecture

```text
Docker Compose
│
├── Django / ASGI
├── Celery Worker
├── PostgreSQL
├── Redis
└── Qdrant
```

Persistent development data:
- PostgreSQL → Docker volume
- Other stateful services → volumes only when persistence is required

Only services that need host access are exposed to the host. PostgreSQL, Redis and Qdrant are not publicly exposed.

## 3. Production/public deployment constraint

Because no payment card is available, we will **not depend on a paid VPS or cloud account**.

A complete production-like stack will remain runnable locally with Docker Compose.

For a public demo, use a genuinely free/no-card platform where its current limits fit the application. **Render Free** is the initial candidate because it currently supports free Python web services, static sites and a free Postgres option without requiring payment information. Its free web services sleep after inactivity, and its free Postgres database expires after 30 days, so it is suitable for a demo/preview rather than permanent production. citeturn0search1turn0search14

Do not design the application around temporary free-tier limitations. The Docker deployment remains the canonical environment.

## 4. Public demo architecture

Start with the smallest viable public deployment:

```text
GitHub
  ↓
Free hosting
  ↓
Django / API
  ↓
Free database/service where available
```

If a required dependency (Redis, Celery worker, Qdrant, persistent object storage, etc.) cannot be hosted free/no-card on the selected platform, keep that component local rather than introducing a paid dependency.

AI features must degrade gracefully when an external AI provider is unavailable.

## 5. Container registry

Use **GitHub Container Registry (GHCR)** for public project images where useful.

- GitHub Actions builds the image.
- Trivy scans it.
- The image can be published to GHCR.
- Keep images public when appropriate so registry costs are not introduced.

GitHub currently provides free use of standard GitHub-hosted Actions runners for public repositories, and GitHub Container Registry currently has free container-image storage/bandwidth policy. citeturn0search3turn0search4

## 6. Reverse proxy / HTTPS

Use **Caddy** for a self-hosted deployment because it provides simple HTTPS configuration.

However, a self-hosted VPS is not part of the free/no-card requirement. Caddy is therefore primarily part of the architecture and local/self-hosted deployment path, not a reason to purchase infrastructure.

## 7. Application server

Production-style Django execution:

```text
Caddy
  ↓
ASGI
  ↓
Gunicorn + Uvicorn worker
```

GraphQL and WebSockets are served through the ASGI application.

Celery remains a separate worker process/container.

## 8. PostgreSQL

### Development
- PostgreSQL in Docker.
- Persistent Docker volume.

### Public demo
- Use a free PostgreSQL option only when its current limits are acceptable.
- Do not rely on temporary free databases for important data.

### Production
- Managed PostgreSQL would be preferred eventually, but it is **not part of the current zero-cost/no-card deployment**.

## 9. Redis

Redis is used for:
- Cache
- Celery broker
- Real-time/WebSocket infrastructure

### Development
- Redis in Docker.

### Public deployment
- Use a genuinely free/no-card Redis option only if available and suitable.
- Otherwise keep the full Redis-dependent stack local.

## 10. Vector database

Use **Qdrant**.

### Development
- Qdrant in Docker.

### Public deployment
- Prefer self-hosted/free availability only if it can be done without payment information.
- Otherwise AI semantic search remains a local/full-stack capability rather than introducing a paid dependency.

## 11. Object/file storage

Property media is image-only.

For the full development environment:
- Store images using local Docker-mounted storage.

For public hosting:
- Use a free/no-card object-storage option only if its current terms satisfy the requirement.
- Do not assume an S3-compatible service is free or card-free.
- Never make PostgreSQL store image binaries.

## 12. Backups

For local development:
- Database can be recreated from migrations/seed data.

For any public environment containing data worth keeping:
- Export PostgreSQL backups regularly.
- Store backups separately from the running database.
- Test restoration.

No paid backup service is required for the project.

## 13. Environment configuration

Development:
- `.env` locally.
- `.env.example` committed with variable names but no secrets.

Production/public hosting:
- Platform environment variables/secrets.
- Never commit secrets.

## 14. CI/CD

### CI — GitHub Actions

For the public GitHub repository:

```text
Push / Pull Request
        ↓
Ruff
        ↓
mypy
        ↓
pytest
        ↓
Coverage
        ↓
Bandit
        ↓
pip-audit
        ↓
Docker build
        ↓
Trivy
```

### CD

Keep CD separate from CI.

For a free public demo, deployment can be triggered by the free hosting provider from GitHub after CI passes.

Do not introduce paid deployment infrastructure just to automate CD.

## 15. Scaling

No Kubernetes.

Start with one application instance and one Celery worker where the chosen free environment supports them.

If the project later gains real traffic and funding, the architecture can scale horizontally:

```text
Django × N
Celery × N
```

behind a reverse proxy/load balancer.

Managed PostgreSQL/Redis/object storage can be introduced later without changing the application architecture significantly.

## 16. Cost rule

The project should never require a credit card to run its development environment.

The complete system must always be reproducible with:

```bash
docker compose up
```

A public demo is optional and must use free/no-card infrastructure. If a provider's free tier changes or requires payment, replace it rather than making payment a project requirement.

## Final technology decisions

| Area | Choice |
|---|---|
| Containers | Docker |
| Local orchestration | Docker Compose |
| Build | Multi-stage Dockerfiles |
| Development base | Python slim |
| Production target | Minimal/non-root, eventually distroless |
| Image scanning | Trivy |
| Registry | GitHub Container Registry |
| Reverse proxy | Caddy |
| Application server | Gunicorn + Uvicorn/ASGI |
| Database | PostgreSQL |
| Cache/broker/realtime support | Redis |
| Vector DB | Qdrant |
| Media | Images only; local storage initially |
| CI | GitHub Actions |
| CD | Separate from CI; free hosting deployment where available |
| Kubernetes | **Not used** |
| Paid VPS/cloud | **Not required** |
| Credit card | **Not required** |
