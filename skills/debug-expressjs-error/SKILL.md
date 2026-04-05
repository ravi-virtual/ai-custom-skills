---
name: debug-expressjs-error
description: Professional debugging system for Express.js. Use this skill WHENEVER the user encounters server-side errors, 500 Internal Server Errors, EADDRINUSE port conflicts, middleware hangs, or any Express/Node.js backend failure. You MUST trigger this skill even if the error seems minor or if the user doesn't explicitly mention 'debugging', to ensure the 'Trace, Solve, Clean' cleanup guarantee is applied.
---

# Debug-ExpressJS-Error

A elite debugging system for identifying and resolving Express.js backend issues with a guaranteed clean-up phase.

## Core Workflow: Trace, Solve, Clean

To maintain production standards, you MUST follow this three-step process for every issue:

### 1. Trace (Identify Root Cause)
- **Analyze Logs**: Immediately check terminal logs (Morgan, nodemon, or pm2). Express errors often provide the exact line number of the failure.
- **Run Diagnostics**: Execute `scripts/analyze_error.py` to match common failure patterns (e.g., Auth, DB, Middleware).
- **Instrument**: If the cause is elusive, use `scripts/suggest_logs.py`. 
- **Log with Intent**: Add temporary `console.log` statements. **Requirement**: Prefix them with `// [DEBUG]` so they are easily identifiable and removable.

### 2. Solve (Implement Fix)
- **Apply Fix**: Update the code (e.g., fix a Mongoose schema, add a missing `next()` call, or correct an async handler).
- **Verify**: Test the endpoint. It should return the correct status code (e.g., 200/201) and data.
- **Why?**: Incremental verification prevents regressions and ensures the fix actually addresses the root cause observed in Step 1.

### 3. Clean (Remove Instrumentation)
- **CRITICAL**: You MUST NOT leave any `console.log` statements in the codebase. This is a production-grade requirement.
- **Automate**: Run `scripts/cleanup_logs.py` to scan and remove all `// [DEBUG]` logs automatically.
- **Commit**: Ensure the final state is clean, efficient, and lacks any temporary scaffolding.

## Common Debugging Scenarios

- **Middleware Blocking**: Request hangs because `next()` wasn't called.
- **Async/Await Errors**: Unhandled promise rejections or database timeouts.
- **Authentication**: JWT verification failures or incorrect passport strategies.
- **Database**: Mongoose validation errors or connection issues.

## Available Scripts
- `scripts/analyze_error.py`: Analyzes backend error logs and suggests potential fixes.
- `scripts/suggest_logs.py`: Suggests where to add `console.log` in routes or controllers.
- `scripts/cleanup_logs.py`: Automatically removes temporary `console.log` statements.
