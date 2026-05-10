# DEBUGGING.md — Debugging Reference & Protocols

## Core Debugging Philosophy
**Trace → Solve → Clean**
1. **Trace**: Follow the error to its exact source — don't guess
2. **Solve**: Fix the root cause, not the symptom
3. **Clean**: Remove ALL debug artifacts before delivering

This workflow applies to ALL debugging tasks, regardless of framework or layer.

---

## Phase 1: TRACE

### Step 1.1: Capture the Full Error
Never work with a partial error. Collect:
- Full error message
- Stack trace (every line, not just the first)
- HTTP status code (for API errors)
- Request method + URL + body (for API errors)
- Browser console output (for frontend errors)
- Server log output (for backend errors)

### Step 1.2: Identify the Layer
```
Frontend:  Component crash, hook violation, stale state, Axios error
Backend:   Express middleware error, controller exception, validation failure
Database:  Mongoose error, connection failure, schema mismatch
Auth:      JWT error, middleware chain failure, 401/403
Network:   CORS failure, proxy mismatch, SSL error
Full-Stack: Frontend error caused by backend issue (or vice versa)
```

### Step 1.3: Add Instrumentation
Add `// [DEBUG]` prefixed logs at key boundaries:
```javascript
// Backend
console.log('// [DEBUG] hasToken - token:', token?.slice(0, 10));
console.log('// [DEBUG] getUser - id:', req.params.id, 'user:', req.user);
console.log('// [DEBUG] DB query result:', user);

// Frontend
console.log('// [DEBUG] dispatch - fetchUser called with:', userId);
console.log('// [DEBUG] Redux state:', store.getState().user);
console.log('// [DEBUG] Axios response:', response.data);
```

**Rules for debug logs:**
- ALWAYS prefix with `// [DEBUG]`
- Include the function name and key variable
- Include value snippets, not full objects (risk of PII exposure in logs)
- REMOVE ALL before final delivery

### Step 1.4: Follow the Data Flow
Trace the request from entry to failure:
```
For Backend:
HTTP Request → CORS → Helmet → Body Parser → Router → 
hasToken → isAuthenticated → isAdmin/isUser → Validator → Controller → DB → Response

For Frontend:
User Action → Component handler → Dispatch → Thunk → axiosInstance → 
Request interceptor → API call → Response interceptor → Redux state → Re-render
```

Stop at the first point where data is wrong or missing — that's your failure zone.

---

## Phase 2: SOLVE

### Step 2.1: Form a Hypothesis
Based on the trace, state your hypothesis:
```
"The error occurs because: [exact statement]"
Example: "The error occurs because req.user is undefined when it reaches the controller,
          which means hasToken is not executing or is not calling next()"
```

### Step 2.2: Check Known Failures
Search FAILURES.md for similar errors before investigating from scratch.

### Step 2.3: Common Error Patterns

#### Express/Node.js
| Error | Root Cause | Fix |
|-------|-----------|-----|
| `Cannot set headers after they are sent` | Missing `return` on response call | Add `return` before every `res.json()/sendError()` |
| `Route handler not found` | Route not registered in app.js | Add `app.use('/api/resource', router)` |
| `Cannot read property 'X' of undefined` | Middleware not populating req.X | Check middleware chain, confirm next() is called |
| `CastError: Cast to ObjectId failed` | UUID string passed to ObjectId field | Schema `_id: { type: String }`, queries use string |
| `E11000 duplicate key` | Unique index violation | Catch error, return 409 Conflict |
| `JsonWebTokenError: invalid signature` | Wrong JWT secret | Check constants.js has correct secret from .env |
| `TokenExpiredError` | Access token expired | Frontend should trigger refresh flow |
| `EADDRINUSE` | Port already in use | Kill process on port: `npx kill-port 5000` |

#### React/Redux
| Error | Root Cause | Fix |
|-------|-----------|-----|
| `Warning: Maximum update depth exceeded` | setState in render or wrong useEffect deps | Add correct deps array, move setState into handlers |
| `Invalid hook call` | Hook called outside component or in condition | Move hook to top level of component |
| `Rendered more hooks than previous render` | Conditional hook call | Remove conditions around hooks |
| `Cannot read property 'X' of null` | Accessing Redux state before loaded | Add null check: `state.user?.name` |
| `Network Error` (Axios) | CORS, proxy config, or server not running | Check server is running; check CORS config |
| `401 on valid token` | Token not being sent or interceptor not working | Check axiosInstance interceptor attaches token |
| State not updating | Mutating state outside Redux | Never mutate state directly; use slice reducer |

#### CORS Issues
```
Symptoms: "No 'Access-Control-Allow-Origin' header" in browser console
Causes:
  1. Backend CORS origin doesn't match frontend URL (check port)
  2. Credentials not set (withCredentials: true missing)
  3. CORS middleware loaded after routes

Fix:
  - Backend: app.use(cors(corsOptions)) BEFORE app.use('/api', router)
  - Backend: Add exact frontend origin to corsOptions
  - Frontend: axios config: withCredentials: true if using cookies
```

### Step 2.4: Apply the Fix
- Make the smallest possible change that fixes the root cause
- Don't change unrelated code while fixing a bug
- Comment why the fix was necessary (if non-obvious)
- Document in FAILURES.md before moving to cleanup

---

## Phase 3: CLEAN

### Step 3.1: Remove ALL Debug Logs
```bash
# Find all debug logs added during this session
grep -r "// \[DEBUG\]" src/

# Remove them manually (search and delete in IDE)
# Or use: sed -i '/\/\/ \[DEBUG\]/d' filename.js
```

**Zero tolerance**: Even a single `// [DEBUG]` log left in the codebase is incomplete work.

### Step 3.2: Verify the Fix
After removing debug logs:
1. Restart the server / refresh the frontend
2. Reproduce the exact steps that caused the original error
3. Confirm the error no longer occurs
4. Confirm no new errors were introduced

### Step 3.3: Document
Write to FAILURES.md:
```markdown
## Failure [ID]: [Error name]
**Date**: YYYY-MM-DD
**Environment**: development
**Affected Component**: [controller/component name]
**Error**: [Full error message]
**Root Cause**: [Exact cause]
**Fix Applied**: [What was changed]
**Prevention**: [How to avoid this in future]
```

---

## Quick Reference: Debug Command Cheatsheet

```bash
# Kill process on specific port
npx kill-port 5000

# Check what's running on port 5000
netstat -ano | findstr :5000       # Windows
lsof -ti:5000                      # Mac/Linux

# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Check Node.js version
node --version

# Check npm packages are installed
ls node_modules | head

# Clear npm cache (if install issues)
npm cache clean --force

# Check if env vars are loaded
node -e "require('dotenv').config(); console.log(process.env.MONGO_URI)"
```
