---
name: debug-reactjs-error
description: Professional debugging system for React.js. Use this skill WHENEVER the user encounters frontend crashes, hook violations, infinite re-renders, stale closures, or state management bugs. You MUST trigger this skill for any React-related issue to ensure the 'Trace, Solve, Clean' cleanup guarantee is applied and the codebase remains production-ready.
---

# Debug-ReactJS-Error

A elite debugging system for identifying and resolving React.js issues with a guaranteed clean-up phase.

## Core Workflow: Trace, Solve, Clean

To maintain high-quality frontend code, you MUST follow this three-step process for every issue:

### 1. Trace (Identify Root Cause)
- **Analyze the Console**: Use browser DevTools or terminal output. React errors often point to the component causing the overflow or the hook being violated.
- **Run Diagnostics**: Execute `scripts/analyze_error.py` to identify common patterns like stale closures or infinite loops.
- **Instrument**: If the cause isn't obvious, use `scripts/suggest_logs.py` to find strategic points in components or hooks.
- **Log with Intent**: Add temporary `console.log` statements. **Requirement**: Prefix them with `// [DEBUG]` so they can be easily cleaned up later.

### 2. Solve (Implement Fix)
- **Apply Fix**: Update the component, hook, or state logic (e.g., fix a `useEffect` dependency array or use a functional update for state).
- **Verify**: Component should render without errors and function as expected.
- **Why?**: Verifying at this stage ensures the logic is sound before moving to cleanup.

### 3. Clean (Remove Instrumentation)
- **CRITICAL**: You MUST NOT leave any `console.log` statements in the frontend code. It's unprofessional and can clutter the browser console in production.
- **Automate**: Run `scripts/cleanup_logs.py` to search and destroy all `// [DEBUG]` logs.
- **Commit**: Final code should be clean, optimized, and ready for PR.

## Common Debugging Scenarios

- **Hook Issues**: Infinite loops in `useEffect`, stale closures, or incorrect dependency arrays.
- **State management**: Unpredictable state changes in Redux Toolkit or Context API.
- **Rendering**: Unnecessary re-renders or component not updating.
- **Network**: API call failures or incorrect data handling.

## Available Scripts
- `scripts/analyze_error.py`: Analyzes error logs and suggests potential fixes.
- `scripts/suggest_logs.py`: Suggests where to add `console.log` for tracing.
- `scripts/cleanup_logs.py`: Automatically removes temporary `console.log` statements.
