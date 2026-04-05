# AI Skill Collection

A professional collection of AI skills for enhanced agentic capabilities. Each skill is designed to be easily discoverable and usable by any AI assistant or agent that supports the skill format.

## Installation

```bash
npm install @your-username/my-skills-collection
```

## CLI Usage

After installation, you can use the `custom-skills` command to interact with your collection:

### List all skills

```bash
npx custom-skills --list
```

### Get detailed information for a skill

```bash
npx custom-skills --info=default-skill
```

## Project Structure

This project follows the manifest-driven architecture used by professional AI skill stores:

- **`skills.json`**: The central manifest file for skill discovery.
- **`index.js`**: Lightweight CLI for skill management.
- **`skills/`**: Root directory for all individual skill folders.
  - **`<skill-name>/`**: 
    - **`SKILL.md`**: Core instructions for the AI agent for this specific skill.
    - **`scripts/`**: Executable scripts specific to this skill.
    - **`examples/`**: Usage guides and reference implementations.

## Adding a New Skill

1. Create a new folder under `skills/` with a unique name.
2. Add a `SKILL.md` file following the standard template.
3. Update `skills.json` with your new skill's details.

## License

MIT
