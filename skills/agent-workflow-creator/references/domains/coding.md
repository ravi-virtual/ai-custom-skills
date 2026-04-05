# Code Generation & Review Workflows

Domain-specific guidance for building agent workflows that generate, review, test, refactor, and maintain code.

---

## Core Challenges in Coding Workflows

- **Context window limits** — large codebases don't fit in a prompt; retrieval is essential
- **Correctness is binary at the edges** — code either compiles and tests pass, or it doesn't
- **Dependency chains** — a change in one file ripples to others
- **Security sensitivity** — generated code may contain vulnerabilities if not reviewed
- **Style consistency** — output must match the existing codebase's conventions

---

## Workflow Archetypes

### A. Code Generation (from spec)
Turn a requirement, ticket, or natural language description into working code.

**Steps:**
1. Parse requirement → extract: language, framework, function signature, constraints
2. Retrieve relevant codebase context (existing utils, patterns, types) via vector search
3. Generate implementation draft
4. Run static analysis / linter
5. Run existing tests; if failures → fix and retry (up to N times)
6. Generate or update unit tests for new code
7. Open PR or return diff for human review

**Key tools:** `vector_search` (codebase RAG), `code_execution`, `file_io`, `llm_completion`

---

### B. Code Review
Review a PR or diff for bugs, security issues, style violations, and logic errors.

**Steps:**
1. Fetch diff (PR, file diff, or pasted code)
2. Parse changed files → identify scope and intent
3. Retrieve context for each changed file (callers, dependencies, tests)
4. Run automated checks: lint, type check, SAST scan
5. LLM review pass: logic correctness, edge cases, error handling
6. Security scan pass: injection, auth, secrets exposure, input validation
7. Style / convention check against repo standards
8. Aggregate findings → categorize as: blocker / warning / suggestion / praise
9. Generate structured review comment per finding
10. Post review or return report

**Key tools:** `code_execution` (lint/tests), `vector_search`, `llm_completion`, `api_call` (GitHub/GitLab)

---

### C. Refactoring
Improve existing code without changing external behavior.

**Steps:**
1. Identify refactoring target (function, module, pattern)
2. Capture existing tests as ground truth (if none: generate characterization tests first)
3. Retrieve all callers and dependents via codebase search
4. Apply refactor (extract method, rename, simplify, optimize)
5. Run full test suite — must all pass
6. Run performance benchmarks if optimization was the goal
7. Update documentation and inline comments
8. Generate diff for review

**Key tools:** `code_execution`, `file_io`, `vector_search`, `llm_completion`

---

### D. Bug Investigation
Given an error, stack trace, or failing test: find and fix the root cause.

**Steps:**
1. Parse error message → extract file, line, error type
2. Fetch relevant source files + recent git history for those files
3. Reproduce the error in a sandbox if possible
4. Hypothesize root cause (LLM reasoning pass)
5. Trace backward through call stack to confirm hypothesis
6. Generate fix
7. Write regression test for this specific bug
8. Run full test suite to confirm no side effects

**Key tools:** `code_execution`, `file_io`, `api_call` (git log, blame), `llm_completion`

---

## Control Flow Patterns for Coding

### Test-Repair Loop
```
GENERATE code
WHILE test_suite fails AND attempts < max_attempts:
  READ failure output
  IDENTIFY failing test + reason
  PATCH code
  RUN tests again
IF still failing:
  ESCALATE to human with context
```

### Confidence-Gated Commit
```
IF lint_errors == 0 AND test_pass_rate == 100% AND security_score > threshold:
  → Auto-commit / auto-merge
ELSE IF minor_warnings_only:
  → Stage for human 1-click approval
ELSE:
  → Block and surface issues to developer
```

---

## Context Retrieval Strategy

Don't dump the whole codebase — retrieve surgically:
- **Semantic search** for similar functions or patterns
- **Symbol lookup** for the exact function/class being modified
- **Call graph** for who calls what
- **Test file** for the module under change
- **Recent git log** for the file (understand intent of recent changes)

Start narrow; widen retrieval only if needed.

---

## Error Handling

| Failure Type | Recovery Strategy |
|---|---|
| Tests fail after max retries | Return partial work with failure summary; escalate |
| Linter reports unfixable errors | Flag and continue; note in output |
| Codebase retrieval returns no relevant context | Proceed with generation; flag as low-context |
| Code execution sandbox timeout | Increase timeout; if still fails, flag for manual run |
| Security scan finds P0 issue | Block output entirely; require human review |

---

## Quality Gates (apply before any output)

- [ ] Code compiles without errors
- [ ] All existing tests pass
- [ ] No new linter errors introduced
- [ ] No hardcoded secrets or credentials
- [ ] All new functions have docstrings/comments
- [ ] Edge cases (null, empty, overflow) handled
- [ ] Performance: no O(n²) loops on unbounded input
- [ ] Security: inputs validated, outputs sanitized

---

## Anti-Patterns to Avoid

- **Generating without codebase context** — produces code that ignores existing patterns and introduces duplication
- **Skipping tests** — "looks right" is not a passing test
- **Giant PRs** — break into small, reviewable changes
- **Auto-merging without human gate** — always keep a human in the loop for production code
- **Silently swallowing errors** — every `try/catch` without a log is a future mystery
