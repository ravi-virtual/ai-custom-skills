# FAILURES.md — Bug Reports & Root Cause Analysis

## Purpose
Document every bug encountered, its root cause, and the fix applied. This prevents re-investigating the same issues and builds institutional knowledge about failure patterns.

## Format
```markdown
## [ID] [Error Name]
**Date**: YYYY-MM-DD
**Environment**: development | staging | production
**Severity**: Critical | High | Medium | Low
**Affected Component**: [file/module/endpoint]
**Error**: [Full error message]
**Root Cause**: [Exact reason]
**Fix Applied**: [What changed]
**Prevention**: [How to avoid this]
```

---

## BUG-001: CastError on Feedback Submission
**Date**: 2026-04-12  
**Environment**: development  
**Severity**: High  
**Affected Component**: Feedback API endpoint, profileValidator.js  
**Reference**: Conversation 9a00e0dc  

**Error**:
```
CastError: Cast to Boolean failed for value "up" (type string) at path "rating"
```

**Root Cause**: 
Frontend was sending the string value `"up"` for the rating field, but the Mongoose schema defined `rating` as `Boolean`. The validator was not enforcing the correct type before passing data to the model.

**Fix Applied**:
1. Added validator rule: `body('rating').isBoolean().toBoolean()`
2. Updated frontend API call to send `true`/`false` instead of `"up"`/`"down"`

**Prevention**:
- Frontend must always map semantic values (up/down, yes/no, like/dislike) to Boolean before API calls
- Validator must use `.toBoolean()` to coerce compatible values
- Add explicit Boolean validation to any field that stores a binary choice

---

## BUG-002: GET /api/profile Not Returning Response
**Date**: 2026-04-12  
**Environment**: development  
**Severity**: Critical  
**Affected Component**: profileRoutes.js, ProfileController.js  
**Reference**: Conversation 2ba0c2d9  

**Error**:
```
Request hangs — no response, no error
```

**Root Cause**:
Controller function was missing the `return` keyword before the `ApiResponse.send()` call. Without `return`, execution continued past the response and triggered "Cannot set headers after they are sent" on the second response attempt, causing Express to hang.

**Fix Applied**:
Added `return` before every response call in the controller:
```javascript
// Before (broken)
new ApiResponse(ResponseCodes.OK, 'Profiles fetched', { profiles }).send(res);

// After (correct)
return new ApiResponse(ResponseCodes.OK, 'Profiles fetched', { profiles }).send(res);
```

**Prevention**:
- RULE: Always `return` response calls in Express controllers (see CODING_STANDARDS.md)
- Code review checklist item: "All response calls have return keyword"
- Missing `return` before response = likely cause of hanging requests

---

## BUG-003: POST /api/profile 401 Unauthorized
**Date**: 2026-04-12  
**Environment**: development  
**Severity**: High  
**Affected Component**: hasToken.js, profileRoutes.js  
**Reference**: Conversation 2ba0c2d9  

**Error**:
```
POST /api/profile → 401 Unauthorized
{"success": false, "message": "No token provided"}
```

**Root Cause**:
The route registration in `profileRoutes.js` was missing the `hasToken` middleware in the chain. The route was registered as:
```javascript
router.post('/', validateProfile, createProfile);  // ← missing auth middleware
```
Instead of:
```javascript
router.post('/', hasToken, isAuthenticated, isUser, validateProfile, createProfile);
```

**Fix Applied**:
Added complete middleware chain to the route definition.

**Prevention**:
- RULE: Every protected route MUST have the full middleware chain (see AGENT_RULES.md Rule 3)
- Code review checklist item: "Every protected route has hasToken + isAuthenticated + role middleware"
- Route files should be reviewed in pairs with their controllers — never add route without verifying auth

---

## BUG-004: hasToken Middleware Not Executing
**Date**: 2026-04-12  
**Environment**: development  
**Severity**: High  
**Affected Component**: app.js, userRoutes.js  
**Reference**: Conversation 64790f93  

**Error**:
```
POST /api/generate/headline → 401
hasToken middleware logs not appearing
```

**Root Cause**:
Route was registered in app.js BEFORE the `hasToken` middleware was imported, and due to a circular require, the middleware reference was `undefined`. The route silently skipped the undefined middleware.

**Fix Applied**:
1. Verified all middleware imports in app.js resolve correctly
2. Added explicit check: middleware must be a function before use
3. Reordered imports to eliminate circular dependency

**Prevention**:
- Always log "hasToken loaded" on startup to verify middleware is available
- Circular require errors in Node.js are silent — check with `console.log(require('./middlewares/hasToken'))` if middleware seems inactive
- Import all middleware at top of app.js before any route registration

---

## BUG-005: Profile Not Persisting Across Page Refresh
**Date**: 2026-04-12  
**Environment**: development  
**Severity**: Medium  
**Affected Component**: profileSlice.js, ProfilePage.jsx  
**Reference**: Conversation 0de175eb  

**Error**:
```
Profile data visible after saving, but disappears on page refresh
```

**Root Cause**:
`fetchProfiles` thunk was not being dispatched on app load / authentication. Redux state resets to `initialState` on refresh (Redux is in-memory). The profile data was only loaded once during the session, not re-fetched on page load.

**Fix Applied**:
1. Added `useEffect` in the main layout or AuthGuard to dispatch `fetchProfiles` when user is authenticated
2. Profile is now fetched from API on every page load (not from Redux alone)

**Prevention**:
- Redux is not persistent by default — server data must always be re-fetched on load
- RULE: Don't rely on Redux state surviving a page refresh; always fetch on mount
- Use redux-persist only if explicitly designed for it (with proper rehydration logic)

---

## BUG-006: Frontend Token Refresh Loop
**Date**: 2026-04-12  
**Environment**: development  
**Severity**: High  
**Affected Component**: axiosInstance.js  
**Reference**: Conversation 1da58224  

**Error**:
```
Infinite loop of 401 → refresh requests → 401 again
Page becomes unresponsive
```

**Root Cause**:
The Axios response interceptor was retrying ALL 401 responses, including the refresh token endpoint itself. When the refresh endpoint returned 401 (expired/invalid refresh token), the interceptor tried to refresh again — causing infinite recursion.

**Fix Applied**:
1. Added URL check before triggering refresh: skip if request URL includes `/auth/refresh`
2. Added flag `_retry` on config to prevent retrying more than once

```javascript
if (error.response?.status === 401 && !error.config._retry) {
  if (error.config.url.includes('/auth/refresh')) {
    // Don't retry — logout instead
    store.dispatch(clearAuth());
    return Promise.reject(error);
  }
  error.config._retry = true;
  // ... proceed with refresh
}
```

**Prevention**:
- RULE: Refresh token endpoint must be excluded from 401 retry logic
- RULE: Use `_retry` flag to prevent double retry
- Any interceptor that retries must have explicit escape conditions

---

## Failure Pattern Summary

| Pattern | Count | Prevention |
|---------|-------|-----------|
| Missing `return` before response | 3 | Always return responses; code review checklist |
| Missing middleware in route chain | 2 | Review route file completely before merging |
| Redux state not persisted across refresh | 1 | Always fetch server data on mount |
| Token/auth retry loop | 1 | Exclude auth endpoints from retry interceptors |
| Type mismatch (string vs Boolean) | 1 | Use validator coercions; align schema and frontend |
