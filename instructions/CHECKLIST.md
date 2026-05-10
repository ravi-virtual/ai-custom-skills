# CHECKLIST.md — Master Checklists

## Purpose
Pre-execution, pre-delivery, pre-deployment, and code review checklists. Every checklist item is derived from a real bug or standard that has been violated at least once.

---

## Checklist 1: Pre-Task (Run Before Any Coding)

```
□ AGENT_RULES.md loaded and understood for this session
□ CONSTRAINTS.md hard limits identified for this task type
□ Task scope defined — what IS in scope and what is NOT
□ Correct skill identified and SKILL.md read
□ FAILURES.md checked — has a similar bug happened before?
□ MEMORY.md checked — is there an established pattern for this?
□ Confidence level assessed: if < 60%, gather context first
□ Destructive operations identified → human confirmation obtained
```

---

## Checklist 2: Backend Code Pre-Delivery

### Controller
```
□ JSDoc block present on every exported method (@name, @file, @param, @description)
□ Every async function has try/catch wrapping the entire body
□ Every response call has 'return' before it
□ Only ApiResponse (success) or sendError (error) — zero raw res.json()
□ No process.env.X access — all constants imported from constants.js
□ No debug logs (// [DEBUG] prefix or any leftover console.log)
□ No hardcoded strings for status codes, error codes, or roles — use constants
```

### Route File
```
□ Full middleware chain: hasToken → isAuthenticated → [role] → validator → controller
□ No business logic in the route file (only middleware references)
□ Protected routes NEVER skip hasToken
□ camelCase filename (userRoutes.js, profileRoutes.js)
□ Router exported correctly (module.exports = router)
□ Route registered in app.js
```

### Validator
```
□ Every POST/PATCH/PUT endpoint has a validator
□ validator array ends with validateRequest middleware
□ Boolean fields use .isBoolean().toBoolean()
□ Integer fields use .isInt().toInt()
□ String fields use .trim() to remove whitespace
□ Optional fields use .optional() before validation rules
□ Required fields have clear .withMessage() messages
```

### Model
```
□ _id: { type: String, default: uuidv4 } present
□ isDeleted: { type: Boolean, default: false } present
□ timestamps: true in schema options
□ _id: false in schema options (prevent Mongoose auto-id)
□ toJSON transform removes __v (and password if user model)
□ Appropriate indexes defined on the schema
□ select: false on password field (user model only)
```

### Database Queries
```
□ Every read query includes { isDeleted: false } filter
□ Every read query uses .lean()
□ List queries use .select() to limit fields
□ List queries use .limit() and .skip() for pagination
□ Write queries use findOneAndUpdate with { new: true } when returning result
□ Unique constraint violations handled (error code 11000)
□ No deleteOne/deleteMany on user data — use { isDeleted: true } instead
```

---

## Checklist 3: Frontend Code Pre-Delivery

### Redux Slice
```
□ initialState has loading, error, and clearError at minimum
□ clearError reducer resets error to null
□ All thunks use rejectWithValue for user-friendly error messages
□ pending handler: loading = true, error = null
□ fulfilled handler: loading = false, data updated
□ rejected handler: loading = false, error = action.payload
□ Slice exported correctly (export default sliceName.reducer)
□ Actions exported individually (export const { clearError } = slice.actions)
```

### API File
```
□ All calls use axiosInstance — zero raw axios imports
□ Function names match the endpoint they call (fetchUsersApi, createProfileApi)
□ camelCase filename with Api suffix (userApi.js, profileApi.js)
□ No state management in API file — just the HTTP call
```

### Component / Page
```
□ PascalCase filename and function name
□ Default export used
□ No inline API calls — all through dispatch(thunk())
□ useDispatch and useSelector at top of component
□ clearError dispatched in useEffect cleanup function
□ Loading state handled (spinner or disabled button)
□ Error state displayed to user (not swallowed silently)
```

### Custom Hook
```
□ camelCase filename with 'use' prefix (useProfile.js)
□ Dispatches thunks, does not call API directly
□ Returns derived state (not raw Redux state)
□ Handles useEffect with proper dependency array
□ Cleanup function dispatches clearError
```

---

## Checklist 4: Security Pre-Delivery

```
□ No credentials, API keys, or secrets in any file
□ No sensitive user data (passwords, tokens) in API responses
□ No stack trace in production error responses
□ JWT validation in hasToken covers: format, signature, expiry
□ All protected routes have hasToken + isAuthenticated + role middleware
□ Input validation present on all POST/PATCH/PUT endpoints
□ Passwords go through bcrypt with cost factor ≥ 10
□ CORS restricted to known origin (not *)
□ Rate limiting configured on auth endpoints
```

---

## Checklist 5: Pre-Deployment

```
□ All automated tests passing (npm test)
□ Zero ESLint errors (npm run lint)
□ Zero debug logs (grep -r "// \[DEBUG\]" src/)
□ Zero hardcoded secrets (manual audit)
□ All CODING_STANDARDS.md naming conventions followed
□ API.md updated for any new or changed endpoints
□ DATABASE.md updated for any schema changes
□ DECISIONS.md updated for any architectural choices
□ TASKS.md task marked complete
□ Environment variables verified in target environment
□ Health check endpoint tested locally: GET /api/health → 200
□ Core user flow tested manually end-to-end
□ Bundle size within budget (< 500KB gzipped)
```

---

## Checklist 6: Post-Deployment Verification

```
□ Health check passes in production: GET /api/health → 200
□ User registration flow works
□ User login flow works (access token + refresh token cookie set)
□ Token refresh works (call /api/auth/refresh → new access token)
□ Core feature works (profile creation / AI generation)
□ No 5xx errors in logs for first 5 minutes
□ Response times within PERFORMANCE.md budgets
□ SESSION.md updated with deployment details
```

---

## Checklist 7: Code Review

```
□ File naming follows CODING_STANDARDS.md conventions
□ File located in correct directory per ARCHITECTURE.md
□ Imports ordered: Node built-ins → npm packages → local files
□ No unused imports
□ No commented-out code blocks
□ JSDoc on all controller methods
□ No magic numbers or magic strings — use constants
□ try/catch on all async functions
□ return before all response calls
□ Mental test performed and passed (all HTTP paths)
□ No TODO or FIXME comments in production code
```

---

## Permanent Checks (Never Remove These)

These were added because real bugs slipped through. They must remain forever:

| Check | Source Bug |
|---|---|
| `return` before every response call | BUG-002: missing return caused request hang |
| Full middleware chain on every route | BUG-003: missing hasToken allowed auth bypass |
| Exclude refresh endpoint from 401 retry | BUG-006: caused infinite token refresh loop |
| `.isBoolean().toBoolean()` on Boolean fields | BUG-001: "up" string failed Boolean cast |
| Fetch server data on mount (not rely on Redux) | BUG-005: profile disappeared on page refresh |
| Check circular requires if middleware is `{}` | BUG-004: circular require silently broke middleware |
