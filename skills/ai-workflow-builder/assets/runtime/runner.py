#!/usr/bin/env python3
"""runner.py - generic executor for agent-workflow-creator YAML workflows.

  python runner.py --check                              # static check: graph + tool availability
  python runner.py --input topic="RAG" --input depth=quick
  python runner.py --input-json inputs.json --max-steps 100

What it does: walks the steps from the first one following on_success.next / next / branches,
renders {{interpolations}}, calls the tool (LLM tools are built in, everything else comes from
tools.py -> TOOLS), applies on_failure (retry / fallback / skip / human_escalation / abort),
and returns the workflow outputs. A step with no next and no branches is terminal.
Not enforced: timeout_seconds, memory persistence, `transform` expressions.
"""
import argparse
import ast
import concurrent.futures
import datetime
import json
import os
import re
import sys
import time

import yaml

LLM_TOOLS = {"llm_completion", "llm_structured", "llm"}
TERMINALS = {"END", "end", "End", "__end__"}   # `next: END` stops the workflow
TEMPLATE_RE = re.compile(r"\{\{\s*([A-Za-z_][\w\-]*(?:\.[\w\-]+)*)\s*\}\}")


class WorkflowError(Exception):
    pass


class EscalationRequired(WorkflowError):
    """A step asked for a human; carries the context so a caller can queue it."""


# ----------------------------------------------------------------------------- state
class State:
    def __init__(self, inputs):
        self.inputs = dict(inputs)
        self.steps = {}    # step_id -> {output_name: value}
        self.flat = {}     # output_name -> latest value
        self.memory = {}

    def set(self, step_id, name, value):
        self.steps.setdefault(step_id, {})[name] = value
        self.flat[name] = value

    def lookup(self, path, extra=None):
        head, *rest = path.split(".")
        if extra and head in extra:
            value = extra[head]
        elif head == "inputs":
            value = self.inputs
        elif head == "memory":
            value = self.memory
        elif head in self.steps:
            value = self.steps[head]
        elif head in self.flat:
            value = self.flat[head]
        elif head == "current_year":
            value = datetime.date.today().year
        elif head == "now":
            value = datetime.datetime.now().isoformat(timespec="seconds")
        else:
            raise WorkflowError(f"unresolved reference '{path}' (known: inputs, {', '.join(sorted(set(self.steps) | set(self.flat))) or 'no outputs yet'})")
        for part in rest:
            try:
                value = value[int(part)] if isinstance(value, list) else value[part]
            except (KeyError, IndexError, ValueError, TypeError):
                raise WorkflowError(f"unresolved reference '{path}' (no '{part}')")
        return value


def render(value, state, extra=None):
    """Interpolate {{refs}} in strings, lists and dicts. A string that is exactly one ref keeps its type."""
    if isinstance(value, str):
        whole = TEMPLATE_RE.fullmatch(value.strip())
        if whole:
            return state.lookup(whole.group(1), extra)

        def sub(m):
            v = state.lookup(m.group(1), extra)
            return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
        return TEMPLATE_RE.sub(sub, value)
    if isinstance(value, list):
        return [render(v, state, extra) for v in value]
    if isinstance(value, dict):
        return {k: render(v, state, extra) for k, v in value.items()}
    return value


# ----------------------------------------------------------------------------- conditions
_ALLOWED = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.Compare, ast.Eq,
            ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Is, ast.IsNot, ast.Name,
            ast.Load, ast.Attribute, ast.Subscript, ast.Constant, ast.List, ast.Tuple)


def eval_condition(expr, state):
    text = TEMPLATE_RE.sub(lambda m: m.group(1), expr.strip())   # "{{a.b}} == 1" -> "a.b == 1"
    text = re.sub(r"\btrue\b", "True", text)
    text = re.sub(r"\bfalse\b", "False", text)
    text = re.sub(r"\b(?:null|none)\b", "None", text, flags=re.I)
    text = text.replace("&&", " and ").replace("||", " or ")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError:
        raise WorkflowError(f"condition is not a machine-evaluable expression: {expr!r}. Rewrite it like \"classification.urgency == 'high'\".")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise WorkflowError(f"unsupported syntax in condition {expr!r}: {type(node).__name__}")
    return bool(_ev(tree.body, state))


def _ev(node, state):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_ev(e, state) for e in node.elts]
    if isinstance(node, ast.Name):
        return state.lookup(node.id)
    if isinstance(node, ast.Attribute):
        base = _ev(node.value, state)
        try:
            return base[node.attr]
        except (KeyError, TypeError):
            raise WorkflowError(f"unresolved '{node.attr}' in condition")
    if isinstance(node, ast.Subscript):
        base = _ev(node.value, state)
        key_node = node.slice.value if isinstance(node.slice, getattr(ast, "Index", ())) else node.slice  # py3.8 compat
        key = _ev(key_node, state)
        try:
            return base[key]
        except (KeyError, IndexError, TypeError):
            raise WorkflowError("unresolved subscript in condition")
    if isinstance(node, ast.UnaryOp):
        v = _ev(node.operand, state)
        return (not v) if isinstance(node.op, ast.Not) else -v
    if isinstance(node, ast.BoolOp):
        vals = (_ev(v, state) for v in node.values)
        return all(vals) if isinstance(node.op, ast.And) else any(vals)
    if isinstance(node, ast.Compare):
        left = _ev(node.left, state)
        for op, comp in zip(node.ops, node.comparators):
            right = _ev(comp, state)
            ok = {ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b, ast.Lt: lambda a, b: a < b,
                  ast.LtE: lambda a, b: a <= b, ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b,
                  ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
                  ast.Is: lambda a, b: a is b, ast.IsNot: lambda a, b: a is not b}[type(op)](left, right)
            if not ok:
                return False
            left = right
        return True
    raise WorkflowError(f"unsupported condition node {type(node).__name__}")


# ----------------------------------------------------------------------------- helpers
def parse_json_loose(text):
    """Parse JSON from an LLM reply, tolerating ```json fences and surrounding prose."""
    if not isinstance(text, str):
        return text
    s = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, re.S)
    if fence:
        s = fence.group(1)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        for open_c, close_c in (("{", "}"), ("[", "]")):
            i, j = s.find(open_c), s.rfind(close_c)
            if 0 <= i < j:
                try:
                    return json.loads(s[i:j + 1])
                except json.JSONDecodeError:
                    pass
        raise WorkflowError("model reply was not valid JSON")


def output_spec(step):
    out = step.get("output")
    if isinstance(out, dict):
        return out.get("name") or "result", (out.get("type") or "").lower()
    if isinstance(out, str):
        return out, ""
    return "result", ""


def builtin_human_input(ctx):
    message = ctx.get("prompt") or json.dumps(ctx.get("input"), default=str)
    if os.getenv("RUNNER_NONINTERACTIVE") == "1" or not sys.stdin.isatty():
        raise EscalationRequired(f"human input required: {message}")
    return input(f"\n{message}\n> ")


def load_tools():
    try:
        import tools as user_tools
        registry = dict(getattr(user_tools, "TOOLS", {}))
    except ImportError:
        registry = {}
    registry.setdefault("human_input", builtin_human_input)
    return registry


# ----------------------------------------------------------------------------- engine
class Runner:
    def __init__(self, workflow, llm=None, tools=None, sleep=time.sleep):
        self.wf = workflow["workflow"] if "workflow" in workflow else workflow
        self.steps = {s["id"]: s for s in self.wf.get("steps", [])}
        if not self.steps:
            raise WorkflowError("workflow has no steps")
        self.first = self.wf["steps"][0]["id"]
        self.llm = llm
        self.tools = tools if tools is not None else load_tools()
        self.sleep = sleep
        self.scale = float(os.getenv("RUNNER_BACKOFF_SCALE", "1"))
        self.trace = []
        self.log_dir = os.getenv("RUN_LOG_DIR")

    # -- static check
    def check(self):
        problems = []
        for sid, step in self.steps.items():
            tool = step.get("tool")
            if tool and tool not in LLM_TOOLS and tool not in self.tools:
                problems.append(f"{sid}: tool '{tool}' is not implemented (add it to tools.py TOOLS)")
            targets = [b.get("next") for b in step.get("branches") or []]
            targets += [(step.get("on_failure") or {}).get("fallback_step")]
            for nxt in ((step.get("on_success") or {}).get("next"), step.get("next")):
                targets += [nxt.get("then"), nxt.get("else")] if isinstance(nxt, dict) else [nxt]
            for t in filter(None, targets):
                if t not in self.steps and t not in TERMINALS:
                    problems.append(f"{sid}: next/fallback '{t}' does not exist")
        return problems

    # -- tracing
    def _log(self, **event):
        event["ts"] = datetime.datetime.now().isoformat(timespec="milliseconds")
        self.trace.append(event)
        if self.log_dir:
            os.makedirs(self.log_dir, exist_ok=True)
            with open(os.path.join(self.log_dir, "trace.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, default=str) + "\n")

    # -- one attempt of one step
    def _call_tool(self, step, state, item=None, mapped=False):
        extra = {"item": item} if mapped else None
        value = self._resolve_input(step, state)
        if mapped:
            value = item
        prompt = render(step["prompt"], state, extra) if step.get("prompt") else None
        config = render(step.get("tool_config") or {}, state, extra)
        tool = step.get("tool")
        if tool in LLM_TOOLS:
            if self.llm is None:
                raise WorkflowError("no LLM configured (see llm.py get_llm)")
            text = self.llm.complete(prompt or json.dumps(value, default=str), system=config.get("system") if isinstance(config, dict) else None)
            return text
        if tool not in self.tools:
            raise WorkflowError(f"tool '{tool}' is not implemented (add it to tools.py TOOLS)")
        return self.tools[tool]({"step": step, "input": value, "prompt": prompt, "config": config, "state": state})

    def _resolve_input(self, step, state):
        inp = step.get("input")
        if inp is None:
            return None
        if isinstance(inp, dict) and "from" in inp:
            src, field = inp["from"], inp.get("field")
            if isinstance(src, list):  # several sources -> {last_path_segment: value}
                return {ref.split(".")[-1]: (state.inputs if ref == "inputs" else state.lookup(ref)) for ref in src}
            value = state.inputs if src == "inputs" else state.lookup(src)
            if isinstance(value, dict) and field and field in value:
                return value[field]
            return value
        return render(inp, state)

    def _attempt(self, step, state):
        name, typ = output_spec(step)
        value = self._resolve_input(step, state)
        if step.get("parallel") and isinstance(value, list):
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, max(1, len(value)))) as pool:
                result = list(pool.map(lambda it: self._call_tool(step, state, it, True), value))
        else:
            result = self._call_tool(step, state)
        if typ in ("json", "list", "dict", "object", "array") and isinstance(result, str):
            result = parse_json_loose(result)
        elif typ in ("json", "list", "dict", "object", "array") and isinstance(result, list) and step.get("tool") in LLM_TOOLS:
            result = [parse_json_loose(r) for r in result]
        return name, result

    def _run_step(self, sid, state):
        step = self.steps[sid]
        policy = step.get("on_failure") or {}
        strategy = policy.get("strategy", "abort")
        attempts = int(policy.get("max_attempts", 3 if strategy == "retry" else 1))
        backoff = policy.get("backoff_seconds", policy.get("wait_seconds", 0))
        last = None
        for attempt in range(1, attempts + 1):
            started = time.time()
            try:
                name, result = self._attempt(step, state)
                state.set(sid, name, result)
                self._log(step=sid, attempt=attempt, status="ok", seconds=round(time.time() - started, 3))
                return None
            except EscalationRequired:
                raise
            except Exception as exc:  # noqa: BLE001 - policy decides what happens next
                last = exc
                self._log(step=sid, attempt=attempt, status="error", error=str(exc))
                if attempt < attempts:
                    delay = backoff[min(attempt - 1, len(backoff) - 1)] if isinstance(backoff, list) and backoff else backoff
                    self.sleep(float(delay or 0) * self.scale)
        fb = policy.get("fallback_step")
        if fb:
            return fb
        if strategy in ("skip", "continue"):
            name, _ = output_spec(step)
            state.set(sid, name, None)
            return None
        if strategy == "human_escalation":
            raise EscalationRequired(f"step '{sid}' needs a human after failure: {last}")
        raise WorkflowError(f"step '{sid}' failed: {last}") from last

    def _next(self, sid, state):
        step = self.steps[sid]
        branches = step.get("branches") or []
        for b in branches:
            if eval_condition(b["condition"], state):
                return b["next"]
        if branches:
            raise WorkflowError(f"step '{sid}': no branch condition matched")
        nxt = (step.get("on_success") or {}).get("next") or step.get("next")
        if isinstance(nxt, dict):  # next: {if: "<expr>", then: step_a, else: step_b}
            return nxt.get("then") if eval_condition(str(nxt.get("if", "false")), state) else nxt.get("else")
        return nxt

    def run(self, inputs, max_steps=None):
        max_steps = max_steps or int(os.getenv("RUNNER_MAX_STEPS", "200"))
        state = State(self._with_defaults(inputs))
        sid, executed = self.first, 0
        while sid and sid not in TERMINALS:
            executed += 1
            if executed > max_steps:
                raise WorkflowError(f"stopped after {max_steps} steps (loop without exit?)")
            if sid not in self.steps:
                raise WorkflowError(f"unknown step '{sid}'")
            forced = self._run_step(sid, state)
            sid = forced if forced else self._next(sid, state)
        return self._collect(state)

    def _with_defaults(self, inputs):
        merged = {}
        for spec in self.wf.get("inputs", []) or []:
            if "default" in spec:
                merged[spec["name"]] = spec["default"]
        merged.update(inputs)
        missing = [s["name"] for s in self.wf.get("inputs", []) or [] if s.get("required") and s["name"] not in merged]
        if missing:
            raise WorkflowError(f"missing required input(s): {', '.join(missing)}")
        return merged

    def _collect(self, state):
        outs = self.wf.get("outputs") or []
        result = {}
        for o in outs:
            src = o.get("from")
            if src:
                try:
                    result[o["name"]] = state.lookup(src)
                except WorkflowError:
                    result[o["name"]] = None
        return result or dict(state.flat)


# ----------------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="Run a workflow.yaml produced with agent-workflow-creator.")
    ap.add_argument("--workflow", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow.yaml"))
    ap.add_argument("--input", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--input-json", help="JSON file with inputs")
    ap.add_argument("--max-steps", type=int)
    ap.add_argument("--check", action="store_true", help="static check only; exit 1 on problems")
    args = ap.parse_args(argv)

    with open(args.workflow, encoding="utf-8") as fh:
        wf = yaml.safe_load(fh)
    runner = Runner(wf)
    if args.check:
        problems = runner.check()
        for p in problems:
            print("PROBLEM:", p)
        print(f"{len(runner.steps)} steps, {len(problems)} problem(s).")
        return 1 if problems else 0

    inputs = {}
    if args.input_json:
        with open(args.input_json, encoding="utf-8") as fh:
            inputs.update(json.load(fh))
    for pair in args.input:
        key, _, val = pair.partition("=")
        inputs[key] = val
    from llm import get_llm
    runner.llm = get_llm()
    try:
        print(json.dumps(runner.run(inputs, args.max_steps), indent=2, ensure_ascii=False, default=str))
        return 0
    except EscalationRequired as exc:
        print(f"ESCALATION: {exc}", file=sys.stderr)
        return 3
    except WorkflowError as exc:
        print(f"WORKFLOW ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
