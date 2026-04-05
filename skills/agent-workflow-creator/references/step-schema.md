# Step Schema Reference

Every node in an agent workflow must conform to this schema. Use it when decomposing tasks.

## Full Step Schema

```yaml
step:
  id: string                  # Unique identifier, e.g. step_01, fetch_data
  name: string                # Human-readable name, e.g. "Fetch Search Results"
  description: string         # 1–2 sentence description of what this step does
  agent: string               # Role performing this step (omit if single-agent)
  tool: string                # Tool or capability used (see Tool Types below)
  tool_config:                # Optional tool-specific configuration
    model: string             # For LLM steps: which model
    temperature: float        # For LLM steps
    endpoint: string          # For API steps
    method: string            # For API steps: GET / POST / etc.
  input:
    from: string              # Source: "inputs", "step_XX.output", "memory", "human"
    field: string             # Specific field name from source
    schema: object            # Expected structure of the input
  output:
    name: string              # Variable name for this step's output
    type: string              # Type: string, list, json, file, boolean, number
    schema: object            # Expected structure of the output
  prompt: string              # For LLM steps: the prompt template (use {{vars}})
  condition:                  # For decision/branching steps
    expression: string        # Condition to evaluate, e.g. "{{output}} != null"
  on_success:
    next: string              # Step ID to go to on success
  on_failure:
    strategy: string          # "retry", "fallback", "abort", "human_escalation"
    max_attempts: int         # For retry strategy
    fallback_step: string     # For fallback strategy: step ID to jump to
    alert: string             # Notification channel/method
  on_ambiguous:
    checkpoint: boolean       # Whether to pause for human review
    prompt_human: string      # What to ask the human
  parallel: boolean           # Can this step run in parallel with others?
  timeout_seconds: int        # Max allowed time for this step
  retry_on:
    - string                  # Error types that trigger retry
  tags:
    - string                  # Labels: "critical", "async", "external", etc.
  notes: string               # Implementation notes, caveats, edge cases
```

---

## Tool Types

Standard tool types used in step definitions:

| Tool Type | Description | Example Use |
|-----------|-------------|-------------|
| `web_search` | Search the internet | Finding current information |
| `web_fetch` | Retrieve full web page content | Reading an article |
| `code_execution` | Run code in a sandbox | Data analysis, computation |
| `file_read` | Read a file from storage | Loading a document |
| `file_write` | Write output to a file | Saving results |
| `llm_completion` | Call an LLM for text generation | Summarizing, drafting |
| `llm_structured` | LLM call with JSON schema output | Extracting structured data |
| `api_call` | HTTP request to an external API | Fetching data, triggering action |
| `database_read` | Query a database | Looking up records |
| `database_write` | Write to a database | Persisting results |
| `vector_search` | Semantic similarity search | RAG retrieval |
| `memory_read` | Read from agent memory | Recalling context |
| `memory_write` | Write to agent memory | Storing context |
| `human_input` | Pause and ask human for input | Approval, clarification |
| `notification` | Send alert or message | Slack, email, webhook |
| `image_generation` | Generate an image | Visual content |
| `audio_transcription` | Transcribe audio to text | Processing recordings |
| `sub_workflow` | Invoke another workflow | Composing workflows |
| `agent_handoff` | Pass task to another agent | Multi-agent coordination |

---

## Atomic vs. Composite Steps

**Atomic step** — a single operation, one tool call:
```yaml
- id: step_02
  name: Summarize Results
  tool: llm_completion
  input:
    from: step_01.output
    field: raw_text
  output:
    name: summary
    type: string
```

**Composite step** — a sub-workflow (reference another workflow):
```yaml
- id: step_03
  name: Generate Full Report
  tool: sub_workflow
  tool_config:
    workflow: report-generation-workflow
  input:
    from: step_02.output
    field: summary
```

---

## Decision / Branching Steps

```yaml
- id: step_04
  name: Check Data Quality
  tool: code_execution
  input:
    from: step_03.output
    field: data
  output:
    name: quality_check
    type: boolean
  on_success:
    next: "{{quality_check == true ? 'step_05_process' : 'step_05b_clean'}}"
```

Or use explicit branches:
```yaml
branches:
  - condition: "quality_check == true"
    next: step_05_process
  - condition: "quality_check == false"
    next: step_05b_clean
  - condition: "default"
    next: step_05b_clean
```

---

## Retry and Fallback Patterns

**Retry with backoff:**
```yaml
on_failure:
  strategy: retry
  max_attempts: 3
  backoff_seconds: [2, 5, 15]
  retry_on:
    - RateLimitError
    - TimeoutError
```

**Fallback to alternative step:**
```yaml
on_failure:
  strategy: fallback
  fallback_step: step_02b_manual_lookup
  alert: slack_channel_ops
```

**Human escalation:**
```yaml
on_failure:
  strategy: human_escalation
  prompt_human: "Step {{id}} failed with error: {{error}}. Please review and decide: continue, skip, or abort."
  timeout_seconds: 3600
```

---

## Input/Output Naming Conventions

- Use `snake_case` for all variable names
- Prefix with step context when referencing: `step_01.raw_results`
- Inputs from the workflow's entry point: `inputs.query`, `inputs.file_path`
- Shared memory: `memory.session_context`
- Use descriptive names, never `output1`, `data2`, `result`

Good: `step_03.validated_records`, `inputs.user_query`, `step_07.draft_report`
Bad: `out`, `data`, `result`, `step4out`
