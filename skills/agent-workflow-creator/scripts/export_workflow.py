#!/usr/bin/env python3
"""
export_workflow.py — Export a workflow YAML to multiple formats.

Usage:
    python export_workflow.py --file workflow.yaml --formats yaml,json,markdown,html,mermaid

Options:
    --file TEXT        Path to YAML workflow file (required)
    --formats TEXT     Comma-separated list of formats: yaml,json,markdown,html,mermaid,all
    --output-dir TEXT  Output directory (default: same as input file)
    --verbose          Print details
"""

import argparse
import json
import sys
from pathlib import Path


def load_yaml(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML required: pip install pyyaml")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def to_json(data: dict) -> str:
    return json.dumps(data, indent=2)


def to_markdown(data: dict, source_yaml: str) -> str:
    wf = data.get("workflow", {})
    name = wf.get("name", "workflow")
    description = wf.get("description", "")
    steps = wf.get("steps", [])
    inputs = wf.get("inputs", [])
    outputs = wf.get("outputs", [])
    agents = wf.get("agents", [])
    metadata = wf.get("metadata", {})

    md_parts = [
        f"# Agent Workflow: {name}",
        "",
        f"> {description.strip()}",
        "",
        "## Metadata",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Type | {metadata.get('type', 'single-agent')} |",
        f"| Domain | {metadata.get('domain', '—')} |",
        f"| Estimated Duration | {metadata.get('estimated_duration', '—')} |",
        f"| Complexity | {metadata.get('complexity', '—')} |",
        "",
        "## Inputs",
    ]

    if inputs:
        md_parts += [
            "| Name | Type | Required | Description |",
            "|------|------|----------|-------------|",
        ]
        for inp in inputs:
            md_parts.append(
                f"| `{inp.get('name')}` | {inp.get('type', '—')} | "
                f"{'Yes' if inp.get('required') else 'No'} | {inp.get('description', '—')} |"
            )
    else:
        md_parts.append("_No inputs defined._")

    md_parts += ["", "## Outputs"]
    if outputs:
        md_parts += [
            "| Name | Type | Source | Description |",
            "|------|------|--------|-------------|",
        ]
        for out in outputs:
            md_parts.append(
                f"| `{out.get('name')}` | {out.get('type', '—')} | "
                f"`{out.get('from', '—')}` | {out.get('description', '—')} |"
            )
    else:
        md_parts.append("_No outputs defined._")

    if agents:
        md_parts += ["", "## Agent Roles",
                     "| ID | Name | Role |",
                     "|----|------|------|"]
        for agent in agents:
            md_parts.append(
                f"| `{agent.get('id')}` | {agent.get('name', '—')} | {agent.get('role', '—')} |"
            )

    md_parts += [
        "", "## Steps",
        "| # | Step ID | Name | Tool | Agent | On Failure |",
        "|---|---------|------|------|-------|------------|",
    ]

    for i, step in enumerate(steps, 1):
        fail = step.get("on_failure", {}).get("strategy", "—")
        agent = step.get("agent", "—")
        md_parts.append(
            f"| {i} | `{step.get('id')}` | {step.get('name', '—')} | "
            f"`{step.get('tool', '—')}` | {agent} | {fail} |"
        )

    md_parts += [
        "", "## Step Details", ""
    ]
    for step in steps:
        sid = step.get("id", "?")
        md_parts += [
            f"### {sid}: {step.get('name', '')}",
            "",
            step.get("description", "_No description._"),
            "",
            f"- **Tool:** `{step.get('tool', '—')}`",
        ]
        if step.get("agent"):
            md_parts.append(f"- **Agent:** {step['agent']}")
        if step.get("input"):
            inp = step["input"]
            md_parts.append(f"- **Input from:** `{inp.get('from', '—')}`.`{inp.get('field', '—')}`")
        if step.get("output"):
            out = step["output"]
            md_parts.append(f"- **Output:** `{out.get('name', '—')}` ({out.get('type', '—')})")
        if step.get("on_failure"):
            f = step["on_failure"]
            md_parts.append(f"- **On failure:** {f.get('strategy', '—')}" +
                           (f" (max {f['max_attempts']} attempts)" if "max_attempts" in f else ""))
        if step.get("parallel"):
            md_parts.append("- **Parallel:** Yes")
        if step.get("timeout_seconds"):
            md_parts.append(f"- **Timeout:** {step['timeout_seconds']}s")
        md_parts.append("")

    md_parts += [
        "## Full YAML Definition",
        "",
        "```yaml",
        source_yaml.strip(),
        "```",
        "",
        "## Pre-flight Checklist",
        "",
        "- [ ] All required tools available and authenticated",
        "- [ ] Input data matches the `inputs` schema",
        "- [ ] Output destinations writable",
        "- [ ] Rate limits checked for external APIs",
        "- [ ] Logging/observability configured",
        "- [ ] Test run completed on sample data",
    ]

    return "\n".join(md_parts)


def to_html(data: dict, source_yaml: str) -> str:
    """Generate a standalone HTML documentation page."""
    md = to_markdown(data, source_yaml)
    wf = data.get("workflow", {})
    name = wf.get("name", "Workflow")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Agent Workflow</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>
  :root {{ --bg: #f8f9fa; --card: #fff; --accent: #4A90D9; --text: #2c3e50; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: var(--bg); color: var(--text); padding: 40px; max-width: 960px; margin: 0 auto; }}
  h1 {{ color: var(--accent); border-bottom: 2px solid var(--accent); padding-bottom: 10px; }}
  h2 {{ color: var(--text); margin-top: 32px; }}
  h3 {{ color: #555; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th {{ background: var(--accent); color: white; padding: 8px 12px; text-align: left; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #dee2e6; }}
  tr:hover {{ background: #f1f3f5; }}
  code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
  pre {{ background: #2d2d2d; color: #f8f8f2; padding: 20px; border-radius: 8px; overflow-x: auto; }}
  pre code {{ background: none; color: inherit; }}
  blockquote {{ border-left: 4px solid var(--accent); padding: 12px 20px; background: #e8f4ff;
                margin: 0 0 16px 0; border-radius: 0 8px 8px 0; }}
  input[type=checkbox] {{ margin-right: 8px; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px;
             background: var(--accent); color: white; font-size: 12px; margin-left: 8px; }}
</style>
</head>
<body>
<div id="content"></div>
<script>
const md = {json.dumps(md)};
document.getElementById('content').innerHTML = marked.parse(md);
mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
// Re-render any mermaid blocks
document.querySelectorAll('code.language-mermaid').forEach(el => {{
  const div = document.createElement('div');
  div.className = 'mermaid';
  div.textContent = el.textContent;
  el.parentElement.replaceWith(div);
}});
mermaid.init();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Export a workflow YAML to multiple formats.")
    parser.add_argument("--file", required=True, help="YAML workflow file")
    parser.add_argument("--formats", default="yaml,markdown",
                        help="Comma-separated formats: yaml,json,markdown,html,mermaid,all")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    in_path = Path(args.file)
    if not in_path.exists():
        print(f"❌ File not found: {in_path}")
        sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else in_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = in_path.stem

    source_yaml = in_path.read_text()
    data = load_yaml(str(in_path))

    formats = [f.strip() for f in args.formats.split(",")]
    if "all" in formats:
        formats = ["yaml", "json", "markdown", "html", "mermaid"]

    exported = []

    for fmt in formats:
        if fmt == "yaml":
            out = out_dir / f"{stem}.yaml"
            out.write_text(source_yaml)
            exported.append(str(out))

        elif fmt == "json":
            out = out_dir / f"{stem}.json"
            out.write_text(to_json(data))
            exported.append(str(out))

        elif fmt == "markdown":
            out = out_dir / f"{stem}.md"
            out.write_text(to_markdown(data, source_yaml))
            exported.append(str(out))

        elif fmt == "html":
            out = out_dir / f"{stem}.html"
            out.write_text(to_html(data, source_yaml))
            exported.append(str(out))

        elif fmt == "mermaid":
            # Import and use render_mermaid
            try:
                sys.path.insert(0, str(Path(__file__).parent))
                from render_mermaid import workflow_to_mermaid
                diagram = workflow_to_mermaid(data)
                out = out_dir / f"{stem}_diagram.md"
                out.write_text(f"```mermaid\n{diagram}\n```")
                exported.append(str(out))
            except Exception as e:
                print(f"⚠️  Could not generate Mermaid diagram: {e}")
        else:
            print(f"⚠️  Unknown format: {fmt}")

    print(f"\n✅ Exported {len(exported)} file(s):")
    for f in exported:
        print(f"   {f}")


if __name__ == "__main__":
    main()
