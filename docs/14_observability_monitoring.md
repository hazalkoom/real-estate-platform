# 14 — Observability & Monitoring

## Decision
Use a small but real observability stack:

- **Structured logging:** Python `logging` + `structlog`
- **Error tracking:** Sentry Developer/free plan
- **Metrics:** Prometheus
- **Dashboards:** Grafana
- **Tracing:** OpenTelemetry
- **Health checks:** Django endpoints
- **Alerts:** Prometheus/Grafana

Keep the implementation intentionally small and expand only when the system needs it.

---

## 1. Logging

### Tools
- Python `logging`
- `structlog`

### Rules
- Use structured logs rather than arbitrary text.
- Include useful context such as:
  - timestamp
  - log level
  - module
  - operation
  - request/trace ID where available
  - user ID where appropriate
  - duration
  - error code/type
- Log important application and infrastructure events, not every line of code.
- Never log passwords, access tokens, API keys, or other sensitive secrets.
- Development logs should remain easy to read; production logs should be structured.

---

## 2. Error Tracking

### Tool
**Sentry — free Developer plan initially.**

The free plan is sufficient for this solo project; current Sentry documentation confirms the Developer plan remains free. Usage quotas will be respected rather than adding paid usage automatically. citeturn0search0turn0search13

### Responsibilities
- Capture unhandled application exceptions.
- Group repeated errors.
- Preserve stack traces and useful request context.
- Track error frequency and affected operations.
- Use Sentry for application error investigation; use normal logs for general application events.

Do not build or self-host a separate error-tracking system.

---

## 3. Metrics

### Tools
- **Prometheus** for collecting/storing metrics.
- **Grafana** for dashboards and visualization.

### Keep the first version small.
Track only useful metrics such as:

- request count/rate
- request error rate
- request latency
- 95th percentile latency
- PostgreSQL latency/errors
- Celery queue length
- Celery failed jobs
- Redis availability/health
- AI request count, latency, and failures
- vector DB request latency/failures

Avoid creating a large dashboard full of meaningless metrics.

---

## 4. Health Checks

Provide more than one simple health endpoint so different checks have clear purposes.

### `/health/live`

Checks that the Django application process is alive.

Should not depend on external services.

### `/health/ready`

Checks whether the application is ready to serve normal traffic.

Check important dependencies such as:

- PostgreSQL
- Redis

Potentially include other critical dependencies if they become required for the deployment.

### `/health/dependencies`

A development/operations-oriented endpoint showing dependency status individually, for example:

```text
postgres:   ok
redis:      ok
vector_db:  ok
```

Do not expose sensitive connection details.

These endpoints remain intentionally simple; they are not a replacement for full monitoring.

---

## 5. Distributed Tracing

### Tool
**OpenTelemetry.**

Use OpenTelemetry for traces and instrumentation. It is vendor-neutral and supports traces, metrics, and logs, while leaving storage/visualization to other systems. citeturn0search1turn0search3

### Initial tracing targets
Trace useful workflows such as:

```text
GraphQL request
    ↓
Resolver
    ↓
Service
    ↓
Repository
    ↓
PostgreSQL
```

and more interesting workflows:

```text
GraphQL
  ↓
AI service
  ↓
Celery
  ↓
AI provider
  ↓
Vector DB
```

Use spans to identify where time is spent and where failures occur. OpenTelemetry traces are composed of spans representing individual operations. citeturn0search2

### Important rule
Do not instrument every tiny function manually. Start with meaningful boundaries and external calls.

---

## 6. OpenTelemetry + Metrics/Logs

OpenTelemetry is an instrumentation/telemetry framework, not the main visualization backend. We will continue using Prometheus and Grafana for our metrics dashboards. citeturn0search3

Initially:

```text
Django / Celery
      │
      ├── structured logs → logging system/stdout
      ├── metrics → Prometheus → Grafana
      └── traces → OpenTelemetry → chosen trace backend
```

The exact trace backend/export destination can be finalized during deployment once the hosting setup is chosen.

---

## 7. Alerts

Use Prometheus/Grafana alerts for meaningful operational problems.

Initial alerts:

- high API error rate
- unusually high API latency
- PostgreSQL unavailable
- Redis unavailable
- Celery queue continuously growing
- repeated Celery failures
- AI provider repeatedly failing
- vector DB repeatedly failing
- storage/disk approaching capacity

Avoid alerts for isolated, harmless failures that create noise.

---

## 8. Observability Boundaries

### Logs
Answer:
> What happened?

### Sentry
Answer:
> What application error broke, and where?

### Metrics
Answer:
> How healthy is the system over time?

### Traces
Answer:
> Where did this particular request/job spend its time?

### Health checks
Answer:
> Is the application/dependency currently available?

---

## 9. Privacy & Security

Never expose or record:

- passwords
- access/refresh tokens
- API keys
- database credentials
- private file URLs when they contain secrets
- unnecessary sensitive user information

Sanitize exception context and request data before sending telemetry externally.

---

## 10. Development vs Production

### Development
Use:

- readable structured logs
- local Prometheus
- local Grafana
- local OpenTelemetry components as needed
- Sentry only when testing production-like error tracking

### Production
Use:

- structured logs
- Sentry
- Prometheus
- Grafana
- OpenTelemetry
- alerts
- health checks

Do not create a large observability deployment before the application itself needs it.

---

## 11. Final Observability Stack

```text
                    Application
                 /      |       \
                /       |        \
             Logs     Metrics    Errors
              ↓          ↓          ↓
          structlog  Prometheus   Sentry
                         ↓
                      Grafana

Application / Celery / AI workflows
                ↓
          OpenTelemetry
                ↓
             Traces
```

### Final decisions

| Area | Choice |
|---|---|
| Logging | Python `logging` |
| Structured logging | `structlog` |
| Error tracking | Sentry free Developer plan |
| Metrics | Prometheus |
| Dashboards | Grafana |
| Tracing | OpenTelemetry |
| Health checks | `/health/live`, `/health/ready`, `/health/dependencies` |
| Alerts | Prometheus/Grafana |
| Sensitive telemetry | Never log secrets |

The stack is intentionally small, but uses real production-oriented observability technologies and gives us practical experience with logs, metrics, errors, tracing, health checks, and alerts.
