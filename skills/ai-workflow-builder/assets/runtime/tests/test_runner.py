"""Engine tests: interpolation, branching, retry/fallback/skip/escalation, parallel, loops, check()."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm import FakeLLM  # noqa: E402
from runner import EscalationRequired, Runner, WorkflowError, eval_condition, parse_json_loose, render, State  # noqa: E402

NO_SLEEP = lambda s: None  # noqa: E731


def wf(steps, **extra):
    return {"workflow": {"name": "t", "inputs": [{"name": "topic", "required": True}], "steps": steps, **extra}}


def test_interpolation_keeps_type_and_json_encodes_in_text():
    st = State({"n": 3})
    st.set("s1", "items", [1, 2])
    assert render("{{inputs.n}}", st) == 3
    assert render("count={{inputs.n}} items={{s1.items}} first={{items.0}}", st) == "count=3 items=[1, 2] first=1"
    with pytest.raises(WorkflowError):
        render("{{nope.x}}", st)


def test_llm_json_and_chain():
    llm = FakeLLM(['```json\n{"urgency": "high"}\n```', "done"])
    steps = [
        {"id": "a", "tool": "llm_structured", "prompt": "classify {{inputs.topic}}", "output": {"name": "cls", "type": "json"}, "on_success": {"next": "b"}},
        {"id": "b", "tool": "llm_completion", "prompt": "write about {{cls.urgency}}", "output": {"name": "text", "type": "string"}},
    ]
    out = Runner(wf(steps), llm=llm, tools={}).run({"topic": "x"})
    assert out == {"cls": {"urgency": "high"}, "text": "done"}
    assert "write about high" in llm.calls[1]["prompt"]


def test_missing_required_input():
    with pytest.raises(WorkflowError, match="missing required"):
        Runner(wf([{"id": "a", "tool": "t"}]), tools={"t": lambda c: 1}).run({})


def test_branches_pick_first_true_and_natural_language_condition_errors():
    steps = [
        {"id": "a", "tool": "t", "output": "flag", "branches": [
            {"condition": "flag == true", "next": "yes"}, {"condition": "flag == false", "next": "no"}]},
        {"id": "yes", "tool": "y", "output": "r"},
        {"id": "no", "tool": "n", "output": "r"},
    ]
    r = Runner(wf(steps), tools={"t": lambda c: True, "y": lambda c: "YES", "n": lambda c: "NO"}, sleep=NO_SLEEP)
    assert r.run({"topic": "x"})["r"] == "YES"
    with pytest.raises(WorkflowError, match="machine-evaluable"):
        eval_condition("if the user is angry", State({}))


def test_retry_then_success_and_exhaustion():
    calls = {"n": 0}

    def flaky(ctx):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    steps = [{"id": "a", "tool": "flaky", "output": "r", "on_failure": {"strategy": "retry", "max_attempts": 3, "backoff_seconds": [1, 2]}}]
    assert Runner(wf(steps), tools={"flaky": flaky}, sleep=NO_SLEEP).run({"topic": "x"})["r"] == "ok"
    calls["n"] = -10
    with pytest.raises(WorkflowError, match="failed"):
        Runner(wf(steps), tools={"flaky": flaky}, sleep=NO_SLEEP).run({"topic": "x"})


def test_fallback_skip_and_escalation():
    def bad(ctx):
        raise RuntimeError("x")

    fb = [
        {"id": "a", "tool": "bad", "output": "r", "on_failure": {"strategy": "fallback", "fallback_step": "b"}},
        {"id": "b", "tool": "good", "output": "r"},
    ]
    assert Runner(wf(fb), tools={"bad": bad, "good": lambda c: "fallback"}, sleep=NO_SLEEP).run({"topic": "x"})["r"] == "fallback"
    skip = [{"id": "a", "tool": "bad", "output": "r", "on_failure": {"strategy": "skip"}, "next": "b"}, {"id": "b", "tool": "good", "output": "s"}]
    assert Runner(wf(skip), tools={"bad": bad, "good": lambda c: 1}, sleep=NO_SLEEP).run({"topic": "x"}) == {"r": None, "s": 1}
    esc = [{"id": "a", "tool": "bad", "on_failure": {"strategy": "human_escalation"}}]
    with pytest.raises(EscalationRequired):
        Runner(wf(esc), tools={"bad": bad}, sleep=NO_SLEEP).run({"topic": "x"})


def test_parallel_maps_over_list_in_order():
    steps = [
        {"id": "a", "tool": "mk", "output": "qs", "next": "b"},
        {"id": "b", "tool": "up", "parallel": True, "input": {"from": "a.qs", "field": "each_query"}, "output": "res"},
    ]
    out = Runner(wf(steps), tools={"mk": lambda c: ["x", "y", "z"], "up": lambda c: c["input"].upper()}).run({"topic": "t"})
    assert out["res"] == ["X", "Y", "Z"]


def test_loop_guard_and_workflow_outputs():
    loop = [{"id": "a", "tool": "t", "output": "r", "next": "a"}]
    with pytest.raises(WorkflowError, match="stopped after"):
        Runner(wf(loop), tools={"t": lambda c: 1}).run({"topic": "x"}, max_steps=5)
    steps = [{"id": "a", "tool": "t", "output": "report"}]
    out = Runner(wf(steps, outputs=[{"name": "final", "from": "a.report"}]), tools={"t": lambda c: "R"}).run({"topic": "x"})
    assert out == {"final": "R"}


def test_check_reports_missing_tools_and_dangling_next():
    steps = [{"id": "a", "tool": "web_search", "next": "ghost"}]
    problems = Runner(wf(steps), tools={}).check()
    assert any("web_search" in p for p in problems) and any("ghost" in p for p in problems)


def test_parse_json_loose():
    assert parse_json_loose('Sure! {"a": 1} hope that helps') == {"a": 1}
    with pytest.raises(WorkflowError):
        parse_json_loose("no json here")


def test_next_if_then_else_loops_until_condition_changes():
    count = {"n": 0}

    def work(ctx):
        count["n"] += 1
        return count["n"] < 3          # "more records available"

    steps = [
        {"id": "a", "tool": "work", "output": "more", "next": {"if": "{{more}} == true", "then": "a", "else": "done"}},
        {"id": "done", "tool": "fin", "output": "r"},
    ]
    out = Runner(wf(steps), tools={"work": work, "fin": lambda c: "end"}).run({"topic": "x"})
    assert count["n"] == 3 and out["r"] == "end"
    assert Runner(wf(steps), tools={"work": work, "fin": lambda c: 1}).check() == []


def test_wait_seconds_is_used_as_backoff():
    waits = []
    steps = [{"id": "a", "tool": "t", "on_failure": {"strategy": "retry", "max_attempts": 3, "wait_seconds": 7}}]

    def always_fails(ctx):
        raise RuntimeError("x")

    with pytest.raises(WorkflowError):
        Runner(wf(steps), tools={"t": always_fails}, sleep=waits.append).run({"topic": "x"})
    assert waits == [7.0, 7.0]


def test_end_sentinel_stops_the_run():
    steps = [{"id": "a", "tool": "t", "output": "r", "next": "END"}, {"id": "b", "tool": "t", "output": "never"}]
    r = Runner(wf(steps), tools={"t": lambda c: 1})
    assert r.check() == [] and r.run({"topic": "x"}) == {"r": 1}


def test_input_from_several_sources_becomes_a_dict():
    seen = {}
    steps = [
        {"id": "a", "tool": "mk", "output": "x", "next": "b"},
        {"id": "b", "tool": "mk2", "output": "y", "next": "c"},
        {"id": "c", "tool": "use", "input": {"from": ["a.x", "b.y"]}, "output": "z"},
    ]
    tools = {"mk": lambda c: 1, "mk2": lambda c: 2, "use": lambda c: seen.update(c["input"]) or 3}
    assert Runner(wf(steps), tools=tools).run({"topic": "t"})["z"] == 3 and seen == {"x": 1, "y": 2}
