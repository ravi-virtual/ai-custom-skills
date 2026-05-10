# OBSERVABILITY.md — Observability Strategy

## Overview
Observability is the ability to understand the internal state of a system from its external outputs. This file covers the full observability stack: **logs + metrics + traces + alerts**.

> Related: `MONITORING.md` covers monitoring tools and dashboards. This file covers the engineering strategy — what to instrument and how.

---

## Observability Pillars

### Pillar 1: Logs (What happened)
The narrative record of events. Every meaningful system action should produce a log entry.

#### Log Level Strategy
```
ERROR  → System failures, unhandled exceptions, data corruption risk
WARN   → Recoverable issues, slow queries, failed retries, suspicious activity
INFO   → Key lifecycle events (request in/out, auth events, job start/end)
DEBUG  → Detailed state (NEVER in production — prefix all with // [DEBUG])
```

#### Structured Log Format
```javascript
// All production logs should be structured JSON
const logEntry = {
  timestamp: new Date().toISOString(),
  level: 'info',              // error | warn | info
  requestId: req.id,          // Unique per request (attach via middleware)
  userId: req.user?.id,       // Null for unauthenticated requests
  method: req.method,
  path: req.path,
  statusCode: res.statusCode,
  durationMs: Date.now() - req.startTime,
  message: 'User login successful',
  // Add domain-specific fields as needed:
  profileId: profile?._id,
};
```

#### What Must Always Be Logged
```
✅ Every authentication event (login, logout, token refresh, failed login)
✅ Every request start/end (method, path, status, duration)
✅ Every error with full stack trace
✅ Every external API call (AI service, email, SMS) — start + result + duration
✅ Every database operation that fails
✅ Application startup and shutdown events
✅ Every slow operation (> threshold from PERFORMANCE.md)
```

#### What Must Never Be Logged
```
❌ Passwords (plaintext or hashed)
❌ JWT tokens (access or refresh)
❌ API keys or secrets
❌ Sensitive personal data (SSN, payment info)
❌ Full request body on auth endpoints (may contain passwords)
❌ Internal stack traces in responses (only in server logs)
```

---

### Pillar 2: Metrics (How the system is performing)

#### Key Metrics to Track

| Metric | Type | Collection Point |
|---|---|---|
| `http.request.duration` | Histogram | Request middleware |
| `http.request.count` | Counter | Request middleware |
| `http.error.count` | Counter | Error handler |
| `db.query.duration` | Histogram | Mongoose plugin |
| `db.query.count` | Counter | Mongoose plugin |
| `auth.login.success` | Counter | Auth controller |
| `auth.login.failure` | Counter | Auth controller |
| `auth.token.refresh` | Counter | Auth controller |
| `ai.generation.duration` | Histogram | AI service |
| `ai.generation.failure` | Counter | AI service |
| `process.memory.heapUsed` | Gauge | Every 30s |
| `process.cpu.usage` | Gauge | Every 30s |

#### Metric Instrumentation Pattern (Express)
```javascript
// middleware/metrics.js
const requestDurationHistogram = {};  // Use your metrics client (prom-client, etc.)

const metricsMiddleware = (req, res, next) => {
  const start = process.hrtime.bigint();
  
  res.on('finish', () => {
    const durationMs = Number(process.hrtime.bigint() - start) / 1_000_000;
    
    // Record duration
    // requestDurationHistogram.observe({ method: req.method, path: req.route?.path, status: res.statusCode }, durationMs);
    
    // Log slow requests
    if (durationMs > 500) {
      console.warn(JSON.stringify({
        level: 'warn',
        message: 'Slow request',
        method: req.method,
        path: req.path,
        durationMs,
      }));
    }
  });
  
  next();
};
```

---

### Pillar 3: Traces (Where time was spent)

For the current stack, distributed tracing is not required. Instead, use **request ID correlation** to trace a single request through multiple log entries.

#### Request ID Pattern
```javascript
// middleware/requestId.js
const { v4: uuidv4 } = require('uuid');

const attachRequestId = (req, res, next) => {
  req.id = req.headers['x-request-id'] || uuidv4();
  req.startTime = Date.now();
  res.setHeader('X-Request-Id', req.id);  // Return in response for frontend correlation
  next();
};

// Register FIRST in app.js — before all other middleware
app.use(attachRequestId);
```

#### Correlating Logs for One Request
When debugging a specific request, filter logs by `requestId` to see the full lifecycle:
```bash
# Find all logs for a specific request
grep "a1b2c3d4-..." production.log | jq .
```

---

## Alert Thresholds

| Alert | Threshold | Severity | Response |
|---|---|---|---|
| 5xx rate | > 0.5% of requests in 5 min | Critical | Investigate immediately |
| 4xx rate | > 10% of requests in 5 min | Warning | Check for bad client or bug |
| Response time p95 | > 2s for 5 min | Warning | Profile the slow endpoint |
| Auth failure rate | > 20/min from same IP | Warning | Check for brute force |
| Memory | > 85% heap used | Warning | Check for memory leak |
| DB query time | > 1s average over 5 min | Warning | Check for missing index |
| AI service failure | > 2 consecutive failures | Warning | Check fallback chain |
| Health check failure | Any failure | Critical | Deploy rollback immediately |

---

## Observability Implementation Checklist

For every new feature/endpoint:
- [ ] Request logged at entry and exit (method, path, status, duration)
- [ ] Auth events produce INFO log (success) or WARN log (failure)
- [ ] Errors produce ERROR log with full context (no sensitive data)
- [ ] External service calls (AI, email) logged with duration and result
- [ ] Request ID propagated through all log entries
- [ ] Slow operation threshold logging in place (> 500ms)
- [ ] No sensitive data in any log entry

---

## Local Observability Setup

```javascript
// app.js — observability middleware stack (in order)
app.use(attachRequestId);          // 1. Attach request ID
app.use(metricsMiddleware);        // 2. Collect metrics
app.use(morgan(logFormat));        // 3. HTTP request logging

// ... routes ...

app.use(errorHandler);             // Last: catch and log all errors
```

---

## Production Observability Stack (Recommended)

| Layer | Tool | Purpose | Free Tier |
|---|---|---|---|
| Logs | Better Stack / LogTail | Log aggregation + search | ✅ |
| Errors | Sentry | Error tracking + stack traces | ✅ |
| Uptime | UptimeRobot | External HTTP monitoring | ✅ |
| DB | MongoDB Atlas | Query performance + slow ops | ✅ |
| Server | Render / Railway | CPU, memory, request metrics | ✅ |
