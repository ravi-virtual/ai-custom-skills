---
name: debug-mern-stack-error
description: Professional full-stack debugging system for MERN (MongoDB, Express, React, Node) applications. Use this skill WHENEVER the user encounters integration issues, CORS failures, proxy errors, or authentication flows where the frontend and backend fail to communicate. You MUST trigger this skill for any full-stack bug to ensure the 'Trace, Solve, Clean' cleanup guarantee is applied across both layers, ensuring a pristine codebase.
---

# Debug-MERN-Stack-Error

A elite full-stack debugging system for identifying and resolving MERN integration issues with a guaranteed clean-up phase.

## Core Workflow: Trace, Solve, Clean

Full-stack bugs require coordination. You MUST follow this three-step process for every issue:

### 1. Trace (Identify Root Cause)
- **Check Both Ends**: Simultaneously monitor the browser console (React) and the server terminal (Express). 
- **Correlate**: If React shows a 404 or 500, check the Express logs immediately to see which route or middleware failed.
- **Run Diagnostics**: Execute `scripts/analyze_error.py` to diagnose integration-specific patterns like CORS or Proxy mismatches.
- **Instrument with Intent**: Use `scripts/suggest_logs.py` to identify coordination points (e.g., matching the Axios call in React with the Route handler in Express).
- **Log with Prefix**: Add temporary `console.log` statements. **Requirement**: Prefix them with `// [DEBUG]` in both frontend and backend for easy identification.

### 2. Solve (Implement Fix)
- **Apply Fix**: Update code in the relevant layer (React, Express, or Mongoose).
- **Verify the Flow**: Test the full cycle (e.g., user clicks button -> React sends request -> Express processes -> MongoDB updates -> React updates UI).
- **Why?**: MERN bugs often hide in the "handshake" between layers. Verifying the full flow is the only way to ensure the fix is complete.

### 3. Clean (Remove Instrumentation)
- **CRITICAL**: You MUST NOT leave any `console.log` statements in a MERN project. It compromises security and performance.
- **Automate**: Run `scripts/cleanup_logs.py` to wipe all `// [DEBUG]` logs from the entire project structure.
- **Commit**: Ensure both the `client/` and `server/` (or equivalent) directories are clean and production-ready.

## Common Debugging Scenarios

- **CORS Issues**: Browser blocks request from frontend to backend.
- **Auth Flow**: Token generated on backend but not sent correctly or stored on frontend.
- **Proxy/URL**: Frontend trying to reach `/api/user` but backend is listening on `/user`.
- **Validation**: Frontend validation passes but backend/Mongoose validation fails.

## Available Scripts
- `scripts/analyze_error.py`: Diagnoses full-stack integration issues.
- `scripts/suggest_logs.py`: Recommends trace logs for frontend-backend interaction.
- `scripts/cleanup_logs.py`: Automatically removes temporary `console.log` statements in the whole project.
