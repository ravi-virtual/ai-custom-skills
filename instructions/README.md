# README.md — AI Operating System Navigation Guide

## What Is This System?

This directory (your **`AI_OS_DIR`**) is a **portable, production-grade AI Operating System** — a markdown-based framework that governs how AI agents (Claude, Gemini, ChatGPT, Cursor, etc.) think, plan, execute, and remember when working on *any* project.

Think of it as a self-contained engineering handbook that travels with you. Drop it into any project root (or point your AI tool to it from a shared path), and every agent instantly inherits consistent behavior, production-quality standards, and institutional memory.

> **Portability**: There are no absolute paths hardcoded in this system. `AI_OS_DIR` is simply wherever this directory lives. See the **Setup for a New System** section below.

---

## Quick Start

### For AI Agents
**Load these files first, in this order:**
1. `AGENT_RULES.md` — Immutable rules (highest authority)
2. `CONSTRAINTS.md` — Hard operational limits
3. `MEMORY.md` — Established patterns and decisions
4. `EXECUTION_MEMORY.md` — Last session state
5. `OBJECTIVE.md` — Current goals
6. `TASKS.md` — Current work items

Then load task-specific files as needed (see CONTEXT.md for the full loading guide).

### For Humans
This system encodes your engineering standards so AI never deviates from them. Key files to understand:
- `RULES.md` — What AI follows in this workspace
- `CODING_STANDARDS.md` — Code quality standards
- `ARCHITECTURE.md` — System design decisions

---

## File Index

### 🤖 AI Instructions (Load Per AI Tool)
| File | Purpose |
|------|---------|
| `CLAUDE.md` | Operating instructions for Claude AI |
| `GEMINI.md` | Operating instructions for Gemini AI |
| `CHATGPT.md` | Operating instructions for ChatGPT/GPT-4 |
| `CURSOR.md` | Operating instructions for Cursor IDE |
| `SYSTEM_PROMPT.md` | Master system prompt (copy-paste for any AI) |

### 🧠 Behavioral Rules
| File | Priority | Purpose |
|------|---------|---------|
| `AGENT_RULES.md` | HIGHEST | Immutable behavioral constraints |
| `CONSTRAINTS.md` | HIGH | Hard operational limits |
| `RULES.md` | MEDIUM | Operational policies |
| `PERSONA.md` | SUPPORT | AI communication style |

### 💾 Memory System
| File | Purpose |
|------|---------|
| `MEMORY.md` | Persistent patterns, decisions, tech choices |
| `MEMORY_RULES.md` | Rules for managing memory files |
| `EXECUTION_MEMORY.md` | Current session state (updated continuously) |
| `VECTOR_MEMORY.md` | Semantic retrieval architecture |
| `RETRIEVAL.md` | Knowledge retrieval decision tree |

### 🏗️ Engineering Reference
| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | System architecture diagrams and decisions |
| `STACK.md` | Technology stack with version references |
| `BACKEND.md` | Express/Node.js patterns with code examples |
| `FRONTEND.md` | React/Redux patterns with code examples |
| `DATABASE.md` | MongoDB/Mongoose patterns |
| `API.md` | API endpoint documentation |
| `CODING_STANDARDS.md` | Naming, formatting, quality standards |
| `SECURITY.md` | Security engineering standards |
| `PERFORMANCE.md` | Performance budgets and optimization |
| `EXAMPLES.md` | Complete working code examples |

### 🤖 Agent System
| File | Purpose |
|------|---------|
| `AGENT.md` | Agent types and operating model |
| `AI_WORKFLOW.md` | Workflow definitions for common tasks |
| `MULTI_AGENT.md` | Multi-agent coordination protocols |
| `TOOLS.md` | Tool usage reference |
| `PROMPTS.md` | Reusable prompt library (CO-STAR format) |

### 📋 Project Management
| File | Purpose |
|------|---------|
| `OBJECTIVE.md` | Mission, goals, success metrics |
| `PLANNING.md` | Feature planning framework |
| `TASKS.md` | Active and backlog task list |
| `CONTEXT.md` | Session context management |

### 📚 Knowledge Management
| File | Purpose |
|------|---------|
| `DECISIONS.md` | Architectural decision records (ADRs) |
| `FAILURES.md` | Bug reports with root cause analysis |
| `LEARNINGS.md` | Discovered patterns and optimizations |
| `KNOWLEDGE_BASE.md` | Verified domain facts |
| `TERMINOLOGY.md` | Standardized definitions |

### 🔧 Operations
| File | Purpose |
|------|---------|
| `DEBUGGING.md` | Trace-Solve-Clean debugging protocol |
| `TESTING.md` | Testing strategy and standards |
| `DEPLOYMENT.md` | Deployment guide (dev → staging → prod) |
| `CI_CD.md` | CI/CD pipeline reference |
| `DEVOPS.md` | Server operations and maintenance |
| `MONITORING.md` | Observability and alerting |

### 📊 Improvement System
| File | Purpose |
|------|---------|
| `SELF_IMPROVEMENT.md` | Self-assessment and improvement plan |
| `REFLECTION.md` | Periodic retrospective |
| `SESSION.md` | Session activity log |

---

## System Boot Sequence

When starting a new AI session with this project:

```
1. Load AGENT_RULES.md         → Understand immutable rules
2. Load CONSTRAINTS.md         → Understand hard limits
3. Load PERSONA.md             → Adopt correct identity
4. Load MEMORY.md              → Recall established patterns
5. Load EXECUTION_MEMORY.md   → Restore last session state
6. Load OBJECTIVE.md           → Confirm current goals
7. Load TASKS.md               → Identify active work
8. Load CONTEXT.md             → Set task-specific context
9. Load skill files            → Apply relevant skill patterns
10. Execute                    → Work autonomously within rules
```

---

## Setup for a New System

This AI-OS is **completely portable**. No code changes are needed to use it in a new project or on a new machine.

### Step 1: Place the directory
Copy (or symlink) this entire directory to your desired location. Common patterns:

| Pattern | Path example |
|---------|--------------|
| Shared across all projects | `C:\ai-os\` or `~/ai-os/` |
| Per-project (in root) | `my-project/ai-os/` |
| Per-project (hidden) | `my-project/.ai/` |

### Step 2: Update AI agent context
Tell your AI tool where to find the files. The exact method depends on your tool:

| AI Tool | How to configure |
|---------|-----------------|
| **Cursor** | Add to `.cursorrules`: `Load operating context from [your path]` |
| **Gemini / Antigravity** | Paste the load sequence into your workspace rules or system prompt |
| **Claude / ChatGPT** | Reference files in your custom instructions or project context |
| **GitHub Copilot** | Add to `.github/copilot-instructions.md` |

### Step 3: Update CONTEXT.md with system-specific paths
Open `CONTEXT.md` and set the two path variables at the top:

```
AI_OS_DIR   = [absolute path to this directory]
SKILLS_DIR  = [absolute path to your AI custom skills, if any]
```

That's it — no other files need editing. All other references are relative to `AI_OS_DIR`.

---



```
Every session:
  New bugs discovered → FAILURES.md
  New patterns found  → LEARNINGS.md
  Key decisions made  → DECISIONS.md
  Facts verified      → KNOWLEDGE_BASE.md
  Session completed   → EXECUTION_MEMORY.md + SESSION.md

Every few sessions:
  Patterns reviewed   → SELF_IMPROVEMENT.md
  Retrospective       → REFLECTION.md

Resulting in:
  Better code quality → CODING_STANDARDS.md improvements
  Fewer repeated bugs → FAILURES.md prevents re-investigation
  Faster development  → MEMORY.md patterns reduce decision-making time
```

---

## Key Conventions (Quick Reference)

| Convention | Rule |
|---|---|
| Response format | Always ApiResponse (success) or sendError (error) |
| Middleware chain | hasToken → isAuthenticated → role → validator → controller |
| Database reads | Always `{ isDeleted: false }` + `.lean()` |
| IDs | UUID strings, never MongoDB ObjectId |
| Env vars | Only in `src/config/constants.js` |
| Frontend state | Redux Toolkit only (no Context API for shared data) |
| API calls | Only through `axiosInstance` |
| Debug logs | `// [DEBUG]` prefix + remove before delivery |
| File naming | Controllers/Models = PascalCase; routes/middleware = camelCase |
