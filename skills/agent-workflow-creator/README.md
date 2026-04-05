# agent-workflow-creator

A comprehensive skill for designing, generating, and documenting complete agent workflows for any task or domain.

## What This Skill Does

Given any task description, this skill produces:

- **Plain-English Workflow Summary** — what it does, inputs, outputs
- **Step-by-Step Table** — every step with tool, input, output, and failure path
- **Mermaid Flowchart** — visual diagram of the workflow
- **Agent Roles Card** — who does what in multi-agent systems
- **Tool Manifest** — every tool and credential required
- **Error Handling Plan** — every failure class with recovery strategy
- **YAML Workflow Definition** — machine-readable spec for any agent framework
- **Execution Checklist** — pre-flight checks before running

## Directory Structure

```
agent-workflow-creator/
├── SKILL.md                          # Main skill instructions
├── evals/
│   └── evals.json                    # Test cases for the skill
├── references/
│   ├── step-schema.md                # Full step schema reference
│   ├── yaml-schema.md                # Full YAML workflow schema
│   ├── patterns.md                   # 9 workflow patterns with diagrams + YAML
│   ├── domains/
│   │   ├── research.md               # Research & knowledge domain guidance
│   │   ├── data-pipeline.md          # Data processing & ETL guidance
│   │   └── content.md                # Content creation domain guidance
│   └── examples/
│       ├── research-report-workflow.yaml
│       └── customer-support-triage.yaml
└── scripts/
    ├── generate_workflow.py          # Scaffold a YAML workflow from task description
    ├── validate_workflow.py          # Validate a YAML workflow against the schema
    ├── render_mermaid.py             # Convert YAML workflow to Mermaid diagram
    └── export_workflow.py            # Export workflow to multiple formats
```

## Scripts Quick Reference

### Generate a workflow

```bash
python scripts/generate_workflow.py \
  --task "monitor social media and alert on negative mentions" \
  --type single-agent \
  --pattern react \
  --domain research \
  --output my_workflow.yaml \
  --verbose
```

### Validate a workflow

```bash
python scripts/validate_workflow.py --file my_workflow.yaml --report
```

### Render a Mermaid diagram

```bash
# Output to Markdown (paste into any Mermaid viewer)
python scripts/render_mermaid.py --file my_workflow.yaml

# Output to standalone HTML
python scripts/render_mermaid.py --file my_workflow.yaml --html --output diagram.html
```

### Export to all formats

```bash
python scripts/export_workflow.py \
  --file my_workflow.yaml \
  --formats yaml,json,markdown,html,mermaid \
  --output-dir ./exports
```

## Supported Workflow Patterns

| Pattern           | Best For                             |
| ----------------- | ------------------------------------ |
| Sequential Chain  | Linear step-by-step tasks            |
| Map-Reduce        | Batch processing many items          |
| Fan-Out / Fan-In  | Parallel independent branches        |
| ReAct Loop        | Open-ended autonomous research       |
| Critic-Refine     | Quality-sensitive content generation |
| Human-in-the-Loop | Approval workflows                   |
| RAG               | Knowledge-base powered responses     |
| Supervisor-Worker | Complex multi-specialist tasks       |
| Event-Driven      | Webhook/trigger-based automation     |

## Requirements

- Python 3.8+
- `pyyaml` (for JSON export and YAML loading): `pip install pyyaml`

## Installation as Skill

Place this directory in your ai's skills folder. The ai will automatically detect and use it when you ask for workflow design, agent architecture, or automation planning help.
