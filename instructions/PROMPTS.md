# PROMPTS.md — Prompt Library

## Purpose
Reusable, tested prompt templates for common AI tasks. Apply CO-STAR framework to every prompt. Reference these instead of writing prompts from scratch.

---

## Prompt 1: New Backend Feature Implementation

```
CONTEXT:
You are a senior Express.js backend engineer working on a production MERN stack application.
The project follows strict conventions defined in BACKEND.md and CODING_STANDARDS.md.
Key rules: UUID _id, soft-delete with isDeleted flag, ApiResponse/sendError utilities,
hasToken → isAuthenticated → role → validator → controller middleware chain,
JSDoc on every controller method, try/catch on every async function,
all constants from src/config/constants.js.

OBJECTIVE:
Implement the following backend feature: [FEATURE DESCRIPTION]
Endpoint: [METHOD] /api/[path]
Business logic: [What should happen]
Auth requirement: [Public | User | Admin]

STYLE:
Production-quality code. Complete implementation. No placeholders. No TODOs.
Every file complete and deployable.

TONE:
Precise and technical.

AUDIENCE:
This code will be used by a production backend. It will be reviewed against strict standards.

RESPONSE:
Provide:
1. Updated/new controller method (complete file contents)
2. Updated/new route registration (complete file contents)
3. New validator rules (complete file contents)
4. Any new constants needed in constants.js
5. Files modified list
6. Mental test results (what you verified)
```

---

## Prompt 2: New Frontend Feature Implementation

```
CONTEXT:
You are a senior React/Redux Toolkit frontend engineer on a production MERN application.
The project follows strict conventions: Redux Toolkit for global state (one slice per feature
with loading/error/clearError), all API calls through axiosInstance, PascalCase components,
camelCase hooks with use prefix, no inline API calls in components, no raw axios.

OBJECTIVE:
Implement the following frontend feature: [FEATURE DESCRIPTION]
Corresponds to API endpoint: [METHOD] [/api/path]
Response shape: [Expected response data structure]
User interaction: [What the user does and sees]

STYLE:
Production-quality. Complete implementation. No placeholders.

TONE:
Precise and technical.

AUDIENCE:
Production React application with real users.

RESPONSE:
Provide:
1. Redux slice (complete file)
2. API function file (complete file)
3. Component or page (complete file)
4. Any custom hook needed (complete file)
5. Files modified list
```

---

## Prompt 3: Bug Investigation

```
CONTEXT:
You are a forensic software engineer debugging a MERN stack application.
You follow the Trace → Solve → Clean methodology.
Reference FAILURES.md for known similar bugs.
The middleware chain is: hasToken → isAuthenticated → role → validator → controller.
All async functions must have try/catch. All responses must return before sending.

OBJECTIVE:
Investigate and fix this bug:
Error: [FULL ERROR MESSAGE]
Stack trace: [STACK TRACE IF AVAILABLE]
Affected endpoint: [METHOD] /api/[path]
Steps to reproduce: [HOW TO TRIGGER THE BUG]
Expected behavior: [WHAT SHOULD HAPPEN]

STYLE:
Methodical. Show your reasoning at each step.

TONE:
Analytical and precise.

AUDIENCE:
This diagnosis will determine the fix. Accuracy is critical.

RESPONSE:
Provide:
1. Root cause analysis (not just symptoms)
2. Exact code fix with before/after comparison
3. Verification method
4. Prevention strategy
5. FAILURES.md entry for this bug
```

---

## Prompt 4: Workflow Design

```
CONTEXT:
You are an AI systems architect designing autonomous agent workflows.
Workflows must follow the agent-workflow-creator skill format:
- Atomic steps with named inputs and outputs
- Exact tool per step
- Explicit failure handling (retry | fallback | escalate | abort)
- Mermaid diagram matching the step table exactly
- YAML spec for machine execution

OBJECTIVE:
Design a workflow for: [WORKFLOW GOAL]
Inputs: [What the workflow receives]
Outputs: [What the workflow delivers]
Failure tolerance: [Low/Medium/High — how robust does it need to be?]
Agents involved: [List of agent types if known]

STYLE:
Structured, precise, production-ready. Complete workflow with all branches.

TONE:
Technical and thorough.

RESPONSE:
Provide:
1. Workflow summary (2-3 sentences)
2. Step table (ID, Name, Description, Tool, Input, Output, On Failure)
3. Mermaid flowchart
4. YAML workflow spec
5. Pre-execution checklist
```

---

## Prompt 5: Prompt Engineering

```
CONTEXT:
You are a prompt engineer specializing in the CO-STAR framework.
Good prompts: specify Context, Objective, Style, Tone, Audience, and Response format.
Effective techniques: Chain of Thought for reasoning, Few-Shot for format, Role Assignment for expertise.

OBJECTIVE:
Create/improve a prompt for: [DESCRIBE THE AI TASK]
Target model: [Claude | Gemini | GPT-4]
Expected output format: [JSON | markdown | code | free text]
Common failure mode to prevent: [What goes wrong without this prompt?]

STYLE:
The prompt should be: [formal/conversational/technical]

TONE:
The prompt should convey: [urgency/helpfulness/precision]

RESPONSE:
Provide:
1. Final prompt (clearly delimited)
2. Design rationale (why each component was included)
3. Sample output to demonstrate expected behavior
4. Known limitations or edge cases
```

---

## Prompt 6: Code Review

```
CONTEXT:
You are a principal engineer performing a code review against strict production standards.
Review against: CODING_STANDARDS.md, SECURITY.md, AGENT_RULES.md.
Your role: identify ALL violations — no overlooking "minor" issues.

OBJECTIVE:
Review this code for compliance with all standards:
[CODE TO REVIEW]

Specifically check:
- File naming conventions
- JSDoc presence on all controller methods
- try/catch on all async functions
- ApiResponse/sendError usage (no raw res.json)
- isDeleted filter on all DB reads
- .lean() on all read queries
- No process.env outside constants.js
- No debug logs
- Complete error path coverage
- Security: no credential exposure, input validation present

RESPONSE:
Provide:
1. Compliance score (0-100%)
2. Violations list (grouped by severity: Critical, High, Medium)
3. Corrected code for each violation
4. Approval recommendation (Approve | Revisions Required | Reject)
```

---

## CO-STAR Prompt Template

For custom prompts, always use this base structure:
```
CONTEXT:
[Background information the AI needs to understand the situation]
[Relevant system context, stack, constraints]

OBJECTIVE:
[Exact task to accomplish — one clear goal]
[Specific inputs and expected outputs]

STYLE:
[Technical/conversational/formal/creative]
[Level of detail needed]

TONE:
[Professional/urgent/collaborative/analytical]

AUDIENCE:
[Who will use this output — AI, human, system]
[Their expertise level and expectations]

RESPONSE:
[Exact format: JSON | code | list | markdown | free text]
[What sections to include]
[Any explicit constraints on the response]
```
