# AI Custom Skills

A collection of AI skills for enhanced agentic capabilities. Each skill is a folder containing a `SKILL.md` instruction file and optional scripts/examples — designed to be copied **directly into your project** (not buried in `node_modules`).

## Quick Start

No installation needed. Use `npx` to run commands directly:

```bash
npx ai-custom-skills list
```

---

## Commands

### `list` — Browse all available skills

```bash
npx ai-custom-skills list
```

Lists all skills grouped by category with a short description.

---

### `info <skill-name>` — Inspect a skill

```bash
npx ai-custom-skills info mern-stack-project
```

Shows the full description, available scripts, examples, and resources for a specific skill.

---

### `install` — Install all skills into your project

```bash
npx ai-custom-skills install
```

Copies **all** skills as real folders into a `skills/` directory in your **current working directory**:

```
your-project/
└── skills/
    ├── mern-stack-project/
    │   └── SKILL.md
    ├── debug-reactjs-error/
    │   ├── SKILL.md
    │   └── scripts/
    └── ...
```

---

### `install <skill-name>` — Install a specific skill

```bash
npx ai-custom-skills install debug-reactjs-error
npx ai-custom-skills install mern-stack-project
npx ai-custom-skills install skill-creator
```

Copies the specified skill folder into `./skills/` in your current directory, plus any skills it depends on (for example, `install mern-stack-project` also installs `backend-expressjs` and `frontend-reactjs`).

---

### `install --all` — Install all skills (explicit)

```bash
npx ai-custom-skills install --all
```

Same as `install` with no arguments.

---

### `help` — Show help

```bash
npx ai-custom-skills help
```

---

## Available Skills

| Skill | Category | What it does |
|---|---|---|
| `mern-stack-project` | Development | Plan and review a full MERN project across both layers |
| `frontend-reactjs` | Development | React + Redux Toolkit frontend conventions and templates |
| `backend-expressjs` | Development | Production Express/Node API conventions and templates |
| `sailsjs-api` | Development | Full Sails.js API endpoint: action, helper, validation, route, policy |
| `sailsjs-helper` | Development | Reusable Sails.js helper with Redis-first and error-log patterns |
| `python-project-setup` | Development | Modern Python project: uv, ruff, pytest, mypy, CI (verified scaffold) |
| `skill-creator` | Development | Create, test and optimise new skills |
| `debug-reactjs-error` | Debugging | Reproduce, trace, fix and clean up React bugs |
| `debug-expressjs-error` | Debugging | Reproduce, trace, fix and clean up Express bugs |
| `debug-mern-stack-error` | Debugging | Trace a bug across React, Express and MongoDB |
| `debug-sailsjs-error` | Debugging | Debug Sails.js actions, helpers, policies and Waterline |
| `prompt-writing` | Productivity | Write, test and improve LLM prompts |
| `agent-workflow-creator` | Productivity | Design and validate AI agent workflows (YAML, Mermaid) |
| `ai-workflow-builder` | Productivity | Run a workflow spec as tested Python, or map it to n8n/Make |
| `qa-test-strategy` | QA | Risk-based test plans, test design, bug reports, release checks |
| `playwright-e2e-testing` | QA | Playwright e2e setup, stable tests, CI and flaky-test triage |
| `remotion-video-creator` | Content | Make MP4 videos from a storyboard with React and Remotion |
| `freelance-proposal-writer` | Freelance | Screen job posts and write tailored proposals |
| `freelance-client-onboarding` | Freelance | Scope of work, intake, kickoff and change requests |
| `freelance-invoicing-followups` | Freelance | Invoices with exact math and payment reminders |

Skills that depend on others (`mern-stack-project` needs `backend-expressjs` and `frontend-reactjs`; `ai-workflow-builder` needs `agent-workflow-creator`) list them under `requires` in `skills.json`, and `install <skill>` copies the dependencies too.

### Highlights

- **Verified scaffolds.** `python-project-setup`, `playwright-e2e-testing`, `remotion-video-creator` and `ai-workflow-builder` generate projects that were installed, type-checked or linted, and run (tests passing, a real MP4 rendered) before being published.
- **Safer debugging.** The `debug-*` skills tag temporary logs with `// [DEBUG]`, and their `cleanup_logs.py` removes only tagged debug statements (never real code) with `--dry-run` and `--check` modes.
- **Freelance toolkit.** Screen job posts and write proposals (`freelance-proposal-writer`), onboard and scope clients (`freelance-client-onboarding`), and invoice and chase payments (`freelance-invoicing-followups`). Drafts are for a human to review and send; nothing is auto-submitted.

---

## Skill Structure

Each skill folder follows this layout (only `SKILL.md` is required):

```
skills/
└── <skill-name>/
    ├── SKILL.md          # Frontmatter (name, description) + core instructions, under 500 lines
    ├── references/       # Detail loaded only when needed (one level deep from SKILL.md)
    ├── scripts/          # Helper scripts (Python/JS) the skill runs
    ├── assets/           # Templates and files used in the output
    └── evals/            # Optional test prompts with expected behaviour
```

---

## Adding a New Skill

1. Create a new folder under `skills/` named in lowercase-with-hyphens (it must equal the `name` in the frontmatter, and must not contain "claude" or "anthropic").
2. Write `SKILL.md`: a `description` of at most 1024 characters that says what the skill does and when to use it, then the instructions. Keep the body under 500 lines and move detail into `references/`.
3. Add an entry to `skills.json` with `name`, `category`, a one-line `summary` (under 90 characters) and, if needed, `requires`.
4. Run `npm run sync` to copy the description into `skills.json`, then `npm run validate`. It checks frontmatter, naming, length limits, that every referenced path exists, and that the manifest matches the folders.
5. Test any scripts you add. Prefer standard-library-only scripts and state any dependency in the `SKILL.md`.

---

## License

MIT © Ravi Patel
