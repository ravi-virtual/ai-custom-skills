---
name: prompt-writing
description: Writes, rewrites and tests high-quality prompts for LLMs - system prompts, chatbot and agent instructions, extraction/classification prompts, coding-assistant prompts and reusable prompt templates. Use when the user asks to create a prompt, improve or debug a prompt that gives inconsistent or wrong output, make output follow a format (JSON, table, style), add few-shot examples, or turn a vague idea into a robust prompt. Delivers the prompt plus a short rationale and test cases. Not for designing multi-step agent pipelines (use agent-workflow-creator).
---

# Prompt Writing

A prompt is a spec for a reader that has no context except what you give it. Good prompts state the goal, the context, the constraints, the input and the exact output wanted, and they are tested on real inputs before delivery.

## Workflow

1. **Pin down the job.** Ask only for what is missing: what the model must do, who or what consumes the output (a person, a parser, another prompt), the input data and its variability, the target model, and what a bad answer looks like. If the user supplied an existing prompt, ask for one input where it fails.
2. **Draft** using the structure below.
3. **Lint**: `python scripts/analyze_prompt.py prompt.txt` flags missing structure, vague words and unresolved placeholders. It is a checklist, not a judge.
4. **Test.** Write 3 to 5 test inputs: a typical case, an edge case, a malformed/adversarial case, and one where the correct answer is "not enough information". Run them if you can, otherwise walk through the likely output and fix gaps.
5. **Deliver** the prompt in one code block, then a short "why it is built this way" list, the variables to fill, and the test cases.

## Structure of a strong prompt

Include these parts, in this order, dropping any that do not apply:

| Part | What goes in it |
|---|---|
| Role (1 line) | Who the model acts as, only if it changes the answer (domain, seniority, stance) |
| Context | Background and the reason behind the task; purpose lets the model make good judgment calls |
| Task | One clear instruction in the imperative; the success criterion |
| Rules | Constraints as positive instructions ("Answer in two sentences") rather than lists of prohibitions |
| Input | The variable data, fenced with XML tags: `<document>...</document>` |
| Examples | 2 to 5 varied, realistic examples in `<example>` tags (input and ideal output) |
| Output format | Exact shape: JSON schema, headings, length, language, what to do if info is missing |

Put long input documents **before** the final question or task, and repeat the key instruction at the end for long prompts.

## Techniques and when to reach for them

| Technique | Use when | How |
|---|---|---|
| Be direct and specific | Always | Replace "good/brief/etc." with measurable terms ("max 80 words", "3 bullet points") |
| Explain the why | A rule seems arbitrary | "Never use ellipses because the output is read aloud" |
| XML tags | Mixed instructions, data and examples | Consistent tag names; refer to them in the instructions ("using the text in `<report>`") |
| Few-shot examples | Format or tone is hard to describe | Cover the range of inputs including an edge case; keep examples consistent with the rules |
| Reasoning first | Math, logic, multi-factor decisions | Ask for reasoning in `<analysis>` tags, then the answer in `<answer>`; strip the analysis if a parser consumes the output |
| Quote then answer | Long documents | "First extract the relevant quotes, then answer using only them" |
| Structured output | A program reads the result | Give the JSON schema, one valid example, and "Return only JSON"; validate in code, do not trust the prompt alone |
| Chain prompts | One prompt does too many jobs | Split: extract, then analyse, then write; pass outputs forward |
| Escape hatch | Hallucination risk | "If the answer is not in the document, reply `NOT_FOUND`" |
| Role/persona | Tone or domain expertise matters | One sentence in the system prompt; do not stack personas |

Frameworks such as CO-STAR (Context, Objective, Style, Tone, Audience, Response) or RTF (Role, Task, Format) are useful checklists for prose tasks; the table above is the superset.

## Improving an existing prompt

1. Run the linter and read the prompt as the model would, with no background knowledge.
2. Find the failure: ambiguous task, missing context, conflicting rules, format not specified, no handling for odd inputs.
3. Change one thing at a time and re-run the same test inputs; keep a before/after note.
4. Remove instructions that are shouted (ALL CAPS, "CRITICAL") unless truly needed; replace them with the reason behind the rule.

## Anti-patterns

- Long lists of "do not" rules with no positive instruction
- Contradictory rules ("be brief" and "explain in detail")
- Hidden assumptions about audience or domain terms
- Examples that all look alike (the model copies them)
- Asking for JSON in prose and then parsing without validation
- One mega-prompt that classifies, extracts, reasons and writes at once
- Leaving placeholders (`{{name}}`, `[TODO]`) in the delivered prompt

## References

- `references/prompt_engineering_guide.md` - worked examples: few-shot, personas, XML tagging, self-critique loops, system prompts
- `scripts/analyze_prompt.py` - structural linter (`--json`, stdin supported)
