# RECOVERY.md — Disaster Recovery & Incident Response

## Purpose
Defines the procedures for recovering from failures, outages, data loss, and security incidents. Every recovery action must be documented after execution.

---

## Incident Severity Levels

| Level | Name | Definition | Response Time |
|---|---|---|---|
| P0 | Critical | Complete service outage, data corruption, security breach | Immediate (< 5 min) |
| P1 | High | Partial service failure, auth broken, AI generation down | < 15 min |
| P2 | Medium | Single feature broken, degraded performance | < 1 hour |
| P3 | Low | Minor bug, cosmetic issue, non-critical feature broken | < 24 hours |

---

## P0: Complete Service Outage

### Immediate Steps (First 5 Minutes)
```
1. Check server status: pm2 list
2. Check error logs: pm2 logs app-backend --lines 100
3. Check DB connectivity: mongosh --eval "db.adminCommand('ping')"
4. Attempt restart: pm2 restart app-backend
5. Verify health: curl https://api.yourdomain.com/api/health
```

### If Restart Doesn't Fix It
```
6. Check disk space: df -h (full disk = silent failures)
7. Check memory: free -h (OOM kills node process)
8. Check network: ping google.com (network outage?)
9. Check for recent deployments: git log --oneline -5
10. If recent deployment caused it → ROLLBACK immediately
```

### Rollback Procedure
```bash
# Step 1: Identify last working commit
git log --oneline -10

# Step 2: Create revert commit (don't force push)
git revert HEAD --no-edit
git push origin main

# Step 3: Redeploy the reverted version
[platform-specific deploy command]

# Step 4: Verify health check passes
curl https://api.yourdomain.com/api/health

# Step 5: Document in FAILURES.md and SESSION.md
```

---

## P0: Data Corruption

### Immediate Steps
```
1. Stop ALL write operations to the affected collection immediately
2. Take a snapshot/backup of the current (corrupted) state — preserve evidence
3. Identify the scope: which documents, which fields, time range
4. Identify the cause: bad migration? Bug in update logic? Manual command?
5. DO NOT run any repair scripts until the cause is fully understood
```

### Recovery from Backup
```bash
# Restore to a MongoDB Atlas Point-in-Time snapshot
# (Atlas free tier: 2-day retention)
# Atlas Dashboard → Cluster → ... → Point in Time Recovery

# For local backup:
mongorestore --uri "mongodb://localhost:27017/appname" \
  --drop ./backups/last-known-good/
```

### After Restoration
- Audit all data written between the corruption event and restoration
- Notify affected users if their data was lost/modified
- Document root cause in FAILURES.md
- Add the triggering bug to CHECKLIST.md as a permanent check

---

## P0: Security Breach

### Immediate Response
```
1. STOP: Do not attempt to "fix" without assessing scope first
2. Identify: What was accessed? What was leaked? (tokens, data, credentials)
3. Contain: If tokens/secrets were compromised, rotate ALL credentials NOW:
   - JWT_SECRET → new 64-char random string
   - JWT_REFRESH_SECRET → new 64-char random string
   - Any exposed API keys (AI services, email, etc.)
4. Invalidate: All existing JWT tokens are immediately invalid after secret rotation
5. Revoke: Revoke any exposed OAuth tokens or service credentials
6. Audit: Check all recent auth logs for unauthorized access patterns
```

### Credential Rotation
```bash
# Generate new secrets
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
# Run twice — one for JWT_SECRET, one for JWT_REFRESH_SECRET

# Update in your deployment platform environment variables
# Restart the backend server
# All users will be logged out — this is expected and correct
```

### Post-Breach
- Document: what was accessed, by whom, for how long
- Assess: does GDPR/CCPA require user notification?
- Patch: fix the vulnerability that allowed the breach
- Harden: review SECURITY.md — what check was missed?

---

## P1: Authentication Broken

**Symptom**: Users cannot log in, tokens not accepted, 401 on all requests

```
1. Verify JWT_SECRET hasn't changed unexpectedly
   → If changed: all tokens invalid — users must log in again
2. Check hasToken middleware is loaded (common after bad deploy)
   → node -e "require('./src/middlewares/hasToken')" — should not error
3. Check isAuthenticated middleware query works
   → Verify DB is reachable and User collection exists
4. Check token format: Authorization: Bearer <token>
   → Ensure frontend is still sending the header correctly
5. Check token expiry settings in constants.js
   → JWT_EXPIRES_IN=15m format is correct
```

---

## P1: Database Connection Lost

**Symptom**: All API calls fail with 500, logs show "MongoNetworkError"

```
1. Verify MONGO_URI is correct in environment
2. Test connection directly:
   mongosh "your-mongo-uri-here" --eval "db.adminCommand('ping')"
3. Check MongoDB Atlas status: status.mongodb.com
4. Check IP whitelist (Atlas): is server IP still whitelisted?
5. Check if MongoDB process is running (local): mongod --version
6. Restart MongoDB if local:
   sudo systemctl restart mongod
7. Restart application after DB is confirmed reachable:
   pm2 restart app-backend
```

---

## P2: AI Generation Service Down

**Symptom**: AI generation endpoints returning 500, timeout errors

```
1. Check primary model (Gemini): verify API key is valid
2. Check secondary model (Grok): verify API key is valid
3. Check tertiary model (OpenAI): verify API key is valid
4. Check AI provider status pages:
   - Google AI: status.cloud.google.com
   - xAI Grok: [check their status page]
   - OpenAI: status.openai.com
5. If all three are down: return user-friendly degraded service message
   → "AI generation is temporarily unavailable. Please try again later."
6. Do NOT fail silently — always inform the user
```

---

## Recovery Documentation Requirements

After any P0 or P1 incident, MANDATORY documentation:

```markdown
## Incident [DATE]: [Short Title]
**Severity**: P0 | P1
**Duration**: [Start time → End time]
**Impact**: [Who was affected, what they couldn't do]

**Timeline**:
- HH:MM: [First sign of problem]
- HH:MM: [Discovered / alerted]
- HH:MM: [Investigation started]
- HH:MM: [Root cause identified]
- HH:MM: [Fix applied]
- HH:MM: [Service restored]
- HH:MM: [Verified stable]

**Root Cause**: [Technical root cause — be specific]

**Fix Applied**: [What exactly was changed]

**Prevention**: [What will prevent this from recurring]

**Action Items**:
- [ ] [Specific task to prevent recurrence]
- [ ] [Update to CHECKLIST.md or FAILURES.md]
```

Add this to `FAILURES.md` after every incident.

---

## Backup Strategy

### What to Back Up
| Data | Frequency | Retention | Method |
|---|---|---|---|
| MongoDB database | Daily | 7 days | Atlas automated backup |
| Environment variables | On change | Indefinitely | Secure password manager |
| Application code | Every commit | Indefinitely | Git + GitHub |
| AI-OS files | Weekly | Indefinitely | Git commit |

### Backup Verification
Monthly: verify backups are restorable by doing a test restore to a non-production environment.
