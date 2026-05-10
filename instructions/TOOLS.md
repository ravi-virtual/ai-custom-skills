# TOOLS.md — Tool Usage Reference

## Available Tools & Usage Rules

This file documents every tool available to AI agents in this system, how to use them correctly, and when each is appropriate.

---

## Tool 1: file_read

**Purpose**: Read the contents of a file in the workspace.

**When to use**:
- Before modifying any file (always read before write)
- To load context files at session start
- To verify current state of a file before making assumptions

**Usage rules**:
- Never assume file contents — always read first
- Read the FULL file, not just the section you think you need
- After reading, confirm the content matches your expectations before acting

**When NOT to use**:
- Don't read files unnecessarily (adds to context window)
- Don't read the same file multiple times in the same session without reason

---

## Tool 2: file_write

**Purpose**: Create or modify files in the workspace.

**When to use**:
- After reading the file and planning the changes
- When creating new files from established templates

**Usage rules**:
- Always read the file first (file_read) before writing
- Never overwrite files without being certain of the change
- For partial updates: read → modify → write the complete updated content
- Always produce COMPLETE file contents — no truncation with "// ..."
- Confirm the write path matches the project structure in ARCHITECTURE.md

**When NOT to use**:
- Don't write files in CONSTRAINTS.md-protected locations without human approval
- Don't overwrite AGENT_RULES.md or CONSTRAINTS.md without explicit human instruction

---

## Tool 3: code_execution

**Purpose**: Execute code snippets to verify logic, run tests, or validate behavior.

**When to use**:
- To verify a complex algorithm produces correct output
- To run unit tests and confirm they pass
- To check that a refactored function produces the same output as the original
- To validate JSON/YAML structure

**Usage rules**:
- Never execute code that writes to the database in production mode
- Always review code before executing it (even your own)
- Capture and analyze the full output, including error messages
- Don't trust the code until execution confirms it

**When NOT to use**:
- Don't execute code that could modify production state
- Don't execute code requiring production credentials

---

## Tool 4: web_search

**Purpose**: Search the internet for information about libraries, APIs, error messages, or documentation.

**When to use**:
- When internal knowledge (KNOWLEDGE_BASE.md, MEMORY.md) doesn't have the answer
- To verify a specific library version's API behavior
- To research a specific error message from a third-party library
- To find official documentation for an external service

**Usage rules**:
- Check internal sources FIRST (KNOWLEDGE_BASE.md, MEMORY.md, STACK.md)
- Formulate specific queries: `"express-validator v7 isEmail 2024"` not `"how to validate email"`
- Verify search results against current stack versions (STACK.md)
- After confirming a fact, add it to KNOWLEDGE_BASE.md

**When NOT to use**:
- Don't search for things already in KNOWLEDGE_BASE.md
- Don't search for internal architectural decisions (check DECISIONS.md instead)

---

## Tool 5: llm_completion

**Purpose**: Use language model capabilities for reasoning, code generation, explanation, and analysis.

**When to use**:
- For code generation following established patterns
- For analyzing complex code and identifying issues
- For writing documentation and explanations
- For reasoning through trade-offs in design decisions

**Usage rules**:
- Load relevant context (MEMORY.md patterns, CODING_STANDARDS.md) BEFORE generating code
- Apply the correct skill pattern (CLAUDE.md → Skill Activation Map) for the task type
- Validate generated code against AGENT_RULES.md before delivering
- State confidence level when making decisions

**Quality gates before delivering llm_completion output**:
- [ ] Follows CODING_STANDARDS.md
- [ ] Passes SECURITY.md review
- [ ] Complete error handling
- [ ] No placeholders or TODOs

---

## Tool 6: log_analysis

**Purpose**: Analyze server logs, error logs, or console output to identify issues.

**When to use**:
- During the TRACE phase of debugging
- When server behavior doesn't match expected behavior
- To identify patterns in repeated errors

**Usage rules**:
- Look for the FIRST error in a log sequence (subsequent errors may be cascades)
- Search for the exact error type, not just the message
- Cross-reference with FAILURES.md before starting analysis

---

## Tool 7: test_runner

**Purpose**: Execute automated tests (Jest, Supertest, etc.) to validate code.

**When to use**:
- After implementing a new feature
- After fixing a bug (verify the fix and no regression)
- Before deployment (full test suite)

**Usage rules**:
- Run the minimal test scope for the change (unit first, then integration)
- Fix test failures before delivering code — never ship failing tests
- If tests don't exist for the changed code, note this gap

---

## Tool Selection Decision Tree

```
"What tool do I need?"
    ↓
Do I need to read a file?
    YES → file_read
    NO  ↓
Do I need to write a file?
    YES → [file_read first] → file_write
    NO  ↓
Do I need to verify code logic?
    YES → code_execution
    NO  ↓
Do I need external information?
    YES → [check KNOWLEDGE_BASE.md first] → web_search if not found
    NO  ↓
Do I need to analyze logs?
    YES → log_analysis
    NO  ↓
Do I need to run tests?
    YES → test_runner
    NO  ↓
Default → llm_completion (reasoning/generation)
```

---

## Tool Chaining Patterns

### Pattern: Safe File Update
```
file_read(target_file)
→ llm_completion(plan the changes)
→ file_write(complete updated content)
→ code_execution(verify the change if it's executable code)
```

### Pattern: Research-Driven Implementation
```
web_search(specific technology question)
→ llm_completion(apply research to implementation)
→ file_write(implementation)
→ knowledge_base.add(verified fact from research)
```

### Pattern: Bug Investigation
```
log_analysis(error logs)
→ file_read(affected files)
→ llm_completion(form hypothesis)
→ file_write(add // [DEBUG] instrumentation)
→ code_execution(if testable)
→ llm_completion(confirm root cause)
→ file_write(apply fix)
→ file_write(remove // [DEBUG] logs)
```
