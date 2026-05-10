# WORKFLOW.md — Standard Operating Workflows

## Purpose
Defines the exact step-by-step workflows for the most common development tasks. Every workflow is atomic, testable, and produces a verifiable output.

> Related: `AI_WORKFLOW.md` defines agent-level automation. This file defines human+AI collaborative workflows.

---

## Workflow 1: New Feature — Full MERN Stack

```
TRIGGER: User asks to implement a new feature end-to-end
DURATION: 20-60 minutes depending on complexity
OUTPUT: Working backend API + connected frontend UI
```

### Phase 1: Plan (5 min)
- [ ] Define the data model (fields, types, constraints)
- [ ] Define the API contract (method, path, request body, response shape)
- [ ] Define the UI flow (what the user sees, what they click, what happens)
- [ ] Identify which skill applies → load that skill's SKILL.md

### Phase 2: Backend (15-20 min)
- [ ] Create/update Mongoose model (`src/models/`)
- [ ] Add validator rules (`src/validators/`)
- [ ] Create controller methods with JSDoc + try/catch (`src/controllers/`)
- [ ] Register routes with full middleware chain (`src/routes/`)
- [ ] Add any new constants to `src/config/constants.js`
- [ ] Mental test: run all paths (happy path, 401, 403, 404, 422, 500)

### Phase 3: Frontend (15-20 min)
- [ ] Create API function file (`src/api/featureApi.js`)
- [ ] Create Redux slice with loading/error/clearError (`src/store/slices/featureSlice.js`)
- [ ] Create custom hook (`src/hooks/useFeature.js`)
- [ ] Create/update page or component (`src/pages/` or `src/components/`)
- [ ] Wire up to Redux store (`src/store/store.js`)
- [ ] Connect routes if new page (`src/router/`)

### Phase 4: Verify (5 min)
- [ ] CODING_STANDARDS.md pre-delivery checklist complete
- [ ] SECURITY.md checklist reviewed
- [ ] No debug logs remaining
- [ ] Files list delivered to user

---

## Workflow 2: Bug Fix

```
TRIGGER: Error reported, unexpected behavior, failing test
DURATION: 10-30 minutes
OUTPUT: Fixed code + FAILURES.md entry + no debug logs
```

### Phase 1: Trace
- [ ] Read the full error message and stack trace
- [ ] Check FAILURES.md — has this bug been seen before?
- [ ] Identify the exact file and line of origin
- [ ] Add `// [DEBUG]` logs at entry/exit of suspect functions
- [ ] Confirm the root cause (not just the symptom)

### Phase 2: Solve
- [ ] Write the fix targeting root cause (not symptom masking)
- [ ] Verify the fix does not break adjacent code
- [ ] Run mental test: does the happy path still work after the fix?
- [ ] Confirm the specific error no longer triggers

### Phase 3: Clean
- [ ] Remove ALL `// [DEBUG]` logs
- [ ] Verify no other debug artifacts remain
- [ ] Write FAILURES.md entry with root cause and prevention
- [ ] Deliver clean code

---

## Workflow 3: Code Review

```
TRIGGER: Review request, PR check, quality audit
DURATION: 10-15 minutes
OUTPUT: Graded review with specific violations and corrected code
```

### Step 1: Structure Review
- [ ] File naming matches CODING_STANDARDS.md conventions
- [ ] File lives in the correct directory per ARCHITECTURE.md
- [ ] Imports are ordered correctly (Node built-ins → third-party → local)

### Step 2: Code Quality Review
- [ ] Every async function has try/catch
- [ ] Every response has `return` before it
- [ ] No `res.json()` or raw status calls — only ApiResponse/sendError
- [ ] No `process.env.X` outside constants.js
- [ ] All database reads have `{ isDeleted: false }` + `.lean()`
- [ ] No hardcoded strings for error codes, response codes, or roles

### Step 3: Security Review
- [ ] All auth-required routes have the full middleware chain
- [ ] Input validation present on all POST/PATCH/PUT endpoints
- [ ] No sensitive data (passwords, tokens) in responses
- [ ] No stack traces in production error responses

### Step 4: Deliver Review
- Compliance score (0-100%)
- Violations list (Critical | High | Medium)
- Corrected code for each violation
- Approve / Revisions Required / Reject

---

## Workflow 4: Database Migration / Schema Change

```
TRIGGER: Adding/changing/removing a field from a model
DURATION: 15-30 minutes
OUTPUT: Updated model + migration plan + rollback strategy
```

### Step 1: Impact Analysis
- [ ] Which collections are affected?
- [ ] Which API endpoints use these fields?
- [ ] Which frontend components display or send these fields?
- [ ] Is this a breaking change (removing a required field)?

### Step 2: Write Migration
- [ ] New fields: add with safe defaults (never `required: true` on first migration)
- [ ] Renamed fields: add new field, migrate data, remove old field in 3 separate deployments
- [ ] Removed fields: mark deprecated first, remove in next deployment

### Step 3: Update Dependent Code
- [ ] Update Mongoose model
- [ ] Update validators that reference this field
- [ ] Update controllers that send/receive this field
- [ ] Update API.md documentation
- [ ] Update frontend slices and components that use this field

### Step 4: Test
- [ ] Create a document with old schema — does the API still work?
- [ ] Create a document with new schema — does the API work correctly?
- [ ] Run existing tests — no regression

---

## Workflow 5: New AI Agent Setup

```
TRIGGER: Starting a new AI coding session or onboarding a new AI tool
DURATION: 5 minutes
OUTPUT: AI agent fully loaded with workspace context
```

### Boot Sequence
```
1. Load AGENT_RULES.md      → Apply immutable rules
2. Load CONSTRAINTS.md      → Apply hard limits
3. Load PERSONA.md          → Adopt communication style
4. Load MEMORY.md           → Recall established patterns
5. Load EXECUTION_MEMORY.md → Restore last session state
6. Load OBJECTIVE.md        → Confirm current goals
7. Load TASKS.md            → Identify active work items
8. Load CONTEXT.md          → Set task-specific context
9. Identify applicable skill → Load skill's SKILL.md
10. Execute task             → Work within all loaded rules
```

### Post-Session Closure
```
1. Update EXECUTION_MEMORY.md → current state for next session
2. Write DECISIONS.md         → any architectural decisions made
3. Write FAILURES.md          → any bugs found and fixed
4. Write LEARNINGS.md         → any new patterns discovered
5. Write SESSION.md           → session activity log entry
```

---

## Workflow 6: Deployment

```
TRIGGER: Feature complete, ready to push to staging/production
DURATION: 30-60 minutes
OUTPUT: Running application in target environment
```

### Pre-Deploy
- [ ] All tests passing: `npm test`
- [ ] No lint errors: `npm run lint`
- [ ] No debug logs: `grep -r "// \[DEBUG\]" src/`
- [ ] No hardcoded secrets: manual audit
- [ ] CHECKLIST.md pre-deployment section complete
- [ ] DEPLOYMENT.md instructions reviewed

### Deploy
- [ ] Set environment variables in target environment
- [ ] Deploy backend (follow DEPLOYMENT.md for platform-specific steps)
- [ ] Deploy frontend build
- [ ] Verify health check endpoint responds: `GET /api/health` → 200

### Post-Deploy
- [ ] Login flow tested end-to-end
- [ ] Core feature tested manually
- [ ] No error spikes in MONITORING.md dashboards
- [ ] Response times within PERFORMANCE.md budgets
