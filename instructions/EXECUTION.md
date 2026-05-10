# EXECUTION.md — Task Execution Framework

## Purpose
Defines how AI agents execute tasks — from receiving a request to delivering a verified output. Every task must pass through this framework.

---

## Execution Phases

### Phase 0: Pre-Execution Checks
Before touching any code, complete ALL of these:

```
□ AGENT_RULES.md loaded and understood
□ CONSTRAINTS.md hard limits identified for this task
□ Task scope clearly defined (what IS in scope, what is NOT)
□ Correct skill identified (see SKILL.md trigger table)
□ Confidence assessed: if < 60%, gather more context before proceeding
□ Destructive operations identified → get human confirmation first
```

---

### Phase 1: OBSERVE
*"What is the current state?"*

```
□ Read ALL referenced files before forming any hypothesis
□ Read the FULL file, not just the section you assume is relevant
□ Check MEMORY.md for established patterns on this topic
□ Check FAILURES.md for known bugs related to this area
□ Check KNOWLEDGE_BASE.md for verified facts about this technology
□ Identify: What exists? What is missing? What is broken?
□ State current understanding with confidence %
```

**Output**: A clear statement of the current state of the system.

---

### Phase 2: ORIENT
*"How does this fit into the larger system?"*

```
□ Map the task against ARCHITECTURE.md patterns
□ Identify all files that will need to change
□ Identify all files that COULD be affected (side effects)
□ Check API.md if this involves an endpoint change
□ Check DATABASE.md if this involves a schema change
□ Identify risk areas: authentication paths, data mutations, external services
```

**Output**: A list of files to change + files to verify + risk areas.

---

### Phase 3: DECIDE
*"What is the best approach?"*

```
□ Select implementation approach
□ Score alternatives (even briefly): why is this approach better than X?
□ If this is an architectural decision: write to DECISIONS.md
□ State confidence: [0-100]%
□ If confidence < 70%: state what information would raise confidence
□ If < 60%: STOP and gather more context before proceeding
```

**Output**: Chosen approach with rationale and confidence score.

---

### Phase 4: ACT
*"Execute precisely and atomically."*

```
□ One change at a time — do not batch unrelated changes
□ Complete each file fully before moving to the next
□ No placeholders, no TODOs, no truncated code
□ Apply skill patterns exactly (from SKILL.md and skill files)
□ After each file: do a quick mental test of that file in isolation
□ Track all files modified (for the final delivery summary)
```

**Atomic Change Rule**: Each change should be independently reversible. If you can't describe exactly what ONE change does, it's not atomic enough.

---

### Phase 5: REFLECT
*"Is this correct and complete?"*

#### Pre-Delivery Checklist
```
Code Quality:
□ Follows CODING_STANDARDS.md (naming, structure, formatting)
□ No raw res.json() — only ApiResponse/sendError
□ Every async function has try/catch
□ Every response has return before it
□ No process.env outside constants.js
□ All DB reads have { isDeleted: false } + .lean()
□ JSDoc on all controller methods

Security:
□ All auth-required routes have full middleware chain
□ Input validation on all mutating endpoints
□ No sensitive data in responses
□ No credentials or secrets in any file

Cleanliness:
□ No debug logs (// [DEBUG] removed)
□ No commented-out code blocks
□ No unused imports
□ No TODO or placeholder comments

Mental Test:
□ Happy path works
□ 401 Unauthorized returns correctly
□ 403 Forbidden returns correctly
□ 404 Not Found returns correctly
□ 422 Validation Error returns correctly
□ 500 Server Error is caught (not unhandled)
```

**Output**: Clean, verified code + files modified list.

---

## Execution Modes

### Mode 1: Single Task
For focused, well-defined tasks (add one endpoint, fix one bug):
- Execute all 5 phases for that single task
- Deliver in one response

### Mode 2: Multi-Task Sprint
For larger features spanning multiple files:
- Phase 0-3: Done once for the whole feature
- Phase 4: Execute file by file, delivering each as a group
- Phase 5: Final checklist on ALL files together

### Mode 3: Exploration
For tasks where requirements are unclear:
- Phase 0-1 only: Gather context, report findings
- Ask clarifying questions
- Do NOT proceed to Phase 4 until requirements are confirmed

---

## Execution Speed Guide

| Task Type | Expected Phase 4 Duration | Notes |
|---|---|---|
| Add one controller method | 5-10 min | Small scope |
| Add one full API endpoint | 15-20 min | Model + validator + controller + route |
| Add full MERN feature | 30-45 min | Backend + frontend + hook + component |
| Debug a reported bug | 10-20 min | Trace-Solve-Clean |
| Full code review | 10-15 min | All files in scope |

---

## Execution Anti-Patterns

### ❌ Never Do These

| Anti-Pattern | Why It Fails |
|---|---|
| Start coding before reading existing files | Creates inconsistencies with existing code |
| Skip Phase 0 checks for "simple" tasks | Simple tasks have caused the most bugs |
| Mix multiple unrelated changes in one Act | Makes rollback impossible |
| Leave `// TODO` comments | Unfinished work disguised as code |
| Guess at API signatures | Causes type errors and silent bugs |
| Skip the mental test | Broken code reaches the user |
| Leave debug logs in delivery | Leaks implementation details, performance cost |

---

## Execution Confidence Scale

| % | State | Action |
|---|---|---|
| 90-100 | High confidence | Execute directly |
| 70-89 | Moderate confidence | Note assumptions, proceed |
| 50-69 | Low confidence | State uncertainty, ask one clarifying question |
| < 50 | Very low | Stop, explain what context is needed, wait |
