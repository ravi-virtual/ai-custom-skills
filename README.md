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

Copies only the specified skill folder into `./skills/` in your current directory.

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

| Skill | Category | Description |
|---|---|---|
| `mern-stack-project` | Development | Full MERN stack scaffolding & review |
| `frontend-reactjs` | Development | React frontend with Redux Toolkit |
| `backend-expressjs` | Development | Production-grade Express/Node.js backend |
| `sailsjs-api` | Development | Sails.js API endpoint creation |
| `sailsjs-helper` | Development | Sails.js reusable helper creation |
| `debug-reactjs-error` | Debugging | Diagnose & fix React frontend errors |
| `debug-expressjs-error` | Debugging | Diagnose & fix Express backend errors |
| `debug-mern-stack-error` | Debugging | Full-stack MERN debugging |
| `debug-sailsjs-error` | Debugging | Sails.js-specific debugging |
| `skill-creator` | Development | Create & optimize new AI skills |
| `prompt-writing` | Productivity | Write & refine high-quality AI prompts |
| `agent-workflow-creator` | Productivity | Design structured agent workflows |

---

## Skill Structure

Each skill folder follows this layout:

```
skills/
└── <skill-name>/
    ├── SKILL.md          # Core AI instructions for this skill
    ├── scripts/          # Helper scripts (Python/JS)
    ├── examples/         # Reference implementations
    └── resources/        # Additional templates & assets
```

---

## Adding a New Skill

1. Create a new folder under `skills/` with a unique name.
2. Add a `SKILL.md` file following the standard template.
3. Register it in `skills.json`.

---

## License

MIT © Ravi Patel
