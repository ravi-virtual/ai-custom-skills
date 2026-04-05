# YAML Workflow Schema

Full machine-readable specification for agent workflows. All generated workflows must conform to this schema.

## Top-Level Structure

```yaml
workflow:
  name: string              # Kebab-case identifier, e.g. "research-report-generator"
  version: string           # Semantic version, e.g. "1.0.0"
  description: string       # Plain-English description (1–3 sentences)
  author: string            # Optional: who created this
  created_at: string        # ISO 8601 date, e.g. "2025-01-15"
  tags:                     # Categorization labels
    - string

  # ─── METADATA ─────────────────────────────────────────────────────────────
  metadata:
    type: string            # "single-agent" | "multi-agent" | "human-in-loop"
    domain: string          # e.g. "research", "data-processing", "content"
    estimated_duration: string  # e.g. "2–5 minutes", "10–30 seconds"
    complexity: string      # "low" | "medium" | "high"

  # ─── INPUTS ───────────────────────────────────────────────────────────────
  inputs:
    - name: string          # Variable name (snake_case)
      type: string          # string | number | boolean | list | json | file
      description: string   # What this input is
      required: boolean
      default: any          # Default value if not provided
      validation:
        pattern: string     # Regex (for strings)
        min: number         # Min value (for numbers)
        max: number         # Max value (for numbers)
        allowed_values:     # Enum constraint
          - string

  # ─── OUTPUTS ──────────────────────────────────────────────────────────────
  outputs:
    - name: string          # Output variable name
      type: string          # string | number | boolean | list | json | file
      description: string
      from: string          # Which step produces this, e.g. "step_07.final_report"

  # ─── AGENTS ───────────────────────────────────────────────────────────────
  # (only required for multi-agent workflows)
  agents:
    - id: string            # Agent identifier, e.g. "researcher"
      name: string          # Display name, e.g. "Research Agent"
      role: string          # Plain description of role
      tools:                # Tools this agent has access to
        - string
      model: string         # LLM model to use
      system_prompt: string # System/persona prompt for this agent

  # ─── MEMORY / SHARED STATE ───────────────────────────────────────────────
  memory:
    type: string            # "none" | "in-context" | "vector-store" | "key-value"
    config:
      store: string         # e.g. "redis", "chromadb", "in-memory"
      ttl_seconds: int      # Time-to-live for stored data

  # ─── STEPS ────────────────────────────────────────────────────────────────
  steps:
    - id: string
      name: string
      description: string
      agent: string         # Which agent (if multi-agent)
      tool: string
      tool_config: object   # Tool-specific config (varies by tool)
      input:
        from: string        # "inputs", "step_XX.output_name", "memory.key"
        field: string
        transform: string   # Optional: transformation expression
      output:
        name: string
        type: string
      prompt: string        # For LLM steps (supports {{variable}} interpolation)
      condition: string     # For decision steps
      branches:             # For multi-branch steps
        - condition: string
          next: string
      on_success:
        next: string
      on_failure:
        strategy: string    # retry | fallback | abort | human_escalation
        max_attempts: int
        backoff_seconds:
          - int
        fallback_step: string
        alert: string
      parallel: boolean
      timeout_seconds: int
      notes: string

  # ─── ERROR HANDLING ───────────────────────────────────────────────────────
  error_handling:
    global_timeout_seconds: int
    global_on_failure: string   # "abort" | "human_escalation" | "partial_output"
    notification:
      channel: string           # "slack" | "email" | "webhook" | "none"
      endpoint: string

  # ─── OBSERVABILITY ────────────────────────────────────────────────────────
  observability:
    logging: boolean
    log_level: string         # "debug" | "info" | "warn" | "error"
    trace_steps: boolean      # Log each step's inputs and outputs
    metrics:
      - name: string
        description: string
```

---

## Complete Example: Research Report Workflow

```yaml
workflow:
  name: research-report-generator
  version: "1.0.0"
  description: >
    Given a research topic, searches the web for relevant sources, extracts key
    information, and generates a structured report with citations.
  tags:
    - research
    - content-generation

  metadata:
    type: single-agent
    domain: research
    estimated_duration: "3–8 minutes"
    complexity: medium

  inputs:
    - name: topic
      type: string
      description: The research topic or question
      required: true
    - name: depth
      type: string
      description: Research depth level
      required: false
      default: "standard"
      validation:
        allowed_values: ["quick", "standard", "deep"]
    - name: output_format
      type: string
      required: false
      default: "markdown"
      validation:
        allowed_values: ["markdown", "json", "html"]

  outputs:
    - name: report
      type: file
      description: The final research report
      from: step_06.report_file

  steps:
    - id: step_01
      name: Plan Research Queries
      tool: llm_completion
      input:
        from: inputs
        field: topic
      output:
        name: search_queries
        type: list
      prompt: |
        Given the research topic: "{{inputs.topic}}"
        Generate 3–5 targeted web search queries to comprehensively cover this topic.
        Return as a JSON list of query strings.
      on_failure:
        strategy: retry
        max_attempts: 2
      on_success:
        next: step_02

    - id: step_02
      name: Execute Web Searches
      tool: web_search
      parallel: true
      input:
        from: step_01.search_queries
        field: each_query
      output:
        name: raw_results
        type: list
      on_failure:
        strategy: fallback
        fallback_step: step_02b_cached_search
      on_success:
        next: step_03

    - id: step_03
      name: Extract Key Information
      tool: llm_structured
      input:
        from: step_02.raw_results
      output:
        name: extracted_facts
        type: json
      prompt: |
        From these search results, extract:
        - Key facts and findings
        - Source URLs and titles
        - Any conflicting information
        Return as structured JSON.
      on_failure:
        strategy: human_escalation
        prompt_human: "Extraction failed. Please review raw results and provide key facts."
      on_success:
        next: step_04

    - id: step_04
      name: Validate Fact Quality
      tool: code_execution
      input:
        from: step_03.extracted_facts
      output:
        name: quality_passed
        type: boolean
      branches:
        - condition: "quality_passed == true"
          next: step_05
        - condition: "quality_passed == false"
          next: step_04b_enrich

    - id: step_05
      name: Generate Report Draft
      tool: llm_completion
      input:
        from: step_03.extracted_facts
      output:
        name: draft_report
        type: string
      prompt: |
        Write a comprehensive research report on "{{inputs.topic}}" using these facts:
        {{step_03.extracted_facts}}
        Format: {{inputs.output_format}}
        Include: Executive Summary, Findings, Sources, Conclusion.
      on_success:
        next: step_06

    - id: step_06
      name: Save Report to File
      tool: file_write
      input:
        from: step_05.draft_report
      output:
        name: report_file
        type: file
      on_failure:
        strategy: retry
        max_attempts: 2

  error_handling:
    global_timeout_seconds: 600
    global_on_failure: human_escalation
    notification:
      channel: none

  observability:
    logging: true
    log_level: info
    trace_steps: true
```

---

## Validation Rules

A valid workflow MUST:
1. Have a unique `id` for every step
2. Have every `next` reference point to a real step ID
3. Have `on_failure` defined for every step with an external tool call
4. Have all `input.from` references resolve to a real input, step, or memory key
5. Have at least one step whose `next` is not defined (the terminal step)
6. Have all declared `outputs` reference a real step output
7. Have no circular dependencies (unless explicitly using a retry loop with a max_iterations cap)
