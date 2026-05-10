# SKILL.md — Skill System Reference

## What Is a Skill?
A skill is a specialized, pre-loaded instruction set that tells AI agents exactly how to handle a specific category of task. Skills eliminate guesswork and enforce consistency by providing:
- The exact folder structure to follow
- Code templates with zero ambiguity
- Validation checklists before delivery
- Error handling patterns specific to that domain

---

## Available Skills (This Workspace)

| Skill ID | File | Trigger Patterns |
|---|---|---|
| `backend-expressjs` | skills/backend-expressjs/SKILL.md | Add API, new route, controller, Express endpoint |
| `frontend-reactjs` | skills/frontend-reactjs/SKILL.md | React component, Redux slice, hook, Vite page |
| `mern-stack-project` | skills/mern-stack-project/SKILL.md | Scaffold MERN, new project, full setup |
| `agent-workflow-creator` | skills/agent-workflow-creator/SKILL.md | Design workflow, agent pipeline, automation |
| `debug-expressjs-error` | skills/debug-expressjs-error/SKILL.md | Express 500, middleware hang, async error |
| `debug-reactjs-error` | skills/debug-reactjs-error/SKILL.md | Hook violation, render loop, state bug |
| `debug-mern-stack-error` | skills/debug-mern-stack-error/SKILL.md | CORS, proxy, auth flow, full-stack bug |
| `debug-sailsjs-error` | skills/debug-sailsjs-error/SKILL.md | Waterline error, policy block, Sails crash |
| `sailsjs-api` | skills/sailsjs-api/SKILL.md | Sails API endpoint, controller action |
| `sailsjs-helper` | skills/sailsjs-helper/SKILL.md | Sails helper function |
| `prompt-writing` | skills/prompt-writing/SKILL.md | Write prompt, CO-STAR, improve prompt |
| `skill-creator` | skills/skill-creator/SKILL.md | Create skill, build skill, optimize skill |

---

## Skill Activation Protocol

### Step 1: Identify the Trigger
Before starting any task, match the user's intent against the trigger patterns above.

### Step 2: Read the SKILL.md
```
MANDATORY: Use view_file on the skill's SKILL.md before generating any code.
Never rely on memory of a skill — always re-read it.
```

### Step 3: Apply Patterns Exactly
- Follow folder structure as defined in the skill
- Use code templates from the skill, not from memory
- Apply the skill's validation checklist before delivery

### Step 4: Confirm Skill Used
In your response, note which skill was applied:
> "Applied: backend-expressjs skill patterns"

---

## Skill Trigger Decision Tree

```
User request received
    ↓
Does it involve Express/Node.js backend code?
    YES → backend-expressjs skill
    NO  ↓
Does it involve React/Redux frontend code?
    YES → frontend-reactjs skill
    NO  ↓
Does it involve both backend + frontend?
    YES → mern-stack-project skill
    NO  ↓
Does it involve debugging an error?
    Express error → debug-expressjs-error skill
    React error   → debug-reactjs-error skill
    Full-stack    → debug-mern-stack-error skill
    Sails error   → debug-sailsjs-error skill
    NO  ↓
Does it involve designing a workflow or agent system?
    YES → agent-workflow-creator skill
    NO  ↓
Does it involve writing or improving a prompt?
    YES → prompt-writing skill
    NO  ↓
Does it involve creating a new skill?
    YES → skill-creator skill
    NO  ↓
No skill applies → use general engineering judgment + CODING_STANDARDS.md
```

---

## How to Create a New Skill

Use the `skill-creator` skill. The structure for every skill:

```
skills/
└── your-skill-name/
    ├── SKILL.md          ← Required: instructions + YAML frontmatter
    ├── scripts/          ← Optional: helper scripts
    ├── examples/         ← Optional: reference implementations
    └── resources/        ← Optional: templates, assets
```

### SKILL.md Frontmatter
```yaml
---
name: skill-name
description: |
  One sentence: what the skill does.
  Two sentences: exact trigger conditions. Be specific enough to activate
  the skill reliably and narrow enough to not activate it incorrectly.
---
```

### SKILL.md Body Sections (Required)
1. **Overview** — What this skill handles
2. **Trigger Conditions** — Exhaustive list of when to use it
3. **Folder Structure** — Exact file layout
4. **Implementation Steps** — Numbered, atomic steps
5. **Code Templates** — Complete, working code (no placeholders)
6. **Validation Checklist** — Pre-delivery checks
7. **Common Mistakes** — What NOT to do

---

## Skill Quality Standards

A skill is production-ready when:
- [ ] Triggers are specific enough to avoid false activation
- [ ] Code templates are complete (no `// TODO` or `// ...`)
- [ ] Validation checklist has 8+ items
- [ ] At least one "Common Mistakes" entry exists
- [ ] Skill has been tested on 3+ real tasks before being marked stable

---

## Skill Maintenance

| Action | When |
|---|---|
| Update skill templates | When CODING_STANDARDS.md changes |
| Add new trigger patterns | When a new task type is repeatedly misrouted |
| Add Common Mistakes entry | After every bug caused by wrong pattern use |
| Archive a skill | When the technology it covers is removed from the stack |
