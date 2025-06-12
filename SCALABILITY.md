# SCALABILITY.md

## 🔢 Scenario 1: Logging under High Traffic

### Problem:

If we log every request (including IP, timestamp, headers, body) during a high-traffic campaign (e.g. thousands of
requests per second), our app will slow down due to:

- Synchronous I/O to disk (log file or DB)
- Blocking request lifecycle

### Solutions:

- ✅ **Use background tasks** to push logs asynchronously.
- ✅ **Send logs to an external system** via queue (e.g. Redis, Kafka, RabbitMQ).
- ✅ **Batch logs** before writing them.
- ✅ **Use observability tools**: integrate with Elastic Stack, Grafana, Sentry, etc.

### Ideal Practice:

- Log only metadata in real-time.
- Store full logs asynchronously.

---

## 🏢 Scenario 2: Multi-instance Deployment

### Problem:

If we deploy the system on multiple instances (horizontal scaling), we need to avoid stateful dependencies.

### What should be externalized?

- ✅ Database must be centralized/shared
- ✅ Logging service should be external
- ✅ Rate limiter and cache (e.g. Redis) should be shared

### Risks:

- In-memory counters (like visit count) won't work — must use a shared DB
- Race conditions in short_code generation — handle uniqueness in DB or pre-generate pool

### Tools:

- Load balancer (e.g. Nginx) with sticky sessions (if needed)
- Use PostgreSQL + Redis cluster
- Kubernetes or Docker Swarm for scaling

---

## 📊 Scenario 3: Traffic Surge (e.g. Campaign)

### Problems:

- DB saturation
- Log overload
- Long response times

### Mitigations:

- ✅ Use **connection pooling** for DB (SQLAlchemy default pool or asyncpg pool)
- ✅ Use **async DB access** via `encode/databases` or `asyncpg` (for high concurrency)
- ✅ **Implement caching**: store frequently accessed redirects in Redis or memory cache
- ✅ Add **rate limiting** to avoid abuse
- ✅ Offload analytics/logging to **background queues** (Celery, RQ, Dramatiq)

---

## 📌 Additional Enhancements (Applied in Codebase)

- ✅ Added short_code collision detection and retry loop
- ✅ Allowed custom short_code via POST `/shorten?custom_code=...`
- ✅ Supported expiration datetime (`expires_at`) for temporary URLs
- ✅ Extended error handling in DB session to log SQLAlchemy exceptions
- ✅ Improved API documentation with metadata in FastAPI app

---

## Summary of Recommendations:

- [x] Use FastAPI + SQLModel + PostgreSQL
- [x] Use Alembic for migrations
- [x] Use middleware for logging (async-friendly)
- [x] Pool DB connections
- [x] Redis for cache and rate limiting
- [x] Kafka/RabbitMQ for async logging
- [x] Deploy via Docker/K8s

---

## Optional Enhancements:

- TTL/expiration for short URLs ✅
- Admin dashboard to monitor top links
- Custom short code option ✅
- Dockerfile + CI/CD pipeline ✅
