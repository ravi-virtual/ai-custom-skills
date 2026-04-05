#!/usr/bin/env python3
"""
validate_workflow.py — Validate a YAML workflow file against the agent-workflow-creator schema.

Usage:
    python validate_workflow.py --file workflow.yaml [--strict] [--report]

Options:
    --file TEXT     Path to the YAML workflow file (required)
    --strict        Fail on warnings, not just errors
    --report        Print a detailed validation report
    --fix           Attempt to auto-fix common issues and write back
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_yaml(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML is required. Install with: pip install pyyaml")
        sys.exit(1)

    with open(path) as f:
        return yaml.safe_load(f)


# ─── Validation Rules ─────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []

    def error(self, msg: str):
        self.errors.append(f"❌ ERROR: {msg}")

    def warning(self, msg: str):
        self.warnings.append(f"⚠️  WARNING: {msg}")

    def ok(self, msg: str):
        self.passed.append(f"✅ {msg}")

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        lines += self.errors
        lines += self.warnings
        lines += self.passed
        return "\n".join(lines)


def validate_workflow(data: dict) -> ValidationResult:
    result = ValidationResult()

    if "workflow" not in data:
        result.error("Top-level 'workflow' key is missing")
        return result

    wf = data["workflow"]

    # ── Required top-level fields ──────────────────────────────────────────
    for field in ("name", "version", "description"):
        if field not in wf:
            result.error(f"Workflow missing required field: '{field}'")
        else:
            result.ok(f"Has '{field}': {wf[field][:60] if isinstance(wf[field], str) else wf[field]}")

    # ── Inputs ─────────────────────────────────────────────────────────────
    inputs = wf.get("inputs", [])
    if not inputs:
        result.warning("No inputs defined — consider defining at least one input")
    else:
        for i, inp in enumerate(inputs):
            if "name" not in inp:
                result.error(f"Input #{i} missing 'name'")
            if "type" not in inp:
                result.warning(f"Input '{inp.get('name', f'#{i}')}' missing 'type'")
            if inp.get("required") is None:
                result.warning(f"Input '{inp.get('name', f'#{i}')}' missing 'required' (defaulting to false)")
        result.ok(f"Inputs: {len(inputs)} defined")

    # ── Outputs ────────────────────────────────────────────────────────────
    outputs = wf.get("outputs", [])
    if not outputs:
        result.warning("No outputs defined")
    else:
        result.ok(f"Outputs: {len(outputs)} defined")

    # ── Steps ──────────────────────────────────────────────────────────────
    steps = wf.get("steps", [])
    if not steps:
        result.error("No steps defined")
        return result

    step_ids = set()
    for step in steps:
        sid = step.get("id")
        if not sid:
            result.error(f"Step missing 'id': {step.get('name', '(unnamed)')}")
            continue
        if sid in step_ids:
            result.error(f"Duplicate step ID: '{sid}'")
        step_ids.add(sid)

    result.ok(f"Steps: {len(steps)} defined with IDs: {sorted(step_ids)}")

    # ── Step-level validation ──────────────────────────────────────────────
    terminal_steps = []
    for step in steps:
        sid = step.get("id", "?")
        name = step.get("name", sid)

        # Required step fields
        if "tool" not in step:
            result.warning(f"Step '{sid}' ({name}) missing 'tool'")

        # Output check
        if "output" not in step:
            result.warning(f"Step '{sid}' ({name}) has no 'output' defined — outputs should be named")

        # On failure check for external tool calls
        external_tools = {"web_search", "web_fetch", "api_call", "database_read", "database_write"}
        if step.get("tool") in external_tools and "on_failure" not in step:
            result.warning(
                f"Step '{sid}' uses external tool '{step['tool']}' but has no 'on_failure' defined"
            )

        # Next step references
        next_steps = []
        if "on_success" in step and "next" in step["on_success"]:
            nxt = step["on_success"]["next"]
            if isinstance(nxt, list):
                next_steps.extend(nxt)
            else:
                next_steps.append(nxt)

        if "branches" in step:
            for branch in step["branches"]:
                if "next" in branch:
                    next_steps.append(branch["next"])

        for nxt in next_steps:
            if nxt not in step_ids:
                result.error(
                    f"Step '{sid}' references unknown step '{nxt}' in on_success/branches"
                )

        # Terminal step detection
        if not next_steps:
            terminal_steps.append(sid)

    if not terminal_steps:
        result.error("No terminal step found — all steps have a 'next'. At least one step must have no next.")
    else:
        result.ok(f"Terminal step(s): {terminal_steps}")

    # ── Output references ──────────────────────────────────────────────────
    for out in outputs:
        if "from" in out:
            ref = out["from"]
            ref_step = ref.split(".")[0] if "." in ref else None
            if ref_step and ref_step not in step_ids:
                result.error(f"Output '{out.get('name')}' references unknown step: '{ref_step}'")

    # ── Agents (multi-agent) ───────────────────────────────────────────────
    agent_ids = set()
    if "agents" in wf:
        for agent in wf["agents"]:
            aid = agent.get("id")
            if not aid:
                result.error("Agent missing 'id'")
            else:
                agent_ids.add(aid)
        result.ok(f"Agents: {len(wf['agents'])} defined")

        # Check step agent references
        for step in steps:
            if "agent" in step and step["agent"] not in agent_ids:
                result.error(
                    f"Step '{step.get('id')}' references unknown agent '{step['agent']}'"
                )

    # ── Error handling ─────────────────────────────────────────────────────
    if "error_handling" not in wf:
        result.warning("No global 'error_handling' defined")
    else:
        result.ok("Global error_handling configured")

    # ── Observability ──────────────────────────────────────────────────────
    if "observability" not in wf:
        result.warning("No 'observability' config — consider enabling logging and tracing")
    else:
        result.ok("Observability configured")

    return result


def print_report(result: ValidationResult, strict: bool) -> bool:
    print("\n── Validation Report ────────────────────────────────────────────")

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  {e}")

    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  {w}")

    if result.passed:
        print(f"\nPassed ({len(result.passed)}):")
        for p in result.passed:
            print(f"  {p}")

    print("\n── Summary ──────────────────────────────────────────────────────")
    is_ok = result.is_valid and not (strict and result.warnings)
    if is_ok:
        print(f"✅ Workflow is VALID ({len(result.passed)} checks passed, {len(result.warnings)} warnings)")
    else:
        status = "INVALID" if result.errors else "INVALID (strict mode: warnings treated as errors)"
        print(f"❌ Workflow is {status}")
        print(f"   Errors: {len(result.errors)}, Warnings: {len(result.warnings)}, Passed: {len(result.passed)}")

    return is_ok


def main():
    parser = argparse.ArgumentParser(description="Validate an agent workflow YAML file.")
    parser.add_argument("--file", required=True, help="Path to workflow YAML")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--report", action="store_true", help="Print detailed report")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    print(f"Validating: {path}")
    data = load_yaml(str(path))
    result = validate_workflow(data)

    is_ok = print_report(result, args.strict)
    sys.exit(0 if is_ok else 1)


if __name__ == "__main__":
    main()
