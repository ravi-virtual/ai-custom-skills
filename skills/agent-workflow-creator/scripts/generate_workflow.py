#!/usr/bin/env python3
"""
generate_workflow.py — Scaffold a YAML agent workflow from a task description.

Usage:
    python generate_workflow.py --task "your task description" [options]

Options:
    --task TEXT          Task description (required)
    --type TEXT          Workflow type: single-agent | multi-agent | human-in-loop (default: single-agent)
    --pattern TEXT       Pattern: sequential | map-reduce | react | critic-refine | supervisor-worker
    --domain TEXT        Domain: research | data-pipeline | content | support | coding | documents
    --output TEXT        Output file path (default: workflow.yaml)
    --format TEXT        Output format: yaml | json | markdown | all (default: yaml)
    --verbose            Print detailed generation steps
"""

import argparse
import json
import sys
import textwrap
from datetime import date
from pathlib import Path


# ─── Templates ────────────────────────────────────────────────────────────────

SEQUENTIAL_TEMPLATE = """workflow:
  name: {name}
  version: "1.0.0"
  description: >
    {description}
  tags:
    - {domain}

  metadata:
    type: {workflow_type}
    domain: {domain}
    estimated_duration: "2–5 minutes"
    complexity: medium

  inputs:
    - name: task_input
      type: string
      description: Primary input for this workflow
      required: true

  outputs:
    - name: final_output
      type: file
      description: Workflow result
      from: step_final.output_file

  steps:
    - id: step_01_plan
      name: Plan Execution
      description: Analyze the task and plan the approach
      tool: llm_completion
      input:
        from: inputs
        field: task_input
      output:
        name: execution_plan
        type: json
      prompt: |
        Task: {{{{inputs.task_input}}}}
        Break this down into a clear execution plan.
        Return JSON: {{ "steps": [...], "approach": "...", "expected_output": "..." }}
      on_failure:
        strategy: retry
        max_attempts: 2
      on_success:
        next: step_02_execute

    - id: step_02_execute
      name: Execute Task
      description: Perform the primary action based on the plan
      tool: llm_completion
      input:
        from: step_01_plan.execution_plan
      output:
        name: raw_result
        type: string
      prompt: |
        Execute according to this plan: {{{{step_01_plan.execution_plan}}}}
        Task context: {{{{inputs.task_input}}}}
      on_failure:
        strategy: retry
        max_attempts: 3
      on_success:
        next: step_03_validate

    - id: step_03_validate
      name: Validate Output
      description: Check the output meets quality criteria
      tool: llm_structured
      input:
        from: step_02_execute.raw_result
      output:
        name: validation
        type: json
      prompt: |
        Validate this output: {{{{step_02_execute.raw_result}}}}
        Return JSON: {{ "passed": bool, "issues": [...], "score": 0-10 }}
      branches:
        - condition: "validation.passed == true"
          next: step_final
        - condition: "validation.passed == false"
          next: step_03b_revise

    - id: step_03b_revise
      name: Revise Output
      description: Fix issues identified in validation
      tool: llm_completion
      input:
        from: step_02_execute.raw_result
      output:
        name: revised_result
        type: string
      prompt: |
        Revise this output based on these issues: {{{{step_03_validate.validation.issues}}}}
        Original: {{{{step_02_execute.raw_result}}}}
      on_success:
        next: step_final

    - id: step_final
      name: Save Final Output
      description: Write the completed result to file
      tool: file_write
      input:
        from: step_03_validate.validation.passed
        field: "{{true ? 'step_02_execute.raw_result' : 'step_03b_revise.revised_result'}}"
      output:
        name: output_file
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
"""

REACT_TEMPLATE = """workflow:
  name: {name}
  version: "1.0.0"
  description: >
    {description}
  tags:
    - {domain}
    - react-loop

  metadata:
    type: single-agent
    domain: {domain}
    estimated_duration: "5–15 minutes"
    complexity: high

  inputs:
    - name: goal
      type: string
      description: The goal for the agent to achieve
      required: true
    - name: max_iterations
      type: number
      default: 10
      description: Maximum number of ReAct iterations

  outputs:
    - name: final_answer
      type: string
      from: step_finalize.answer

  memory:
    type: in-context
    config:
      store: in-memory

  steps:
    - id: step_init
      name: Initialize
      description: Set up the task and initial context
      tool: llm_completion
      input:
        from: inputs
        field: goal
      output:
        name: initial_plan
        type: string
      prompt: |
        You are an autonomous agent with the goal: {{{{inputs.goal}}}}
        Create an initial plan. What is the first action to take?
      on_success:
        next: step_reason

    - id: step_reason
      name: Reason
      description: Think about what action to take next
      tool: llm_structured
      input:
        from: memory
        field: action_history
      output:
        name: next_action
        type: json
      prompt: |
        Goal: {{{{inputs.goal}}}}
        Previous actions and results: {{{{memory.action_history}}}}
        What is the next best action?
        Return JSON: {{
          "thought": "my reasoning",
          "action": "tool_name",
          "action_input": "input for the tool",
          "is_done": false
        }}
      on_success:
        next: step_check_done

    - id: step_check_done
      name: Check Completion
      description: Decide whether the goal is achieved or continue
      tool: code_execution
      branches:
        - condition: "next_action.is_done == true OR iteration_count >= inputs.max_iterations"
          next: step_finalize
        - condition: "default"
          next: step_act

    - id: step_act
      name: Act
      description: Execute the chosen action
      tool: "{{{{step_reason.next_action.action}}}}"
      input:
        from: step_reason.next_action
        field: action_input
      output:
        name: observation
        type: string
      on_failure:
        strategy: fallback
        fallback_step: step_act_fallback
      on_success:
        next: step_observe

    - id: step_act_fallback
      name: Action Fallback
      description: Handle action failure gracefully
      tool: llm_completion
      prompt: |
        The action {{{{step_reason.next_action.action}}}} failed.
        Reason: {{{{error}}}}.
        What alternative approach can we take?
      on_success:
        next: step_observe

    - id: step_observe
      name: Observe and Update Memory
      description: Process the result and store in memory
      tool: memory_write
      input:
        from: step_act.observation
      on_success:
        next: step_reason   # loop back

    - id: step_finalize
      name: Finalize Answer
      description: Compile all results into a final answer
      tool: llm_completion
      prompt: |
        Goal: {{{{inputs.goal}}}}
        All actions taken: {{{{memory.action_history}}}}
        Compile a comprehensive final answer.
      output:
        name: answer
        type: string

  error_handling:
    global_timeout_seconds: 1800
    global_on_failure: human_escalation
    notification:
      channel: none

  observability:
    logging: true
    log_level: debug
    trace_steps: true
"""

SUPERVISOR_WORKER_TEMPLATE = """workflow:
  name: {name}
  version: "1.0.0"
  description: >
    {description}
  tags:
    - {domain}
    - multi-agent

  metadata:
    type: multi-agent
    domain: {domain}
    estimated_duration: "10–30 minutes"
    complexity: high

  inputs:
    - name: task
      type: string
      description: The complex task to complete
      required: true

  outputs:
    - name: final_deliverable
      type: file
      from: step_finalize.deliverable

  agents:
    - id: orchestrator
      name: Supervisor Agent
      role: Plans the task, assigns work to specialists, synthesizes results
      tools: [llm_completion, llm_structured, agent_handoff]
      model: "{{model_id}}"  # Replace with the model ID used in your environment
      system_prompt: You are a supervisor who breaks complex tasks into subtasks and coordinates specialist agents.

    - id: researcher
      name: Research Agent
      role: Gathers information from external sources
      tools: [web_search, web_fetch, memory_write]
      model: "{{model_id}}"  # Replace with the model ID used in your environment
      system_prompt: You are a research specialist. Find accurate, relevant information efficiently.

    - id: analyst
      name: Analysis Agent
      role: Processes and analyzes gathered information
      tools: [code_execution, llm_structured, memory_read]
      model: "{{model_id}}"  # Replace with the model ID used in your environment
      system_prompt: You are an analytical specialist. Process data, find patterns, and draw conclusions.

    - id: writer
      name: Writing Agent
      role: Produces the final written deliverable
      tools: [llm_completion, file_write, memory_read]
      model: "{{model_id}}"  # Replace with the model ID used in your environment
      system_prompt: You are a writing specialist. Produce clear, well-structured, professional content.

  steps:
    - id: step_01_decompose
      agent: orchestrator
      name: Decompose Task
      description: Break the complex task into specialist subtasks
      tool: llm_structured
      input:
        from: inputs
        field: task
      output:
        name: task_plan
        type: json
      prompt: |
        Break this task into subtasks for specialist agents:
        Task: {{{{inputs.task}}}}
        Return JSON: {{
          "research_tasks": [...],
          "analysis_tasks": [...],
          "writing_brief": "..."
        }}
      on_failure:
        strategy: retry
        max_attempts: 2
      on_success:
        next: [step_02_research, step_02_analyze]  # parallel fork

    - id: step_02_research
      agent: researcher
      name: Research
      description: Gather all required information
      tool: web_search
      parallel: true
      input:
        from: step_01_decompose.task_plan
        field: research_tasks
      output:
        name: research_results
        type: list
      on_failure:
        strategy: retry
        max_attempts: 3

    - id: step_02_analyze
      agent: analyst
      name: Analyze Available Data
      description: Analyze any existing data or context
      tool: code_execution
      parallel: true
      input:
        from: step_01_decompose.task_plan
        field: analysis_tasks
      output:
        name: analysis_results
        type: json
      on_failure:
        strategy: fallback
        fallback_step: step_02_analyze_fallback

    - id: step_03_synthesize
      agent: orchestrator
      name: Synthesize Results
      description: Combine research and analysis into a unified brief
      tool: llm_completion
      input:
        from: [step_02_research.research_results, step_02_analyze.analysis_results]
      output:
        name: synthesis
        type: string
      prompt: |
        Synthesize these research and analysis results into a comprehensive brief:
        Research: {{{{step_02_research.research_results}}}}
        Analysis: {{{{step_02_analyze.analysis_results}}}}
        Writing brief: {{{{step_01_decompose.task_plan.writing_brief}}}}
      on_success:
        next: step_04_write

    - id: step_04_write
      agent: writer
      name: Write Final Deliverable
      description: Produce the final output
      tool: llm_completion
      input:
        from: step_03_synthesize.synthesis
      output:
        name: draft
        type: string
      prompt: |
        Using this brief, write the final deliverable:
        {{{{step_03_synthesize.synthesis}}}}
      on_success:
        next: step_finalize

    - id: step_finalize
      agent: writer
      name: Save Deliverable
      tool: file_write
      input:
        from: step_04_write.draft
      output:
        name: deliverable
        type: file

  error_handling:
    global_timeout_seconds: 3600
    global_on_failure: human_escalation
    notification:
      channel: none

  observability:
    logging: true
    log_level: info
    trace_steps: true
"""

TEMPLATES = {
    "sequential": SEQUENTIAL_TEMPLATE,
    "react": REACT_TEMPLATE,
    "supervisor-worker": SUPERVISOR_WORKER_TEMPLATE,
}

DOMAIN_MAP = {
    "research": "research",
    "data-pipeline": "data-processing",
    "content": "content-generation",
    "support": "customer-support",
    "coding": "software-development",
    "documents": "document-processing",
}


def slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]


def generate_workflow(task: str, workflow_type: str, pattern: str, domain: str) -> str:
    """Generate a workflow YAML from a task description."""
    name = slugify(task)
    description = f"Agent workflow for: {task}"
    template = TEMPLATES.get(pattern, SEQUENTIAL_TEMPLATE)
    domain_label = DOMAIN_MAP.get(domain, domain)

    return template.format(
        name=name,
        description=description,
        workflow_type=workflow_type,
        domain=domain_label,
    )


def workflow_to_markdown(yaml_content: str, task: str, pattern: str) -> str:
    """Convert a workflow YAML to a Markdown documentation page."""
    md = f"""# Agent Workflow: {task}

**Pattern:** {pattern}  
**Generated:** {date.today().isoformat()}

## Workflow YAML

```yaml
{yaml_content}
```

## Quick Start

1. Review the workflow YAML above
2. Customize the `inputs` section for your use case
3. Configure tool credentials in `tool_config` for each step
4. Run validation: `python validate_workflow.py --file workflow.yaml`
5. Execute: load the YAML into your agent framework

## Pre-flight Checklist

- [ ] All required tools available and authenticated
- [ ] Input data matches the `inputs` schema
- [ ] Output destinations writable
- [ ] Rate limits checked for external APIs
- [ ] Logging/observability configured
- [ ] Test run completed on sample data
"""
    return md


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a YAML agent workflow from a task description."
    )
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument(
        "--type", default="single-agent",
        choices=["single-agent", "multi-agent", "human-in-loop"],
        help="Workflow type"
    )
    parser.add_argument(
        "--pattern", default="sequential",
        choices=["sequential", "react", "supervisor-worker", "map-reduce", "critic-refine"],
        help="Workflow pattern"
    )
    parser.add_argument(
        "--domain", default="general",
        choices=["research", "data-pipeline", "content", "support", "coding", "documents", "general"],
        help="Domain"
    )
    parser.add_argument("--output", default="workflow.yaml", help="Output file path")
    parser.add_argument(
        "--format", default="yaml",
        choices=["yaml", "json", "markdown", "all"],
        help="Output format"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        print(f"Generating workflow for: {args.task}")
        print(f"Type: {args.type}, Pattern: {args.pattern}, Domain: {args.domain}")

    yaml_content = generate_workflow(args.task, args.type, args.pattern, args.domain)

    output_path = Path(args.output)

    if args.format in ("yaml", "all"):
        yaml_path = output_path if args.format == "yaml" else output_path.with_suffix(".yaml")
        yaml_path.write_text(yaml_content)
        print(f"✅ YAML workflow written to: {yaml_path}")

    if args.format in ("json", "all"):
        try:
            import yaml
            data = yaml.safe_load(yaml_content)
            json_path = output_path.with_suffix(".json")
            json_path.write_text(json.dumps(data, indent=2))
            print(f"✅ JSON workflow written to: {json_path}")
        except ImportError:
            print("⚠️  PyYAML not installed — skipping JSON output. Install with: pip install pyyaml")

    if args.format in ("markdown", "all"):
        md_content = workflow_to_markdown(yaml_content, args.task, args.pattern)
        md_path = output_path.with_suffix(".md")
        md_path.write_text(md_content)
        print(f"✅ Markdown docs written to: {md_path}")

    if args.verbose:
        print("\n── Preview ──────────────────────────────────────")
        print(yaml_content[:800] + "..." if len(yaml_content) > 800 else yaml_content)


if __name__ == "__main__":
    main()
