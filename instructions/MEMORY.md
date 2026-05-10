# MEMORY.md — Persistent Memory & Knowledge State

## Memory Architecture Overview
This file is the persistent memory layer for AI agents in this system. It stores decisions, patterns, facts, and context that must survive across sessions.

## Memory Categories

### 1. Architectural Decisions (Long-Term)
Decisions that define system structure — loaded first, rarely overridden.

| Decision ID | Decision | Rationale | Date | Status |
|-------------|----------|-----------|------|--------|
| ARCH-001 | Use MERN stack (MongoDB, Express, React, Node.js) | Full-stack JavaScript, mature ecosystem, strong community | Initial | Active |
| ARCH-002 | UUID `_id` for all MongoDB models | Cross-system portability, no ObjectId serialization issues | Initial | Active |
| ARCH-003 | Redux Toolkit for all React global state | Predictable state, dev tools, reduced boilerplate | Initial | Active |
| ARCH-004 | Single `constants.js` as source of truth for all config | Eliminates scattered env access, enforces fail-fast startup | Initial | Active |
| ARCH-005 | Soft delete only (isDeleted flag) for user data | Data recovery, audit trail, regulatory compliance | Initial | Active |
| ARCH-006 | JWT authentication with 15m access + 15m refresh tokens | Short-lived access tokens minimize breach window | Initial | Active |
| ARCH-007 | express-validator for input validation (not Joi) | Native Express integration, familiar pattern | Initial | Active |

### 2. Technology Choices (Long-Term)
| Choice | Selected | Rejected | Reason |
|--------|----------|----------|--------|
| CSS framework | Vanilla CSS | TailwindCSS, Bootstrap | Maximum control; no dependency debt |
| Auth strategy | JWT (stateless) | Sessions (stateful) | Scalability across multiple servers |
| State management | Redux Toolkit | Zustand, Context API | Mature, predictable, excellent DevTools |
| ORM/ODM | Mongoose (MongoDB) | TypeORM, Prisma | Native MongoDB pattern, schema validation |
| API testing | Mental testing + Postman | Jest integration tests | Speed; add automated tests when stable |

### 3. Pattern Library (Operational)
Established patterns that must be reused — never reinvented.

#### Backend Patterns
```javascript
// Controller structure (MUST follow this)
const methodName = async (req, res) => {
  try {
    // validation, DB query, business logic
    return new ApiResponse(ResponseCodes.OK, 'message', { data }).send(res);
  } catch (err) {
    return sendError(res, { statusCode: ResponseCodes.SERVER_ERROR, message: err.message });
  }
};

// Route chain (MUST follow this order)
router.verb('/path', hasToken, isAuthenticated, [isAdmin|isUser], validationRules, controller);

// Model structure (MUST follow this)
const schema = new mongoose.Schema({
  _id: { type: String, default: uuidv4 },
  // ... fields
  isDeleted: { type: Boolean, default: false }
}, {
  timestamps: true,
  _id: false,
  toJSON: { transform(doc, ret) { delete ret.__v; delete ret.password; } }
});
```

#### Frontend Patterns
```javascript
// Slice structure (MUST follow this)
const slice = createSlice({
  name: 'feature',
  initialState: { data: null, loading: false, error: null },
  reducers: { clearError: (state) => { state.error = null; } },
  extraReducers: (builder) => { /* thunk cases */ }
});

// Thunk structure (MUST follow this)
export const fetchData = createAsyncThunk('feature/fetch', async (params, { rejectWithValue }) => {
  try {
    const { data } = await fetchDataApi(params);
    return data.data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed');
  }
});
```

### 4. Known Issues & Gotchas (Operational)
Patterns that have caused bugs before — avoid these.

| Issue | Context | Correct Approach |
|-------|---------|-----------------|
| ObjectId vs UUID | MongoDB queries | Always use UUID string; never mix with ObjectId |
| Password in response | User queries | Always `select: false` on password field; strip in toJSON |
| Missing isDeleted filter | Find queries | Every `.find()` must include `{ isDeleted: false }` |
| Unauthorized vs Forbidden | Auth middleware | 401 = no/invalid token; 403 = valid token, wrong role |
| Token expired error code | JWT errors | `TokenExpiredError` → `TOKEN_EXPIRED` code, not `INVALID_TOKEN` |
| Redux state mutation | Slice reducers | State mutations OK inside createSlice (Immer); never mutate outside |
| Raw axios in components | API calls | Always import functions from `api/` folder, never raw axios |

### 5. System Constants Reference (Fast Lookup)
```javascript
// Response codes
OK: 200, CREATED: 201, NO_CONTENT: 204
BAD_REQUEST: 400, UNAUTHORIZED: 401, FORBIDDEN: 403
NOT_FOUND: 404, CONFLICT: 409, UNPROCESSABLE: 422
SERVER_ERROR: 500

// Error codes (strings)
VALIDATION_ERROR, NOT_FOUND, UNAUTHORIZED, FORBIDDEN
DUPLICATE_ERROR, INVALID_TOKEN, TOKEN_EXPIRED, SERVER_ERROR

// Roles
ADMIN: 'admin', USER: 'user'
```

### 6. Skill Trigger Memory
When user intent matches these patterns, activate the corresponding skill:

| Intent Pattern | Skill |
|---|---|
| Build/extend backend, add API, new route, create controller | backend-expressjs |
| Build/extend frontend, React component, Redux slice, hook | frontend-reactjs |
| Full-stack MERN, new project, scaffold, setup | mern-stack-project |
| Design workflow, automation, pipeline, agent architecture | agent-workflow-creator |
| Express error, 500, middleware hang, async issue | debug-expressjs-error |
| React error, hook violation, render issue, state bug | debug-reactjs-error |
| CORS, proxy, full-stack integration, auth flow bug | debug-mern-stack-error |
| Sails.js error, Waterline, action crash, policy block | debug-sailsjs-error |
| Create Sails API endpoint | sailsjs-api |
| Create Sails helper | sailsjs-helper |
| Write prompt, improve prompt, optimize prompt | prompt-writing |
| Create skill, build skill, optimize skill description | skill-creator |

## Memory Update Protocol
Agents must update memory in these situations:
- After completing a task → update patterns if new pattern established
- After fixing a bug → add to "Known Issues" if not already documented
- After making an architectural decision → add to "Architectural Decisions"
- After discovering a tech limitation → add to "Known Issues"
- **Never remove entries** — mark as `deprecated` instead

## Memory Retrieval Priority
1. Load AGENT_RULES.md (immutable rules)
2. Load CONSTRAINTS.md (hard limits)
3. Load this file (MEMORY.md) — persistent knowledge
4. Load EXECUTION_MEMORY.md — last session state
5. Load CONTEXT.md — current session context
