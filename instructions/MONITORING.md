# MONITORING.md — Observability & Monitoring Reference

## Overview
Observability is the ability to understand what your system is doing from its outputs. This file defines the monitoring strategy, alerting rules, and operational playbooks.

---

## The Three Pillars of Observability

### 1. Logs (What happened)
### 2. Metrics (How the system is performing)
### 3. Traces (Where time was spent)

---

## Section 1: Logging Strategy

### Log Levels
```
ERROR  → System failures, exceptions, security events (always log)
WARN   → Recoverable issues, degraded performance, unexpected state
INFO   → Request lifecycle, business events, startup/shutdown
DEBUG  → Detailed tracing (NEVER in production, always prefixed // [DEBUG])
```

### Structured Log Format
```javascript
// Use structured JSON logging in production
const log = {
  level: 'info',
  timestamp: new Date().toISOString(),
  requestId: req.id,         // Attach request ID to all logs in a request
  method: req.method,
  path: req.path,
  statusCode: res.statusCode,
  userId: req.user?.id,      // For authenticated requests
  duration: Date.now() - start,
  message: 'Request completed',
};
```

### What to Log
```javascript
// ✅ Log these
INFO:  Request start/end with method, path, status, duration
INFO:  Authentication events (login, logout, token refresh, failed login)
WARN:  Slow requests (> 500ms)
WARN:  Failed authentication attempts (for anomaly detection)
ERROR: All uncaught exceptions with stack trace
ERROR: Database connection failures
ERROR: Third-party service failures (AI API, email, etc.)

// ❌ Never log these
Passwords (plaintext or hashed)
JWT tokens (access or refresh)
Any sensitive personal data (SSN, credit cards)
API keys or secrets
```

### Morgan Request Logging
```javascript
// Development: colored output
app.use(morgan('dev'));

// Production: structured JSON
app.use(morgan('combined'));
// Or custom JSON format:
app.use(morgan((tokens, req, res) => JSON.stringify({
  method: tokens.method(req, res),
  url: tokens.url(req, res),
  status: parseInt(tokens.status(req, res)),
  responseTime: parseFloat(tokens['response-time'](req, res)),
  timestamp: new Date().toISOString(),
})));
```

---

## Section 2: Metrics

### Key Metrics to Track

| Metric | Type | Alert Threshold |
|---|---|---|
| API response time (p95) | Histogram | > 1s for CRUD, > 20s for AI |
| Error rate | Counter | > 1% of requests |
| 4xx rate | Counter | > 5% (may indicate abuse) |
| 5xx rate | Counter | > 0.1% (server issues) |
| Auth failure rate | Counter | > 10/min from same IP |
| Database query time | Histogram | > 500ms |
| Memory usage | Gauge | > 80% of limit |
| CPU usage | Gauge | > 80% sustained |

### Slow Request Detection
```javascript
// Middleware to detect slow requests
const slowRequestDetector = (req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (duration > 500) {
      console.warn(JSON.stringify({
        level: 'warn',
        message: 'Slow request detected',
        method: req.method,
        path: req.path,
        duration,
        userId: req.user?.id,
      }));
    }
  });
  next();
};
app.use(slowRequestDetector);
```

---

## Section 3: Health Check Endpoint

```javascript
// Always implement a health check endpoint
router.get('/health', async (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    checks: {}
  };

  try {
    // Check DB connection
    await mongoose.connection.db.admin().ping();
    health.checks.database = { status: 'healthy' };
  } catch (err) {
    health.status = 'degraded';
    health.checks.database = { status: 'unhealthy', error: err.message };
  }

  const statusCode = health.status === 'healthy' ? 200 : 503;
  return res.status(statusCode).json(health);
});
```

---

## Section 4: Error Tracking

### Error Classification for Monitoring

| Error Type | Handling | Alerting |
|---|---|---|
| Validation errors (422) | Expected, log INFO | No alert |
| Auth failures (401/403) | Expected, log WARN | Alert if > 10/min from same IP |
| Not found (404) | Expected, log INFO | No alert |
| Server errors (500) | Unexpected, log ERROR | Immediate alert |
| Database errors | Critical, log ERROR | Immediate alert |
| External service failures | Degraded, log WARN | Alert if sustained |

### Error Context Logging
```javascript
// Always log enough context to reproduce the error
const errorContext = {
  level: 'error',
  message: err.message,
  stack: err.stack,
  requestId: req.id,
  method: req.method,
  path: req.path,
  userId: req.user?.id,
  body: sanitizeBody(req.body), // Remove sensitive fields
  params: req.params,
  query: req.query,
};
```

---

## Section 5: Alerting Runbook

### Alert: High 5xx Rate
```
Trigger: > 1% of requests return 5xx in 5 minutes
Action:
  1. Check server logs for the error pattern
  2. Check database connectivity
  3. Check third-party service status
  4. If DB issue: restart DB connection, verify connection string
  5. If code bug: identify the endpoint, apply hotfix
  6. If unable to resolve in 30 min: rollback to last known good version
```

### Alert: Database Connection Failure
```
Trigger: Health check fails database ping
Action:
  1. Check MongoDB Atlas status (if cloud)
  2. Verify MONGO_URI is correct in environment
  3. Check network connectivity from server to DB
  4. Check IP whitelist in Atlas (if using Atlas)
  5. Restart application server
  6. If Atlas: check for maintenance windows
```

### Alert: Auth Failure Spike
```
Trigger: > 10 auth failures per minute from same IP
Action:
  1. Check IP — is it a known scraper or bad actor?
  2. If confirmed malicious: add IP to block list
  3. Check if rate limiting is correctly configured
  4. Review recent user complaints about login issues
  5. Verify JWT secret hasn't changed (would invalidate all tokens)
```

---

## Section 6: Monitoring Tools (Recommended)

| Tool | Purpose | Free Tier? |
|---|---|---|
| MongoDB Atlas Monitoring | DB performance, slow queries | ✅ Yes |
| Render.com Metrics | Server CPU, memory, requests | ✅ Yes |
| UptimeRobot | External uptime monitoring | ✅ Yes (50 monitors) |
| Sentry | Error tracking with stack traces | ✅ Yes (5k errors/month) |
| LogTail / Better Stack | Log aggregation | ✅ Yes |

---

## Section 7: Performance Baseline

After every deployment, establish baselines:
```bash
# Test with 100 requests, 10 concurrent
artillery quick --count 100 --num 10 http://localhost:5000/api/health

# Test the most critical endpoint
artillery quick --count 50 --num 5 \
  -H "Authorization: Bearer <test-token>" \
  http://localhost:5000/api/users/me

# Record results in PERFORMANCE.md
```
