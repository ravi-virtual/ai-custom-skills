# MEMORY_RULES.md — Memory Management Rules & Protocols

## Core Memory Principles

### Principle 1: Memory is the AI's Long-Term State
Without memory, every session starts from zero. Memory files bridge sessions, preserve decisions, and prevent re-learning the same lessons. Memory is not optional — it is a core system component.

### Principle 2: Memory is Append-Only for History
- Decisions, failures, and learnings are never deleted
- Mark obsolete entries as `[DEPRECATED]` with a reason and date
- Historical records enable retrospective analysis and pattern recognition

### Principle 3: Memory Has Structure
Unstructured memory is unsearchable. Every memory file uses consistent schemas so agents can retrieve relevant context efficiently.

---

## Memory File Taxonomy

| File | Type | Contents | Update Frequency |
|------|------|----------|-----------------|
| MEMORY.md | Long-term | Decisions, patterns, tech choices, skill triggers | After every architectural decision |
| EXECUTION_MEMORY.md | Session | Current task state, in-progress work, next steps | Continuously during session |
| DECISIONS.md | Long-term | Detailed decision records with rationale | After every non-trivial decision |
| FAILURES.md | Long-term | Bug reports, root causes, fixes applied | After every bug fix |
| LEARNINGS.md | Long-term | Patterns discovered, optimizations found | After every session |
| KNOWLEDGE_BASE.md | Long-term | Verified domain facts, terminology, API behaviors | When new facts verified |
| SESSION.md | Short-term | Session metadata, start/end times, tasks worked | At session start and end |
| REFLECTION.md | Long-term | Periodic self-assessment of agent quality | Weekly / after major milestones |

---

## Memory Write Rules

### Writing to MEMORY.md
Write when:
- A new architectural decision is finalized
- A new coding pattern is established
- A new technology is chosen with a reason
- A gotcha or footgun is discovered

Format every entry:
```markdown
| ID | Description | Rationale | Date | Status |
```

### Writing to DECISIONS.md
Write when:
- A non-obvious implementation choice was made
- An alternative approach was explicitly rejected
- A tradeoff was accepted

Format:
```markdown
## Decision [ID]: [Title]
**Date**: YYYY-MM-DD
**Status**: Active | Deprecated | Superseded by [ID]
**Context**: [What situation prompted this decision]
**Decision**: [What was decided]
**Rationale**: [Why this was the right choice]
**Alternatives Rejected**: [What else was considered and why rejected]
**Consequences**: [Known tradeoffs or side effects]
```

### Writing to FAILURES.md
Write when:
- A bug is found and fixed
- A failed approach was tried before the correct one
- An unexpected error occurred in production

Format:
```markdown
## Failure [ID]: [Error Description]
**Date**: YYYY-MM-DD
**Environment**: development | staging | production
**Affected Component**: [file/module/endpoint]
**Error**: [Full error message or description]
**Root Cause**: [Exact reason the error occurred]
**Fix Applied**: [What was changed to resolve it]
**Prevention**: [How to avoid this in the future]
```

### Writing to LEARNINGS.md
Write when:
- A better pattern is discovered
- A performance improvement is found
- A workflow optimization is validated

Format:
```markdown
## Learning [ID]: [Title]
**Date**: YYYY-MM-DD
**Source**: [What session/task revealed this]
**Learning**: [The insight]
**Applied To**: [Where this has been implemented]
**Action Required**: [If the learning requires codebase changes]
```

### Writing to EXECUTION_MEMORY.md
Write continuously during sessions:
```markdown
## Current Session: [YYYY-MM-DD]

### Active Task
ID: [TASK-ID]
Description: [What is being worked on]
Status: [in-progress | blocked]
Last Step Completed: [What was done most recently]
Next Step: [Exactly what to do next]
Context Files Loaded: [List of files currently in context]
Decisions Made This Session: [Quick reference list]

### Pending Actions
- [ ] [Action 1]
- [ ] [Action 2]
```

---

## Memory Retrieval Protocol

### Session Start Sequence
```
1. Load AGENT_RULES.md → Apply immutable rules
2. Load CONSTRAINTS.md → Set hard limits
3. Load MEMORY.md → Restore long-term knowledge
4. Load EXECUTION_MEMORY.md → Restore session state (where did we leave off?)
5. Load DECISIONS.md → Review recent decisions for context
6. Load OBJECTIVE.md → Confirm current goals
7. Load TASKS.md → Identify current work items
8. Load CONTEXT.md → Get session-specific context
```

### Retrieval Priority for Specific Queries
| Query Type | Primary Source | Secondary Source |
|---|---|---|
| "How do we do X in this codebase?" | MEMORY.md (patterns) | CODING_STANDARDS.md |
| "What did we decide about Y?" | DECISIONS.md | MEMORY.md |
| "Why is Z broken?" | FAILURES.md | DEBUGGING.md |
| "What should I do next?" | EXECUTION_MEMORY.md | TASKS.md |
| "What are the rules for this?" | AGENT_RULES.md | RULES.md |
| "What is the architecture?" | ARCHITECTURE.md | MEMORY.md |
| "What technology are we using?" | STACK.md | MEMORY.md |

---

## Memory Compression Protocol
When memory files become large (>200 entries):
1. Archive entries older than 90 days to `archive/[filename]_[YYYY-MM].md`
2. Maintain a summary at the top of the active file
3. Keep the most recent 50 entries readily accessible
4. Ensure archived entries are still searchable

## Memory Conflict Resolution
When two memory sources conflict:
- AGENT_RULES.md always wins (immutable)
- CONSTRAINTS.md wins over all others except AGENT_RULES.md
- More recent entries override older entries within the same file
- Explicit human decisions override AI-generated decisions

## Memory Integrity Checks
At the start of each session, verify:
- [ ] EXECUTION_MEMORY.md reflects the actual last-known state
- [ ] No contradictions between MEMORY.md and DECISIONS.md
- [ ] TASKS.md statuses are accurate
- [ ] FAILURES.md entries have complete root cause analysis
