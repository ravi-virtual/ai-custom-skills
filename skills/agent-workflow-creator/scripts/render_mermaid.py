#!/usr/bin/env python3
"""
render_mermaid.py — Convert a YAML workflow file to a Mermaid flowchart diagram.

Usage:
    python render_mermaid.py --file workflow.yaml [--output diagram.md] [--html]

Options:
    --file TEXT      Path to YAML workflow file (required)
    --output TEXT    Output file path (default: stdout)
    --html           Wrap in standalone HTML page with Mermaid.js rendering
    --theme TEXT     Mermaid theme: default | dark | forest | neutral (default: default)
"""

import argparse
import sys
from pathlib import Path


ROLE_COLORS = {
    "orchestrator": "#4A90D9",
    "supervisor": "#4A90D9",
    "researcher": "#7BC67E",
    "analyst": "#F5A623",
    "writer": "#9B59B6",
    "validator": "#E74C3C",
    "default": "#95A5A6",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title} — Workflow Diagram</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
         padding: 40px; background: #f8f9fa; }}
  h1 {{ color: #2c3e50; }}
  .mermaid {{ background: white; padding: 24px; border-radius: 8px; 
              box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .meta {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
</style>
</head>
<body>
<h1>🔄 {title}</h1>
<p class="meta">{description}</p>
<div class="mermaid">
{diagram}
</div>
<script>mermaid.initialize({{ startOnLoad: true, theme: '{theme}' }});</script>
</body>
</html>"""


def load_yaml(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML required: pip install pyyaml")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def get_node_shape(step: dict) -> tuple[str, str]:
    """Return (open, close) shape chars for a step."""
    tool = step.get("tool", "")
    if "branches" in step or step.get("condition"):
        return "{", "}"           # diamond
    if tool in ("file_write", "file_read", "database_read", "database_write"):
        return "[(", ")]"         # cylinder
    if tool == "human_input":
        return "[/", "/]"         # parallelogram
    if tool == "sub_workflow":
        return "((", "))"         # circle
    return "[", "]"               # rectangle


def sanitize_label(text: str) -> str:
    """Make text safe for Mermaid labels."""
    return text.replace('"', "'").replace('\n', ' ').replace('>', '&gt;').replace('<', '&lt;')


def workflow_to_mermaid(data: dict) -> str:
    wf = data.get("workflow", {})
    steps = wf.get("steps", [])
    workflow_type = wf.get("metadata", {}).get("type", "single-agent")
    is_multi = workflow_type == "multi-agent"

    lines = ["flowchart TD"]
    lines.append("")

    # ── Collect agent→role mapping ──────────────────────────────────────
    agents = {}
    for agent in wf.get("agents", []):
        agents[agent["id"]] = agent.get("name", agent["id"])

    # ── Start node ────────────────────────────────────────────────────────
    inputs = wf.get("inputs", [])
    input_labels = ", ".join(i["name"] for i in inputs) if inputs else "Input"
    lines.append(f'    START(["\U0001F7E2 Start: {sanitize_label(input_labels)}"])')

    # ── Step nodes ────────────────────────────────────────────────────────
    step_map = {s["id"]: s for s in steps}
    first_step = steps[0]["id"] if steps else None

    if first_step:
        lines.append(f"    START --> {first_step}")

    for step in steps:
        sid = step["id"]
        name = sanitize_label(step.get("name", sid))
        tool = step.get("tool", "")
        agent = step.get("agent", "")
        open_s, close_s = get_node_shape(step)

        # Node label with tool badge
        if tool:
            label = f'{name}<br/><small>{tool}</small>'
        else:
            label = name

        if agent and is_multi:
            agent_name = agents.get(agent, agent)
            label = f'{name}<br/><small>{agent_name} · {tool}</small>'

        lines.append(f'    {sid}{open_s}"{label}"{close_s}')

    lines.append("")

    # ── Edges ─────────────────────────────────────────────────────────────
    for step in steps:
        sid = step["id"]

        # on_success next
        on_success = step.get("on_success", {})
        nxt = on_success.get("next")
        if nxt:
            if isinstance(nxt, list):
                for n in nxt:
                    lines.append(f"    {sid} --> {n}")
            else:
                lines.append(f"    {sid} --> {nxt}")

        # branches
        for branch in step.get("branches", []):
            condition = sanitize_label(branch.get("condition", ""))
            nxt = branch.get("next")
            if nxt and condition:
                lines.append(f'    {sid} -->|"{condition}"| {nxt}')
            elif nxt:
                lines.append(f"    {sid} --> {nxt}")

        # on_failure fallback
        on_fail = step.get("on_failure", {})
        fallback = on_fail.get("fallback_step")
        if fallback:
            lines.append(f'    {sid} -.->|"on failure"| {fallback}')

    lines.append("")

    # ── End node ──────────────────────────────────────────────────────────
    outputs = wf.get("outputs", [])
    output_label = ", ".join(o["name"] for o in outputs) if outputs else "Output"
    lines.append(f'    END(["\U0001F534 End: {sanitize_label(output_label)}"])')

    # Connect terminal steps to END
    step_ids = {s["id"] for s in steps}
    referenced_ids = set()
    for step in steps:
        for nxt in [step.get("on_success", {}).get("next")] + [b.get("next") for b in step.get("branches", [])]:
            if nxt:
                if isinstance(nxt, list):
                    referenced_ids.update(nxt)
                else:
                    referenced_ids.add(nxt)

    terminal_ids = step_ids - referenced_ids
    for tid in terminal_ids:
        lines.append(f"    {tid} --> END")

    lines.append("")

    # ── Style by agent role (multi-agent) ──────────────────────────────────
    if is_multi and wf.get("agents"):
        lines.append("    %% Agent color coding")
        for agent in wf["agents"]:
            aid = agent["id"]
            color = ROLE_COLORS.get(aid, ROLE_COLORS["default"])
            agent_steps = [s["id"] for s in steps if s.get("agent") == aid]
            if agent_steps:
                steps_str = ",".join(agent_steps)
                lines.append(f"    classDef {aid}Style fill:{color},color:#fff,stroke:#333")
                for s in agent_steps:
                    lines.append(f"    class {s} {aid}Style")

    lines.append("    classDef terminal fill:#2ECC71,color:#fff,stroke:#27AE60,stroke-width:2px")
    lines.append("    class START,END terminal")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render a workflow YAML as a Mermaid diagram.")
    parser.add_argument("--file", required=True, help="YAML workflow file")
    parser.add_argument("--output", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--html", action="store_true", help="Wrap in standalone HTML")
    parser.add_argument("--theme", default="default",
                        choices=["default", "dark", "forest", "neutral"])
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    data = load_yaml(str(path))
    wf = data.get("workflow", {})
    diagram = workflow_to_mermaid(data)

    if args.html:
        output = HTML_TEMPLATE.format(
            title=wf.get("name", "Workflow"),
            description=wf.get("description", ""),
            diagram=diagram,
            theme=args.theme,
        )
        ext = ".html"
    else:
        output = f"```mermaid\n{diagram}\n```"
        ext = ".md"

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output)
        print(f"✅ Diagram written to: {out_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
