# LEARNINGS.md — Discovered Patterns & Optimizations

## Purpose
Document valuable insights, patterns, and optimizations discovered during development. Each learning should be actionable — either already applied or with a clear action required.

---

## LEARN-001: Return Keyword is Critical in Express Controllers
**Date**: 2026-04-12  
**Source**: BUG-002, BUG-003 debugging sessions  

**Learning**: Missing `return` before `res.json()` or `ApiResponse.send()` is one of the most common Express bugs. Without it, execution continues after the response, causing "Cannot set headers after they are sent" errors or silent request hangs.

**Applied To**: CODING_STANDARDS.md (explicit rule added), code review checklist

**Action Required**: None — pattern is documented and enforced in reviews.

---

## LEARN-002: Redux State Does Not Survive Page Refresh
**Date**: 2026-04-12  
**Source**: BUG-005 profile persistence investigation  

**Learning**: Redux is an in-memory store. Every page refresh starts with `initialState`. Server data (users, profiles, settings) must always be fetched from the API on component mount or on authentication. Never assume Redux state will persist across refreshes without explicit persistence (redux-persist).

**Applied To**: FRONTEND.md (documented in state management rules), BUG-005

**Action Required**: All features that load server data must dispatch a fetch thunk on mount.

---

## LEARN-003: Axios Interceptors Need Escape Conditions
**Date**: 2026-04-12  
**Source**: BUG-006 token refresh infinite loop  

**Learning**: A 401 response interceptor that triggers refresh must:
1. Skip refresh for the refresh endpoint itself
2. Use a `_retry` flag to prevent re-triggering on the retried request

Without both guards, a failed refresh creates an infinite loop.

**Applied To**: FRONTEND.md (Axios Instance section), FAILURES.md BUG-006

**Action Required**: Review all axiosInstance configurations to confirm both guards are in place.

---

## LEARN-004: Middleware Chain Must Be Complete on Every Route
**Date**: 2026-04-12  
**Source**: BUG-003, BUG-004  

**Learning**: Route security is only as strong as its middleware chain. A single route missing `hasToken` creates an authentication bypass. The order matters: `hasToken → isAuthenticated → [isAdmin|isUser] → validator → controller`.

**Applied To**: BACKEND.md, RULES.md, AGENT_RULES.md

**Action Required**: Add a route security audit to CI — automatically flag routes that don't include `hasToken`.

---

## LEARN-005: Boolean Schema Fields Require Type-Coercing Validators
**Date**: 2026-04-12  
**Source**: BUG-001 feedback casting error  

**Learning**: When a Mongoose schema field is Boolean, the validator must:
1. Validate it IS a boolean: `body('field').isBoolean()`
2. Coerce it: `.toBoolean()` — converts `"true"`, `"false"`, `1`, `0` to proper Boolean

Without coercion, strings like `"true"` will fail the Mongoose type check even though they're logically valid.

**Applied To**: FAILURES.md BUG-001, validator pattern in BACKEND.md

**Action Required**: Review all validators for Boolean fields — ensure they use `.toBoolean()`.

---

## LEARN-006: Circular Requires Silently Fail in Node.js
**Date**: 2026-04-12  
**Source**: BUG-004 hasToken not executing  

**Learning**: In Node.js CommonJS, circular dependencies don't throw errors — they resolve to an empty object `{}`. This means a middleware imported through a circular path becomes `undefined`, and Express silently skips `undefined` middleware without throwing. This is extremely hard to debug because no error appears.

**Applied To**: FAILURES.md BUG-004, DEBUGGING.md

**Action Required**: 
- Keep require chains linear (no circular dependencies)
- Add startup validation: all middleware must be `typeof === 'function'`
- Use `eslint-plugin-import/no-cycle` to detect circular imports

---

## LEARN-007: Multi-Model AI Fallback Requires Per-Model Timeout
**Date**: 2026-04-12  
**Source**: Conversation e5e1b2e6  

**Learning**: When implementing AI model fallback chains (Gemini → Grok → OpenAI), each model needs its own timeout configuration because:
- Different models have different cold-start times
- Default Axios timeout may be too short for some models
- A hung primary model without timeout will block the fallback indefinitely

**Applied To**: DECISIONS.md DEPLOY-001

**Action Required**: Ensure each model in the fallback chain has explicit timeout (e.g., 10s for primary, 8s for secondary, 6s for tertiary).

---

## LEARN-008: Profile Form Multi-Step Validation Pattern
**Date**: 2026-04-12  
**Source**: Conversation 249023b8  

**Learning**: For multi-step forms, validation must happen in two places:
1. **On Next click**: Validate only the current step's fields
2. **On Save click**: Validate ALL fields across all steps before submission

Both validations should prevent progression/submission if invalid, showing field-specific error messages.

**Applied To**: PLANNING.md (form validation patterns)

**Action Required**: Create a reusable `validateStep(stepIndex, formData)` utility function for multi-step forms.

---

## LEARN-009: Hamburger Menu Needs Three Closing Triggers
**Date**: 2026-04-12  
**Source**: Conversation 824a485f  

**Learning**: A responsive hamburger menu needs to close in three scenarios:
1. Click the X/close button
2. Click a menu item
3. Click anywhere outside the menu

Scenario 3 requires adding a click listener to `document` with a check: if `event.target` is not inside the menu element, close the menu. The listener must be removed in the cleanup function to prevent memory leaks.

**Applied To**: Frontend component patterns, FRONTEND.md

**Action Required**: None — pattern is documented for future implementation.

---

## LEARN-010: AI OS Files Must Be Comprehensive, Not Filler
**Date**: Current session  
**Source**: AI OS generation task  

**Learning**: AI operating system files only provide value if they contain production-grade, specific instructions. Files with vague guidance ("write good code") provide no actionable context to AI agents. Every file must contain:
- Specific patterns with code examples
- Exact rules with rationale
- Precise tool invocation instructions
- Clear failure handling protocols

**Applied To**: All files in this AI OS

**Action Required**: After initial creation, review each file to ensure no entry is vague or filler.
