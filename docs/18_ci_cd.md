# 18 — CI/CD

## Decision
Use **GitHub Actions** for CI/CD. Keep Continuous Integration and Continuous Delivery/Deployment as separate responsibilities.

## CI

CI answers: **Is this code safe to merge?**

Pull requests should run automated checks including:

- Ruff linting and formatting checks
- mypy type checking
- pytest unit and integration/API tests
- pytest-cov coverage
- Bandit security checks
- pip-audit dependency vulnerability checks
- Docker production-image build
- Trivy container-image vulnerability scan
- Playwright critical E2E tests after the main backend checks pass

Independent checks should run in parallel where practical to keep CI fast.

## CI test infrastructure

- Use a clean PostgreSQL test database for integration tests.
- Use Redis only for tests that actually require it.
- Start Celery workers only for dedicated Celery integration tests.
- Start Qdrant only for vector-database integration tests.
- Never call real external AI providers during normal PR CI.
- Mock/fake external AI providers for deterministic tests.
- Real provider tests, if needed, are separate and require protected secrets.

## CI Docker checks

The production Docker image must successfully build before merging/deployment.

Use:

- Multi-stage Docker builds
- Python slim for build/development stages
- Distroless production image where practical
- Non-root production containers
- No secrets baked into images

Trivy scans the resulting image. Critical vulnerabilities should block the pipeline according to the project's configured policy.

## Branch protection

The `main` branch should require:

- Pull requests
- Passing required CI checks
- No direct pushes

The exact review requirement can remain appropriate for a solo project.

## CD

CD answers: **How do we deliver verified code?**

Initial flow:

```text
Merge → main
    ↓
CI passes
    ↓
Build production image
    ↓
Trivy scan
    ↓
Push image → GHCR
    ↓
Manual production approval
    ↓
Deploy
    ↓
Run Django migrations
    ↓
Health checks
    ↓
Live
```

## Container registry

Use **GitHub Container Registry (GHCR)**.

Build the image once in CI and deploy that exact image. Do not rebuild the application independently on the production machine.

## Image versioning

Tag images with the Git commit SHA so the exact source version running in production is identifiable.

Optional semantic release tags such as `v1.2.0` may also be used later.

## Deployment

Use the Docker-based deployment strategy defined in `17_deployment_infrastructure.md`.

Initial production deployment should be simple and manually controlled rather than fully automatic.

## Database migrations

Deployments run Django migrations in a controlled step.

Production migrations should be designed to be backward-compatible when necessary so application rollback remains practical.

## Health verification

After deployment, verify:

- Application liveness
- Application readiness
- Critical dependency readiness

A failed health check means the deployment is unsuccessful.

## Rollback

Production images are immutable/versioned so a previous known-good image can be redeployed.

Database migrations require additional care because application rollback and schema rollback are not always symmetric.

## Secrets

Never store secrets in Git.

Use:

- `.env` locally
- GitHub Actions Secrets for CI/CD secrets
- Production environment/secret configuration for deployment

Only provide secrets to workflows that actually need them.

## Dependency updates

Use **Dependabot** for dependency update/security PRs. All dependency updates must pass normal CI before merging.

## Initial CI workflow structure

Keep workflows understandable rather than creating a large monolithic YAML file. Separate concerns where useful, for example:

- Pull-request quality/tests
- Security checks
- Docker build/image scan
- E2E tests
- Production deployment

The exact number of workflow files will be decided during implementation based on complexity.

## CI/CD principles

1. Fast checks should run early.
2. Independent checks should run in parallel when practical.
3. Never merge known failing CI.
4. Never deploy an image that has not passed CI.
5. Build once and deploy the exact tested image.
6. Keep production deployment manually controlled initially.
7. Keep secrets out of source control and images.
8. Make deployments observable and health-checked.
9. Keep rollback simple.
10. Avoid unnecessary CI/CD infrastructure.
