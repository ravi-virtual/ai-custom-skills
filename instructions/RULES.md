# RULES.md — Operational Rules & Policies

## Rule Hierarchy
```
AGENT_RULES.md  (immutable, highest priority)
    ↓
CONSTRAINTS.md  (hard limits)
    ↓
RULES.md        (this file — operational policies)
    ↓
CODING_STANDARDS.md (implementation standards)
    ↓
STACK.md        (technology-specific rules)
```

## Section 1: Code Generation Rules

### 1.1 Naming Conventions
| Entity | Convention | Example |
|--------|-----------|---------|
| Backend controller | PascalCase | `UserController.js` |
| Backend model | PascalCase | `User.js` |
| Backend route file | camelCase | `userRoutes.js` |
| Backend middleware | camelCase | `hasToken.js` |
| Backend validator | camelCase | `userValidator.js` |
| Backend util | camelCase | `apiResponse.js` |
| Frontend component | PascalCase | `UserCard.jsx` |
| Frontend page | PascalCase + Page | `DashboardPage.jsx` |
| Frontend hook | camelCase + use | `useAuth.js` |
| Frontend slice | camelCase + Slice | `userSlice.js` |
| Frontend API file | camelCase + Api | `userApi.js` |
| URL paths | kebab-case plural | `/api/user-profiles` |
| Environment vars | UPPER_SNAKE_CASE | `JWT_SECRET` |
| Frontend env vars | VITE_ prefix | `VITE_API_BASE_URL` |

**Hard rule: Never use `.` in filenames except for the extension.**

### 1.2 File Structure Rules
- One responsibility per file — never mix concerns
- No dots in filenames: `user.controller.js` ❌ → `UserController.js` ✅
- Backend under `backend/src/`; frontend under `frontend/src/`
- Configuration in `backend/src/config/constants.js` only

### 1.3 Import Rules
- Backend: use `require()` with destructuring from constants
- Frontend: use `import` statements
- No barrel files (index.js re-exports) unless explicitly designed
- Import order: node_modules → local config → local utils → local components

---

## Section 2: API Rules

### 2.1 URL Design
```
Collection:    GET    /api/{resource}
Single item:   GET    /api/{resource}/:id
Create:        POST   /api/{resource}
Full replace:  PUT    /api/{resource}/:id
Partial:       PATCH  /api/{resource}/:id
Delete:        DELETE /api/{resource}/:id
Sub-resource:  GET    /api/{resource}/:id/{sub-resource}  (use sparingly)
```

### 2.2 Response Format (Non-Negotiable)
```javascript
// Success
{ success: true, message: "string", data: { /* always object */ } }

// Paginated
{ success: true, message: "string", data: { items: [], totalCount: N } }

// Error
{ success: false, message: "string", error: { code: "ERROR_CODE", details: [] } }
```

### 2.3 Middleware Chain Order
```
hasToken → isAuthenticated → [isAdmin | isUser] → validator → controller
```
Never skip steps in the chain. Never reorder.

---

## Section 3: Database Rules

### 3.1 MongoDB / Mongoose
- All model IDs use UUID v4 (not ObjectId)
- Every model includes `timestamps: true`
- Every model includes `isDeleted: false` flag
- All read queries include `{ isDeleted: false }` filter
- All read queries use `.lean()` for performance
- Soft delete only — set `isDeleted: true`, never use `.deleteOne()`
- `password` field always has `select: false`

### 3.2 PostgreSQL (when used)
- All tables have UUID primary key with `gen_random_uuid()`
- All tables have `is_deleted BOOLEAN DEFAULT FALSE`
- All tables have `created_at` and `updated_at` with triggers
- Every table gets its own `updated_at` trigger function

---

## Section 4: Security Rules

### 4.1 Authentication
- JWT verification in `hasToken.js` middleware only
- Tokens extracted from `Authorization: Bearer <token>` header
- Token expiry handled explicitly (different code for expired vs invalid)
- Refresh tokens stored securely (httpOnly cookie or secure storage)

### 4.2 Authorization
- Role checks in `isAdmin.js` and `isUser.js` middleware
- Never check roles inside controllers
- Admin routes require both `isAuthenticated` and `isAdmin`

### 4.3 Input Security
- All inputs validated via express-validator before reaching controller
- All string inputs trimmed and sanitized
- Email inputs normalized
- No raw SQL string concatenation (use parameterized queries)

---

## Section 5: Frontend Rules

### 5.1 State Management
- Redux Toolkit for all global/shared state
- Context API permitted only for: theme, locale, low-frequency UI state
- Every slice must have: `loading`, `error`, `clearError`, and data fields
- Async operations always via `createAsyncThunk` with `rejectWithValue`

### 5.2 API Layer
- All HTTP calls go through `axiosInstance` (configured with base URL + interceptors)
- Request interceptor attaches `Authorization: Bearer <token>` if token exists
- Response interceptor handles 401 → clear token → redirect to login
- One API file per backend resource (`userApi.js`, `authApi.js`)
- API function names: `{resource}Action + Api` (e.g., `fetchUserApi`, `createOrderApi`)

### 5.3 Component Rules
- One component per file, always default export
- No API calls inside components (dispatch thunks or use hooks)
- No server data in local `useState` (use Redux state)
- Local `useState` allowed for: modal open/close, form input, UI toggle
- Never use `<form action>` — always `onSubmit` + `e.preventDefault()`

---

## Section 6: Testing Rules

### 6.1 Mental Testing Protocol
Before delivering any code, mentally verify:
- Happy path: what happens when everything works correctly
- Not found: what happens when resource doesn't exist
- Unauthorized: what happens when token is missing or invalid
- Forbidden: what happens when role check fails
- Validation: what happens when input is malformed
- Server error: what happens when DB/external service fails

### 6.2 Automated Testing Requirements
- Unit tests for utility functions
- Integration tests for API endpoints (at minimum happy path + 401 + 404)
- E2E tests for critical user flows (login, core feature workflows)

---

## Section 7: Documentation Rules

### 7.1 Code Documentation
- JSDoc required on every controller method
- Inline comments for non-obvious logic only
- No comments that restate what the code obviously does

### 7.2 Decision Documentation
- Every non-trivial architectural decision → DECISIONS.md
- Format: What was decided | Why | Alternatives rejected
- Link to the relevant code file

### 7.3 Knowledge Documentation
- New patterns discovered → KNOWLEDGE_BASE.md
- New error patterns → FAILURES.md
- Performance findings → PERFORMANCE.md

---

## Section 8: Workflow Rules

### 8.1 Task Management
- New tasks added to TASKS.md with ID, description, status
- Status values: `pending | in-progress | blocked | complete`
- Blocked tasks require a blocker description and escalation plan

### 8.2 Session Rules
- Load EXECUTION_MEMORY.md at session start to restore state
- Write final state to EXECUTION_MEMORY.md at session end
- Update SESSION.md with start time, tasks worked, completion status

### 8.3 Change Management
- Major changes proposed in PLANNING.md before execution
- Changes requiring human approval noted in DECISIONS.md as `PENDING_APPROVAL`
- No destructive operations without explicit human confirmation
