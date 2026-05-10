# CONTEXT.md — Session Context Management

## Purpose

This file captures the current operational context — what environment we're in, what project state looks like, and what the AI needs to know to be immediately productive in any session.

## ⚙️ System-Specific Paths (Update This Section Per Machine / Project)

> These are the **only values** you need to change when moving this AI-OS to a new system.  
> All other files are fully portable — no absolute paths elsewhere.

```
AI_OS_DIR  = [absolute path to this directory, e.g. /path/to/ai-md-files]
SKILLS_DIR = [absolute path to AI custom skills, e.g. /path/to/ai-custom-skills/skills — leave blank if none]
```

---

## Current Project Context

### Project Details

**Status**: Active Development

**Stack**: MongoDB + Express.js + React + Node.js  
**Auth**: JWT (access: 15m, refresh: 15m)  
**Deployment Target**: Production cloud environment  
**Team**: AI-assisted development with human oversight

### Active Sprint Focus

Define the current sprint focus here (update each sprint):

```
Sprint Goal: [What are we trying to accomplish this sprint?]
Key Features: [List of features in scope]
Key Fixes: [List of bugs to resolve]
Definition of Done: [How we know a task is complete]
```

### Current Codebase State

```
Backend:
  - Framework: Express.js
  - Database: MongoDB with Mongoose
  - Auth: JWT middleware (hasToken, isAuthenticated, isAdmin, isUser)
  - Validation: express-validator
  - Models: UUID-based with soft delete
  - Response pattern: ApiResponse / sendError utilities

Frontend:
  - Framework: React (Vite)
  - State: Redux Toolkit
  - HTTP: Axios with configured instance + interceptors
  - Routing: React Router v6
  - Styling: Vanilla CSS
```

## Context Loading Rules

### Global Context (Always Load)

These files provide context that applies to every task:

```
AGENT_RULES.md   → Immutable behavioral rules
CONSTRAINTS.md   → Hard operational limits
PERSONA.md       → Communication style and expertise
MEMORY.md        → Established patterns and decisions
STACK.md         → Technology stack reference
```

### Task-Specific Context (Load per Task)

Based on task type, additionally load:

| Task Type            | Additional Context Files                          |
| -------------------- | ------------------------------------------------- |
| New backend feature  | ARCHITECTURE.md, BACKEND.md, CODING_STANDARDS.md  |
| New frontend feature | ARCHITECTURE.md, FRONTEND.md, CODING_STANDARDS.md |
| Bug fix              | FAILURES.md, DEBUGGING.md, target component files |
| API design           | API.md, BACKEND.md, SECURITY.md                   |
| Database change      | DATABASE.md, BACKEND.md, TESTING.md               |
| Deployment           | DEPLOYMENT.md, DEVOPS.md, CI_CD.md                |
| Performance          | PERFORMANCE.md, MONITORING.md, STACK.md           |
| Security review      | SECURITY.md, AGENT_RULES.md                       |

### Context Override Rules

Later-loaded context can override earlier context EXCEPT:

- AGENT_RULES.md is never overridden
- CONSTRAINTS.md is never overridden
- Explicit human instructions override all file-based context

## Runtime Context Injection

### Dynamic Context Variables

These values are injected at runtime and should be treated as live state:

```yaml
runtime:
  current_user_role: [admin | developer | reviewer]
  environment: [development | staging | production]
  current_task_id: [TASK-XXX]
  session_start: [ISO timestamp]
  files_modified_this_session: []
  decisions_made_this_session: []
  last_checkpoint: [ISO timestamp]
```

### Context Persistence

At session end, write these runtime values to EXECUTION_MEMORY.md:

- Current task state and next steps
- Files modified (and their current state)
- Decisions made this session
- Any blocking issues encountered

## Context Compression Strategy

### When Context Is Large

1. **Prioritize recent decisions** over older ones from DECISIONS.md
2. **Summarize completed sections** rather than keeping full text
3. **Extract only relevant rules** from RULES.md for current task type
4. **Use section anchors** to reference parts of files without loading the whole file

### Compression Priority (Compress First = Least Important)

```
Lowest Priority (compress first):
- Old LEARNINGS.md entries (keep only last 5)
- EXAMPLES.md (reference by name, don't load)
- Historical FAILURES.md (keep only recent similar failures)

Medium Priority:
- DECISIONS.md (keep recent decisions + decisions relevant to current task)
- KNOWLEDGE_BASE.md (load only relevant sections)

Highest Priority (never compress):
- AGENT_RULES.md
- CONSTRAINTS.md
- Current task from TASKS.md
- EXECUTION_MEMORY.md (current session state)
```

## Context Validation Checklist

Before starting any task, verify:

- [ ] AGENT_RULES.md loaded and active
- [ ] Current task is clearly identified in TASKS.md
- [ ] Environment (dev/staging/prod) is known
- [ ] Required files for this task type are loaded
- [ ] Last session state from EXECUTION_MEMORY.md is reviewed
- [ ] No contradictions between loaded context files
