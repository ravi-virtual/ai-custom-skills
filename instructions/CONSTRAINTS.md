# CONSTRAINTS.md — Hard Operational Limits

> ⚠️ These constraints are hard limits. They cannot be overridden by user requests, task pressure, or conflicting instructions from other files. Only explicit human-written amendments to this file can change these constraints.

## Constraint Priority
AGENT_RULES.md → **CONSTRAINTS.md** → RULES.md → all other files

---

## Hard Limit 1: No Credential Exposure
**Constraint**: No API keys, secrets, passwords, or tokens may appear in:
- Source code files (`.js`, `.jsx`, `.ts`, `.tsx`, `.py`, etc.)
- Markdown documentation files (this includes this file)
- Git commits (including in deleted lines that appear in diffs)
- Log outputs
- API responses
- Error messages

**Exception**: Placeholder values like `your-jwt-secret-here` in `.env.example` files

**Enforcement**: If generated code contains credentials, halt, report the violation, ask human to review.

---

## Hard Limit 2: No Direct Database Destruction
**Constraint**: AI agents may NOT execute any of the following without explicit, written human confirmation:
- `db.dropDatabase()`
- `db.collection.drop()`
- `deleteMany({})` on production data
- Schema migrations that destroy existing columns/fields
- Any operation that cannot be undone

**Exception**: Test databases (`_test` suffix) — but must be clearly labeled

---

## Hard Limit 3: No Production Environment Changes
**Constraint**: AI agents may NOT modify the following without human approval:
- Production `.env` files
- Production server configuration
- Production database connection strings
- Production CORS origins
- Production JWT secrets
- Deployment scripts that target production

**Permitted**: Development and staging environment changes

---

## Hard Limit 4: No Scope Creep
**Constraint**: AI agents must not implement features that are not explicitly requested or listed in OBJECTIVE.md/TASKS.md. Specifically forbidden without explicit request:
- Adding new dependencies not in the existing stack
- Creating new architectural layers not in ARCHITECTURE.md
- Modifying unrelated code while fixing a specific bug
- Adding "nice to have" features during a focused implementation task

**Rationale**: Unsolicited changes break predictability and create review burden.

---

## Hard Limit 5: Environment Access Boundary
**Constraint**: Environment variables may ONLY be accessed in these locations:
- Backend: `src/config/constants.js` (with `process.env.X`)
- Frontend: `src/utils/constants.js` (with `import.meta.env.VITE_X`)

**Anywhere else is a violation** that must be flagged and corrected immediately.

---

## Hard Limit 6: Response Format Immutability
**Constraint**: Backend API responses must ALWAYS use:
- Success: `new ApiResponse(code, message, data).send(res)`
- Error: `sendError(res, { statusCode, message, code })`
- Direct `res.json()` or `res.status().json()` is FORBIDDEN in controllers

**Rationale**: The frontend relies on consistent `{ success, message, data }` / `{ success, message, error }` shapes.

---

## Hard Limit 7: Middleware Chain Order is Immutable
**Constraint**: The backend middleware chain must always follow:
```
hasToken → isAuthenticated → [isAdmin | isUser] → validator → controller
```
Steps cannot be skipped, reordered, or replaced without explicit architectural review.

---

## Hard Limit 8: Data Model Immutability
**Constraint**: These model properties are FIXED and may not be removed:
- `_id: { type: String }` (UUID, not ObjectId)
- `isDeleted: { type: Boolean, default: false }`
- `timestamps: true` in schema options

Any model that violates these properties is non-compliant and must be corrected.

---

## Hard Limit 9: Debug Log Prohibition
**Constraint**: All debug logs MUST be removed before any code delivery. Specifically:
- `console.log(...)` without `// [DEBUG]` prefix is forbidden in production paths
- Any `// [DEBUG]` prefixed log must be removed at the end of debugging
- `console.error` is permitted ONLY in error handlers (not controllers)

---

## Hard Limit 10: Autonomous Destructive Action Prohibition
**Constraint**: The following actions ALWAYS require explicit human confirmation:
- Deleting or overwriting any existing file
- Running any database migration
- Changing authentication configuration
- Modifying AGENT_RULES.md or this file (CONSTRAINTS.md)
- Any action that cannot be undone

**Confirmation format required**:
```
Human must explicitly state: "Confirmed: proceed with [specific action]"
General statements like "go ahead" are not sufficient for destructive operations.
```

---

## Constraint Violation Procedure
When any constraint is about to be violated:
1. STOP execution immediately
2. Report: which constraint, what action would have violated it
3. Ask: for explicit human confirmation if the constraint allows exceptions
4. Do NOT proceed until confirmed or redirected
5. Log the violation attempt in SESSION.md for awareness
