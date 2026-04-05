---
name: debug-sailsjs-error
description: Specialist skill for debugging Sails.js backend applications. Use this skill when the user encounters Sails.js-specific errors such as Waterline ORM issues, action/helper failures, policy blocks, or route misconfigurations. This skill implements a "Trace, Solve, Clean" workflow to ensure issues are resolved systematically and all temporary debugging code is removed.
---

# Debug-SailsJS-Error

A specialized skill for identifying and resolving issues in Sails.js backends with a clean-up guarantee.

## Core Workflow: Trace, Solve, Clean

Whenever you encounter a Sails.js error (Waterline errors, action crashes, policy failures, route issues, etc.), you MUST follow this three-step process:

### 1. Trace (Identify Root Cause)

- **Analyze**: Inspect the Sails.js server log (`sails lift` output) for stack traces or exit codes.
- **Python Assistance**: Run `scripts/analyze_error.py "<error_message>"` to get targeted advice on the specific Sails.js/Waterline error pattern.
- **Instrument**: If the root cause isn't immediately clear, run `scripts/suggest_logs.py <file_path>` to identify strategic logging points in actions or helpers.
- **Log**: Add temporary `console.log` statements prefixed with `// [DEBUG]` to trace inputs, outputs, and database query results.
  - **In Actions**: Log `inputs` at the top of `fn`, and log the result just before calling `exits.success()` or `exits.error()`.
  - **In Helpers**: Log `inputs` at the start of `fn` and log the return value before `return`.
  - **In Models**: Add logs inside lifecycle callbacks (`beforeCreate`, `afterCreate`, etc.) to verify data before/after DB operations.

### 2. Solve (Implement Fix)

- **Fix**: Apply the necessary code changes based on the identified root cause:
  - **E_UNIQUE**: Add or fix unique index handling in the model, or adjust the action to handle the error gracefully.
  - **E_MISSING_OR_INVALID_PARAMS**: Ensure `inputs` in the action/helper match what is being sent. Check type validation.
  - **Policy Block**: Verify the policy function returns `proceed()` in the success path and `forbid()` or the appropriate exit otherwise.
  - **Waterline Query Failure**: Check that the criteria object is correct and all referenced attributes exist on the model.
  - **Action Hang**: Ensure every code path in `fn` calls one of the defined `exits` (e.g., `exits.success()`, `exits.error()`, `exits.notFound()`).
- **Verify**: The API endpoint should return the expected status code and response body.
- **Confirm**: Ensure no errors or unhandled rejections appear in the terminal running `sails lift`.

### 3. Clean (Remove Instrumentation)

- **CRITICAL**: After verifying the fix, you MUST remove all `console.log` statements added during Step 1.
- **Automate**: Run `scripts/cleanup_logs.py <file_path>` on any file that was instrumented to ensure no temporary `// [DEBUG]` logs remain.
- **Commit**: The final code should be clean and production-ready.

## Common Debugging Scenarios

- **E_UNIQUE**: A uniqueness constraint was violated on a model attribute. Usually caused by duplicate emails, usernames, or other unique fields.
- **E_MISSING_OR_INVALID_PARAMS**: An action or helper received inputs that don't match the defined `inputs` contract. Check types and required fields.
- **E_INVALID_CRITERIA**: A Waterline query was called with malformed or missing criteria (e.g. `undefined` id in `.findOne()`).
- **E_UNAUTHENTICATED / Policy Block**: A policy rejected the request. The user may not be logged in or the session/token is invalid.
- **Action Hang (No Response)**: The action fn never called an exit. Every code branch MUST call `exits.success()`, `exits.error()`, etc.
- **`sails.config` undefined**: Accessing config values before `sails` is lifted. Use lifecycle hooks or wait for lift to complete.
- **Blueprint Route Conflicts**: A custom route or action shadows a blueprint, causing unexpected behavior. Check `config/routes.js`.

## Available Scripts

- `scripts/analyze_error.py <error_message>`: Analyzes Sails.js/Waterline error strings and provides specific fix suggestions.
- `scripts/suggest_logs.py <file_path>`: Suggests where to add `console.log` inside Sails.js action/helper/model files.
- `scripts/cleanup_logs.py <file_path>`: Automatically removes all temporary `// [DEBUG]` console.log statements from a file.
