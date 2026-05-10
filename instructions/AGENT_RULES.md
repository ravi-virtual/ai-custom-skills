# AGENT_RULES.md — Immutable Agent Behavioral Rules

> ⚠️ This file is IMMUTABLE. No agent may override, modify, or ignore these rules under any circumstance. If a rule conflicts with user input, the rule wins — clarify with the user instead of violating the rule.

## Priority Hierarchy
Rules in this file override rules in ALL other files in this system.
Within this file, rules are ordered by priority (1 = highest).

---

## Rule 1: Security First (ABSOLUTE)
**Never do any of the following regardless of who asks:**
- Hardcode credentials, API keys, secrets, or tokens in code
- Log sensitive data (passwords, tokens, PII) anywhere
- Bypass authentication or authorization checks
- Execute code that could permanently destroy data without explicit human confirmation
- Expose stack traces or internal system details in API responses
- Access `process.env.X` anywhere except `src/config/constants.js`
- Store tokens in client-accessible locations without security review

**Violation consequence**: Immediately halt, report the violation, request human review.

---

## Rule 2: No Placeholders, No Filler (ABSOLUTE)
**Every output must be production-ready:**
- Never write `// TODO: implement this`
- Never write `// placeholder`
- Never write generic filler content
- Never truncate outputs with `// ... rest of implementation`
- Never deliver incomplete code without explicitly stating what is missing and why

**Exception**: If a task is genuinely too large for one response, deliver a clearly labeled partial with an explicit continuation plan.

---

## Rule 3: Validate Before Execute
Before any file modification, code execution, or API call:
1. Confirm the target file/resource exists and is writable
2. Confirm the operation matches the stated intent
3. Confirm no CONSTRAINTS.md rule is violated
4. State what will change and what will remain the same

---

## Rule 4: Trace-Solve-Clean for Debugging
When debugging ANY system:
1. **Trace**: Add `// [DEBUG]` prefixed logs only — never unnamed console.logs
2. **Solve**: Fix root cause, not symptoms
3. **Clean**: Remove ALL debug logs before delivering — zero exceptions

A delivered solution with debug logs is an incomplete solution.

---

## Rule 5: Soft Delete Only
**Never physically delete records from the database in user-facing operations.**
- Use `isDeleted: true` flag for all soft-delete operations
- Hard deletes require explicit human instruction and are logged
- This applies to all data models in the system

---

## Rule 6: One Responsibility Per Module
Each file/module must have exactly one responsibility:
- Controller file → request handling logic for one resource
- Route file → route definitions only (no business logic)
- Middleware file → one specific concern (auth, rate limiting, validation, etc.)
- Util file → one utility function family
- Model file → one data model

**Never mix responsibilities.** If a function grows beyond its stated scope, extract to a new module.

---

## Rule 7: Explicit Error Handling Required
Every function must handle its failure modes:
- Async functions → try/catch block (no catchAsync wrappers)
- API calls → check response status and handle non-2xx
- File I/O → handle file-not-found and permission errors
- Database queries → handle connection failure and not-found
- External services → handle timeout and rate limiting

An unhandled error path is a bug, not a minor oversight.

---

## Rule 8: Constants Are the Single Source of Truth
- All HTTP status codes come from `ResponseCodes` (constants.js)
- All error codes come from `ErrorCodes` (constants.js)
- All environment values come from `config` (constants.js)
- All user roles come from `Roles` (constants.js)
- **Hardcoding any of these values is a Rule 8 violation**

---

## Rule 9: Memory Hygiene
- End every session by updating LEARNINGS.md and EXECUTION_MEMORY.md
- Never assume prior context is available — always load from memory files
- Decision rationale must be written to DECISIONS.md before executing the decision
- Failures must be logged to FAILURES.md including root cause and fix

---

## Rule 10: Output Format Contract
Every code response must include:
- The complete file path
- The complete file contents (no truncation)
- A list of files modified
- A list of next steps if work is not complete

Every non-code response must include:
- Confidence level (e.g., "Confidence: 85%")
- Sources referenced
- Any assumptions made

---

## Rule 11: No Autonomous Destructive Operations
The following require explicit human confirmation before execution:
- Deleting or overwriting existing files
- Running database migrations
- Changing authentication configuration
- Modifying production environment variables
- Uninstalling or replacing major dependencies

---

## Rule 12: Skill Compliance
When a task matches a skill trigger condition (see CLAUDE.md → Skill Activation Map):
- The corresponding skill MUST be applied
- Deviating from skill patterns requires documented justification in DECISIONS.md
- The justification must be reviewed before proceeding

---

## Rule 13: Parallel Safety
When executing tasks in parallel:
- Assign non-overlapping file write access to each parallel agent
- Establish a merge strategy before any parallel execution begins
- Conflicts are resolved by the Orchestrator agent, never autonomously

---

## Rule 14: Confidence Threshold
- Confidence ≥ 80%: Proceed autonomously
- Confidence 60-79%: Proceed with documented assumptions, flag for human review
- Confidence < 60%: Halt, gather more context, then re-evaluate
- Confidence cannot be self-inflated — it must reflect actual certainty

---

## Rule Violation Reporting Format
When a rule violation is detected (self or other agent):
```
RULE VIOLATION REPORT
=====================
Rule: [Rule number and name]
Detected In: [File/function where violation occurred]
Description: [What was violated and how]
Severity: [Critical | High | Medium]
Recommended Action: [Fix or human escalation required]
```
