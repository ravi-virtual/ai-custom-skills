#!/usr/bin/env python3
"""scaffold_python_workflow.py - turn an agent-workflow-creator YAML into a runnable Python project.

Usage:
  python scaffold_python_workflow.py --file workflow.yaml --out ./my-workflow [--force]

Creates in --out:
  workflow.yaml        copy of the spec (the single source of truth)
  runner.py, llm.py    generic executor + Anthropic/Fake LLM adapters (from assets/runtime)
  tools.py             one stub per non-LLM tool the workflow uses -> implement these
  tests/               engine tests + a graph test for this workflow
  requirements.txt, .env.example, README.md

Next steps printed at the end. Requires PyYAML to read the spec.
"""
import argparse
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(os.path.dirname(HERE), "assets", "runtime")
LLM_TOOLS = {"llm_completion", "llm_structured", "llm"}
BUILTIN_TOOLS = {"human_input"}


def collect_tools(steps):
    used = {}
    for s in steps:
        t = s.get("tool")
        if t and t not in LLM_TOOLS and t not in BUILTIN_TOOLS:
            used.setdefault(t, []).append(s)
    return used


def render_tools_py(used):
    lines = ['"""Tool implementations for this workflow. Each tool receives one dict:',
             '',
             '  ctx["input"]   resolved step input     ctx["prompt"]  rendered prompt (or None)',
             '  ctx["config"]  rendered tool_config    ctx["state"]   run State (outputs so far)',
             '',
             'Return the value that should be stored as the step output. Raise on failure so the',
             'step\'s on_failure policy (retry / fallback / escalation) can react.',
             '"""',
             '']
    for tool, steps in sorted(used.items()):
        where = "; ".join(f"{s['id']} ({s.get('name', '')})" for s in steps)
        out_names = sorted({(s.get("output") or {}).get("name", "result") if isinstance(s.get("output"), dict) else str(s.get("output") or "result") for s in steps})
        lines += [f"def {tool}(ctx):",
                  f'    """Used by: {where}',
                  f"    Must return: {', '.join(out_names)}",
                  '    """',
                  f'    raise NotImplementedError("Implement tool \'{tool}\' in tools.py")',
                  '', '']
    lines.append("TOOLS = {")
    lines += [f'    "{t}": {t},' for t in sorted(used)]
    lines.append("}")
    return "\n".join(lines) + "\n"


GRAPH_TEST = '''"""Structural test for this workflow: every next/fallback target must exist."""
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import Runner  # noqa: E402


def test_no_dangling_references():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflow.yaml")) as fh:
        runner = Runner(yaml.safe_load(fh), tools={})
    dangling = [p for p in runner.check() if "does not exist" in p]
    assert not dangling, dangling


# Add an end-to-end test once tools are implemented, e.g.:
#   from llm import FakeLLM
#   runner = Runner(spec, llm=FakeLLM(["{...json...}"]), tools={"web_search": lambda c: [...]})
#   assert runner.run({"topic": "x"})["report"]
'''

README = '''# {name}

{description}

Generated from `workflow.yaml` (agent-workflow-creator schema). Edit the YAML to change behaviour; edit `tools.py` to implement integrations.

```bash
pip install -r requirements.txt
cp .env.example .env            # then export the variables (or use your env manager)
python runner.py --check        # graph + missing-tool report
python -m pytest -q             # engine + graph tests
RUNNER_FAKE_LLM=1 python runner.py --input key=value   # dry run with a fake LLM
python runner.py --input key=value                     # real run (needs ANTHROPIC_API_KEY)
```

Exit codes: 0 ok, 1 workflow error, 3 human escalation required.
'''


def main():
    ap = argparse.ArgumentParser(description="Scaffold a runnable Python project from a workflow YAML.")
    ap.add_argument("--file", required=True, help="workflow YAML (agent-workflow-creator schema)")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--force", action="store_true", help="overwrite files in a non-empty output directory")
    args = ap.parse_args()

    try:
        with open(args.file, encoding="utf-8") as fh:
            spec = yaml.safe_load(fh)
        wf = spec["workflow"]
        steps = wf["steps"]
        assert steps and all("id" in s for s in steps)
    except (OSError, KeyError, TypeError, AssertionError, yaml.YAMLError) as exc:
        print(f"Error: {args.file} is not a valid workflow spec ({exc!r}). Run validate_workflow.py from agent-workflow-creator first.", file=sys.stderr)
        return 1

    if os.path.isdir(args.out) and os.listdir(args.out) and not args.force:
        print(f"Error: {args.out} is not empty (use --force to overwrite).", file=sys.stderr)
        return 1
    os.makedirs(os.path.join(args.out, "tests"), exist_ok=True)

    for name in ("runner.py", "llm.py"):
        shutil.copy(os.path.join(RUNTIME, name), os.path.join(args.out, name))
    shutil.copy(os.path.join(RUNTIME, "tests", "test_runner.py"), os.path.join(args.out, "tests", "test_runner.py"))
    shutil.copy(args.file, os.path.join(args.out, "workflow.yaml"))

    used = collect_tools(steps)
    write = lambda rel, text: open(os.path.join(args.out, rel), "w", encoding="utf-8").write(text)  # noqa: E731
    write("tools.py", render_tools_py(used))
    write("tests/test_workflow_graph.py", GRAPH_TEST)
    write("requirements.txt", "pyyaml>=6\nanthropic>=0.40\npytest>=8\n")
    write(".env.example", "ANTHROPIC_API_KEY=\n# ANTHROPIC_MODEL=claude-sonnet-5-5\n# RUN_LOG_DIR=./runs\n# RUNNER_MAX_STEPS=200\n")
    write("README.md", README.format(name=wf.get("name", "workflow"), description=" ".join(str(wf.get("description", "")).split())))

    print(f"Scaffolded {len(steps)} step(s) into {args.out}")
    if used:
        print("Implement these tools in tools.py: " + ", ".join(sorted(used)))
    print(f"Next: cd {args.out} && python runner.py --check && python -m pytest -q")
    return 0


if __name__ == "__main__":
    sys.exit(main())
