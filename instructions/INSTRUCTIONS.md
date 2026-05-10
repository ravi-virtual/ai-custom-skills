# INSTRUCTIONS.md — Master Operating Instructions

## Purpose
This is the human-readable master guide for configuring and operating this AI Operating System. It explains what every file does, how to use the system, and how to maintain it over time.

---

## Quick Start: For Humans

### Step 1: Understand the File Hierarchy
```
AGENT_RULES.md     ← IMMUTABLE: AI must always follow these
CONSTRAINTS.md     ← IMMUTABLE: Hard limits, no exceptions
RULES.md           ← High priority: Operational policies
CODING_STANDARDS.md ← Medium: Code quality rules
Everything else    ← Reference: Context and knowledge
```

### Step 2: Load the System into Your AI Tool
See the **Integration Guide** for how to load these files into:
- Cursor, Windsurf, Cline (→ `.cursorrules` / `.windsurfrules` / `.clinerules`)
- GitHub Copilot (→ `.github/copilot-instructions.md`)
- Antigravity/Gemini (→ `GEMINI.md`)
- Claude, ChatGPT (→ System prompt / Custom Instructions)

### Step 3: Start Each Session Correctly
Tell your AI:
> "Load and follow: AGENT_RULES.md, CONSTRAINTS.md, CODING_STANDARDS.md, BACKEND.md, FRONTEND.md, SECURITY.md"

Or paste the contents of `SYSTEM_PROMPT.md` as the first message.

---

## Quick Start: For AI Agents

### Mandatory First Steps
```
1. Read AGENT_RULES.md  — these rules override everything else
2. Read CONSTRAINTS.md  — these are hard limits you cannot violate
3. Read MEMORY.md       — recall established patterns
4. Read EXECUTION_MEMORY.md — restore last session state
5. Identify the task type → load the correct skill from SKILL.md
```

### Task Execution Loop
```
OBSERVE: Gather all context. Read referenced files. Identify gaps.
ORIENT:  Match task to known patterns (MEMORY.md, KNOWLEDGE_BASE.md).
DECIDE:  Select approach. State confidence %. Document if architectural.
ACT:     Execute one change at a time. Validate each step.
REFLECT: Check against AGENT_RULES.md. Log in LEARNINGS.md.
```

### Session Closure (Every Session)
Before ending any session, update:
- `EXECUTION_MEMORY.md` → current state
- `SESSION.md` → what was done
- `DECISIONS.md` → architectural choices made
- `FAILURES.md` → any bugs fixed
- `LEARNINGS.md` → new patterns found

---

## File Ownership & Modification Rules

| File | Who Can Modify | How |
|---|---|---|
| `AGENT_RULES.md` | Human only | Direct edit |
| `CONSTRAINTS.md` | Human only | Direct edit |
| `RULES.md` | Human or AI (with approval) | Propose → Human approves |
| `CODING_STANDARDS.md` | Human or AI (with approval) | Propose → Human approves |
| `MEMORY.md` | AI (after verifying pattern) | Add entries, never delete |
| `DECISIONS.md` | AI (during task) | Append only |
| `FAILURES.md` | AI (after debugging) | Append only |
| `LEARNINGS.md` | AI (after session) | Append only |
| `KNOWLEDGE_BASE.md` | AI (after verification) | Append only |
| `EXECUTION_MEMORY.md` | AI (every session) | Overwrite current state |
| `TASKS.md` | Human or AI | Add, update, mark complete |
| All other files | Human or AI | Follow standard update process |

---

## System Configuration

### Changing the Tech Stack
If the project moves to a different stack:
1. Update `STACK.md` — new versions and tools
2. Update `ARCHITECTURE.md` — new system design
3. Update `BACKEND.md` or `FRONTEND.md` — new patterns
4. Update `MEMORY.md` — new patterns replace old ones
5. Update `AGENT_RULES.md` — if immutable rules need to change (human only)
6. Update `SYSTEM_PROMPT.md` — reflect new stack in the master prompt

### Adding a New AI Tool
1. Create a `TOOLNAME.md` file (e.g., `WINDSURF.md`)
2. Model it after `CURSOR.md` or `CLAUDE.md`
3. Add the tool to `README.md` file index
4. Add integration steps to the integration guide

### Adding a New Skill
1. Use the `skill-creator` skill
2. Place skill in `D:\programming\ai-custom-skills\skills\your-skill-name\`
3. Add skill to `SKILL.md` trigger table
4. Add skill to `MEMORY.md` Skill Trigger Memory table

---

## Maintenance Schedule

### Every Session
- Update `EXECUTION_MEMORY.md`
- Log session in `SESSION.md`
- Add any new bugs to `FAILURES.md`
- Add any new patterns to `LEARNINGS.md`

### Weekly
- Review `TASKS.md` — mark complete, add new
- Review `FAILURES.md` — are any bugs recurring? Fix the pattern.
- Review `SELF_IMPROVEMENT.md` — any improvement actions overdue?

### Monthly
- Write `REFLECTION.md` entry
- Review `DECISIONS.md` — are any decisions now outdated?
- Check `STACK.md` — any dependency updates needed?
- Archive old `FAILURES.md` entries (move to `FAILURES_ARCHIVE.md`)

### After Every Major Feature
- Update `ARCHITECTURE.md` if structure changed
- Update `API.md` with new endpoints
- Update `DATABASE.md` if schema changed
- Update `OBJECTIVE.md` if goals were met

---

## Troubleshooting the AI-OS

### AI is Ignoring the Rules
- Verify the AI tool has loaded `AGENT_RULES.md` (use verification question)
- Re-paste `SYSTEM_PROMPT.md` at the start of the conversation
- Check that the rules file is within the tool's context window

### AI is Producing Inconsistent Code
- Check `MEMORY.md` — the pattern may not be documented there yet
- Verify the correct skill is being activated (see `SKILL.md` trigger table)
- Add the specific pattern to `MEMORY.md` Section 1

### AI is Making Destructive Changes
- Verify `CONSTRAINTS.md` is loaded
- Rule 10 of `CONSTRAINTS.md` explicitly prohibits autonomous destructive actions
- Escalate: human must explicitly confirm any destructive operation

### AI Memory Seems Empty
- Check `EXECUTION_MEMORY.md` — was the last session state saved?
- Re-load `MEMORY.md` and `KNOWLEDGE_BASE.md`
- Rebuild context by reading recent `SESSION.md` entries

---

## Glossary of Key Terms
See `TERMINOLOGY.md` for complete definitions of all terms used in this system.
