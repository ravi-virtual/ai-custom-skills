# MULTI_AGENT.md — Multi-Agent Coordination Protocols

## Overview
This file defines how multiple AI agents coordinate in this system — how tasks are distributed, how agents communicate, how conflicts are resolved, and how outputs are merged into coherent deliverables.

---

## Agent Roster

| Agent ID | Name | Specialization | Authority Level |
|---|---|---|---|
| ORCH-01 | Orchestrator | Planning, delegation, synthesis | High |
| DEV-01 | MERN Developer | Express + React implementation | Medium |
| DBG-01 | Debugger | Error tracing, root cause analysis | Medium |
| QA-01 | QA Validator | Testing, verification | Low |
| WF-01 | Workflow Designer | Agent workflow design, YAML specs | Low |
| PE-01 | Prompt Engineer | Prompt creation and optimization | Low |
| RSC-01 | Researcher | Information gathering, documentation | Low |

---

## Coordination Models

### Model 1: Supervisor-Worker (Most Common)
```
ORCH-01 receives task
    ↓
Decomposes into subtasks
    ↓
Assigns each to specialist agent
    ├── DEV-01: Backend implementation
    ├── DEV-01: Frontend implementation
    └── QA-01: Validation
    ↓
Collects outputs from all workers
    ↓
Validates consistency across outputs
    ↓
Delivers unified result
```

**Use when**: Task spans multiple specializations

### Model 2: Sequential Pipeline
```
ORCH-01 → DEV-01 → QA-01 → RSC-01 → Delivery
```
Each agent processes the output of the previous one.

**Use when**: Strict dependency ordering (can't test before implementing)

### Model 3: Parallel Execution
```
ORCH-01 assigns:
├── DEV-01 → Backend API (files: controllers/, routes/)
├── DEV-01 → Frontend slice (files: store/slices/)
└── RSC-01 → Documentation (files: API.md)
```
All agents work simultaneously on non-overlapping files.

**Use when**: Tasks are independent with no shared state

---

## File Access Protocol

### Preventing Write Conflicts
Before any parallel execution, the Orchestrator assigns exclusive write access:

```yaml
task_assignment:
  id: TASK-010
  parallel_tasks:
    - agent: DEV-01
      task: "Implement user update controller"
      exclusive_write_access:
        - backend/src/controllers/UserController.js
        - backend/src/validators/userValidator.js
        
    - agent: DEV-01 (instance 2)
      task: "Implement user update Redux slice"
      exclusive_write_access:
        - frontend/src/store/slices/userSlice.js
        - frontend/src/api/userApi.js
        
    - agent: RSC-01
      task: "Document user update API"
      exclusive_write_access:
        - API.md
```

No two agents may have write access to the same file simultaneously.

---

## Agent Handoff Protocol

### Task Handoff Package
When ORCH-01 hands a task to a specialist:
```yaml
handoff:
  from: ORCH-01
  to: DEV-01
  task_id: TASK-010
  description: "Implement PATCH /api/users/:id endpoint"
  
  context_required:
    - AGENT_RULES.md
    - ARCHITECTURE.md
    - BACKEND.md
    - CODING_STANDARDS.md
  
  inputs:
    - name: user_update_spec
      description: "User can update their name only (not email/role)"
      type: specification
    - name: existing_user_model
      file: backend/src/models/User.js
  
  outputs_expected:
    - name: updated_controller
      file: backend/src/controllers/UserController.js
      changes: "Add updateUser method"
    - name: updated_routes
      file: backend/src/routes/userRoutes.js
      changes: "Add PATCH /:id route"
    - name: new_validator
      file: backend/src/validators/userValidator.js
      changes: "Add updateUserRules"
  
  constraints:
    - Follow CODING_STANDARDS.md exactly
    - Follow backend-expressjs skill patterns
    - No raw res.json() calls
    - All async functions must have try/catch
  
  definition_of_done:
    - All specified files created/updated
    - Mental test performed (happy path + 401 + 403 + 404 + 422)
    - No debug logs
    - Checklist in CODING_STANDARDS.md verified
```

### Output Report (Specialist → Orchestrator)
```yaml
output_report:
  from: DEV-01
  to: ORCH-01
  task_id: TASK-010
  status: success  # success | partial | failed
  
  files_modified:
    - file: backend/src/controllers/UserController.js
      changes: "Added updateUser method with full validation and error handling"
    - file: backend/src/routes/userRoutes.js
      changes: "Added PATCH /:id route with full middleware chain"
    - file: backend/src/validators/userValidator.js
      changes: "Added updateUserRules array with name validation"
  
  decisions_made:
    - "Used PATCH instead of PUT because partial update is intended"
    - "Only allowed name update; email/role changes require admin endpoint"
  
  confidence: 95%
  
  issues_encountered: []
  
  next_steps:
    - "QA-01 should verify the happy path and error paths"
    - "Frontend slice update needed to use this endpoint"
```

---

## Conflict Resolution Protocol

### File Conflict
If two agents attempt to write to the same file:
1. Second agent's write is blocked immediately
2. ORCH-01 is notified
3. ORCH-01 resolves by: serializing the writes with clear dependency ordering
4. Never allow merge of two AI outputs without human review for non-trivial conflicts

### Decision Conflict
If two agents reach conflicting architectural decisions:
1. Both document their reasoning in DECISIONS.md (marked `[CONFLICT - PENDING RESOLUTION]`)
2. ORCH-01 reviews both and selects one
3. If ORCH-01 cannot resolve: escalate to human
4. Human decision becomes the final decision and is marked `Active`

### Context Conflict
If agents operate with different versions of the same context file:
1. ORCH-01 establishes a "context snapshot" at task start
2. All agents receive the same snapshot
3. No agent updates shared context files during parallel execution
4. Context files are updated only by ORCH-01 after all agents complete

---

## Communication Patterns

### Agent-to-Orchestrator (Async)
Agents report back to ORCH-01 via structured output reports (see above).
ORCH-01 polls for completion before proceeding to the next phase.

### Orchestrator-to-Agent (Sync)
ORCH-01 sends handoff packages synchronously at task assignment time.

### Agent-to-Agent (Via Orchestrator)
Agents do NOT communicate directly. All inter-agent communication goes through ORCH-01.
This prevents race conditions and maintains clear accountability.

---

## Multi-Agent Quality Assurance

### Mandatory QA Pass
Before ORCH-01 delivers any output from a multi-agent task:
1. QA-01 reviews all generated files against CODING_STANDARDS.md
2. QA-01 performs mental testing on all API endpoints
3. ORCH-01 verifies consistency across backend and frontend (naming, types, error codes)
4. ORCH-01 confirms all DECISIONS.md entries are written for this task

### Cross-Agent Consistency Checks
| Check | Description |
|---|---|
| API contract | Backend route URL matches frontend API function URL |
| Response shape | Backend response shape matches what frontend thunk expects |
| Error codes | Frontend handles the exact error codes backend can return |
| Field names | DB field names match what frontend sends in request body |
| Types | Data types match (Boolean not string, UUID not number) |
