# Implementation Patterns (Python + Anthropic SDK)

Install: `pip install anthropic`. The client reads `ANTHROPIC_API_KEY`. Keep the model in configuration (`ANTHROPIC_MODEL`); check the `claude-api` skill or the current Anthropic docs for model IDs, parameters and features before relying on a specific one.

## Contents
- [Shared helpers](#shared-helpers)
- [Prompt chain with a gate](#prompt-chain-with-a-gate)
- [Router](#router)
- [Parallel map](#parallel-map)
- [Orchestrator and workers](#orchestrator-and-workers)
- [Evaluator-optimizer loop](#evaluator-optimizer-loop)
- [Tool-using agent loop](#tool-using-agent-loop)
- [Validation, retries, evaluation](#validation-retries-evaluation)

## Shared helpers

```python
import json, os, re
import anthropic

client = anthropic.Anthropic()
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

def ask(prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
    kwargs = {"model": MODEL, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    if system:
        kwargs["system"] = system
    msg = client.messages.create(**kwargs)
    return "".join(b.text for b in msg.content if b.type == "text")

def ask_json(prompt: str, required: set[str]) -> dict:
    """Ask for JSON, parse it, and check required keys; raise so the caller can retry."""
    text = ask(prompt + "\n\nReturn only a JSON object.")
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    data = json.loads(text)
    missing = required - data.keys()
    if missing:
        raise ValueError(f"missing keys: {missing}")
    return data
```

## Prompt chain with a gate

Each call does one job; a code check between calls stops bad data early.

```python
def write_post(topic: str) -> str:
    outline = ask(f"Create a 5-point outline for a blog post about: {topic}")
    if outline.count("\n") < 4:                      # gate: cheap deterministic check
        raise ValueError("outline too short")
    draft = ask(f"Write the post from this outline. Max 600 words.\n<outline>{outline}</outline>")
    return ask(f"Edit for clarity and fix errors. Return only the post.\n<draft>{draft}</draft>")
```

## Router

```python
ROUTES = {"billing": handle_billing, "technical": handle_technical, "other": handle_other}

def route(ticket: str):
    kind = ask_json(f'Classify the ticket as one of {list(ROUTES)}. JSON: {{"kind": "..."}}\n<ticket>{ticket}</ticket>', {"kind"})["kind"]
    return ROUTES.get(kind, handle_other)(ticket)     # unknown label falls back, never crashes
```

## Parallel map

```python
import asyncio
aclient = anthropic.AsyncAnthropic()

async def summarise(doc: str, sem: asyncio.Semaphore) -> str:
    async with sem:                                     # bound concurrency to respect rate limits
        msg = await aclient.messages.create(model=MODEL, max_tokens=500,
                                            messages=[{"role": "user", "content": f"Summarise in 3 bullets:\n<doc>{doc}</doc>"}])
        return msg.content[0].text

async def summarise_all(docs: list[str], limit: int = 5) -> list[str]:
    sem = asyncio.Semaphore(limit)
    return await asyncio.gather(*(summarise(d, sem) for d in docs))
```

## Orchestrator and workers

The orchestrator decides the subtasks at run time; workers run them; a final call merges.

```python
plan = ask_json(f'Split this task into 2-5 independent subtasks. JSON: {{"subtasks": ["..."]}}\n<task>{task}</task>', {"subtasks"})["subtasks"]
results = asyncio.run(summarise_all(plan))               # or a worker prompt per subtask
final = ask("Combine these results into one answer.\n" + "\n".join(f"<part>{r}</part>" for r in results))
```

## Evaluator-optimizer loop

```python
def refine(task: str, max_rounds: int = 3) -> str:
    draft = ask(task)
    for _ in range(max_rounds):                          # hard cap: loops must end
        review = ask_json(f'Review against the task. JSON: {{"ok": true|false, "issues": ["..."]}}\n<task>{task}</task>\n<draft>{draft}</draft>', {"ok", "issues"})
        if review["ok"]:
            break
        draft = ask(f"Revise the draft to fix these issues: {review['issues']}\n<draft>{draft}</draft>")
    return draft
```

## Tool-using agent loop

```python
TOOLS = [{
    "name": "search_orders",
    "description": "Look up a customer's orders by email. Read-only.",
    "input_schema": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]},
}]
HANDLERS = {"search_orders": lambda email: lookup_orders(email)}

def run_agent(task: str, max_turns: int = 8) -> str:
    messages = [{"role": "user", "content": task}]
    for _ in range(max_turns):                           # always bound the loop
        resp = client.messages.create(model=MODEL, max_tokens=2048, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                try:
                    out, is_error = HANDLERS[block.name](**block.input), False
                except Exception as exc:                  # report errors to the model instead of crashing
                    out, is_error = str(exc), True
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(out, default=str), "is_error": is_error})
        messages.append({"role": "user", "content": results})
    raise RuntimeError("agent did not finish within max_turns")
```

Tool design rules: narrow, well-described tools; read-only by default; destructive tools require an explicit approval step in code, not in the prompt; return small, structured results.

## Validation, retries, evaluation

- **Retry only what can change.** Retry on timeouts, 429/5xx and malformed output (with the error appended to the prompt); do not retry on auth or validation errors. The SDK already retries some transport errors; add your own bounded loop around parsing.
- **Validate outputs in code** (types, enums, ranges) rather than trusting the prompt. For anything user-visible, validate the schema before sending.
- **Evaluation set.** Keep `evals/cases.jsonl` with `{"input": ..., "expect": ...}`; run it on every prompt/model change and compare pass rates. Start with 10 cases that include edge and failure inputs.
- **Cost control.** Log token usage per step; put cheap, short steps (classification, routing) on smaller models where quality allows; cache or skip unchanged work.
- **Observability.** One JSON line per step with run id, step id, attempt, status, duration; keep prompts out of logs when they contain personal data.
