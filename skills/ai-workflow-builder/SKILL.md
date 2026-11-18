---
name: ai-workflow-builder
description: Implements an AI workflow as working software - a runnable, tested Python project that executes an agent-workflow-creator YAML spec (LLM steps via the Anthropic API, tool steps, retries, fallbacks, branching, human approval gates, logging), or a mapped no-code build in n8n, Make or Zapier. Use when the user wants to actually build, wire up, run or automate an LLM pipeline or agent (not just design it), add tool use or an agent loop, make a prompt chain reliable, or turn a process into something that runs on a schedule or webhook. Pair with agent-workflow-creator, which designs and validates the spec first.
---

# AI Workflow Builder

Turns a workflow design into something that runs. Design lives in `agent-workflow-creator`; this skill covers implementation, testing and hardening.

## Choose the simplest thing that works

| Situation | Build |
|---|---|
| One LLM call (maybe with retrieval) solves it | A single function, no workflow engine |
| Fixed sequence of steps, some LLM, some API calls | Prompt chain: the Python runner here, or n8n/Make for non-developers |
| Inputs differ and need different handling | Router (classify, then branch) |
| Same operation over many items | Parallel map (`parallel: true`) |
| Quality bar needs a second look | Generate then evaluate then revise, with a loop limit |
| Path cannot be known in advance | Agent loop with tools (see `references/implementation-patterns.md`) |

Add agency only when a fixed workflow demonstrably fails; every extra loop costs latency, money and predictability.

## Workflow

1. **Get a valid spec.** If none exists, use `agent-workflow-creator` to design it, then validate: `python ../agent-workflow-creator/scripts/validate_workflow.py --file workflow.yaml --strict`.
2. **Pick the runtime.** Code: continue below. No-code (n8n, Make, Zapier): read `references/no-code-automation.md` for the concept mapping.
3. **Scaffold:** `python scripts/scaffold_python_workflow.py --file workflow.yaml --out ./my-workflow`. Result: `runner.py` (generic executor), `llm.py` (Anthropic adapter and a fake for tests), `tools.py` (one stub per non-LLM tool), `tests/`, `.env.example`, `README.md`.
4. **Implement `tools.py`.** Each tool receives `ctx` (`input`, `prompt`, `config`, `state`), returns the step output, and **raises** on failure so the step's `on_failure` policy applies. Replace real side effects with fakes in tests.
5. **Check and test:** `python runner.py --check` (dangling `next`, missing tools), `python -m pytest -q`, then `RUNNER_FAKE_LLM=1 python runner.py --input key=value` for a dry run, then a real run with `ANTHROPIC_API_KEY` set.
6. **Harden** with the checklist below. Hand over the run commands and the list of environment variables.

## What the runner supports

Sequential flow via `on_success.next` / `next`; `next: {if, then, else}`; `branches` with conditions such as `classification.urgency == 'high'`; `next: END`; `{{inputs.x}}`, `{{step_id.output}}`, `{{output_name.field}}` interpolation; `parallel: true` over a list input; `on_failure` strategies `retry` (with `backoff_seconds` or `wait_seconds`), `fallback` (`fallback_step`), `skip`, `human_escalation`, `abort`; input defaults and required checks; JSON-reply parsing for `type: json|list`; a step cap (`RUNNER_MAX_STEPS`) against runaway loops; JSONL traces (`RUN_LOG_DIR`). Not enforced: `timeout_seconds`, `memory` persistence, `transform` expressions. Conditions must be real expressions; natural-language conditions fail with a message telling you to rewrite them.

## Hardening checklist

- [ ] Every tool that writes, sends, pays or deletes is behind a human approval step or is idempotent (safe to run twice)
- [ ] Text fetched from the web, email or files is treated as **data**: it never becomes instructions, and tools are limited to what the step needs (prompt-injection defence)
- [ ] Secrets come from environment variables or a secrets manager, never from the YAML, the prompts or logs
- [ ] Each LLM step validates its output (JSON parse, required keys, allowed values) and has a retry or fallback
- [ ] Loops have a counter and a maximum; the run has a step cap and a cost/time budget
- [ ] Logs record step, attempt, status and duration without personal data or full prompts where that is sensitive
- [ ] A small evaluation set (5 to 20 realistic inputs with expected results) exists and is rerun after every prompt or model change
- [ ] Rate limits and 429/5xx errors are retried with backoff; failures end in a clear state (escalated, partial output, or aborted), never silence
- [ ] Model name comes from configuration (`ANTHROPIC_MODEL`), not scattered literals

## References

- `references/implementation-patterns.md` - prompt chain, router, parallel map, orchestrator-workers, evaluator-optimizer and a tool-using agent loop with the Anthropic SDK, plus validation, retries and evaluation
- `references/no-code-automation.md` - mapping workflow concepts to n8n, Make and Zapier, and when to prefer them
- `assets/runtime/` - the runner, LLM adapter and engine tests that the scaffold copies
