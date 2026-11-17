---
name: debug-reactjs-error
description: Debugs React.js frontend problems with a Reproduce, Trace, Solve, Clean workflow that guarantees temporary logging is removed afterwards. Use for white screens, console errors, invalid or conditional hook calls, infinite re-renders, stale closures, useEffect dependency bugs, Redux/Context state not updating, hydration mismatches, and unexpected re-renders. Use it even when the user only pastes an error or says "my component is not working" without mentioning debugging. For bugs that span React and the API, use debug-mern-stack-error instead.
---

# Debug React.js Errors

Fix the root cause, prove it is fixed, and leave no debugging scaffolding behind.

## Workflow: Reproduce, Trace, Solve, Clean

### 0. Reproduce
- Get the exact error text, the component stack, and the steps that trigger it. Read the **first** console error, not the last; later ones are usually fallout.
- Note the React version (`package.json`) and whether `<StrictMode>` is on. In React 18+ dev mode StrictMode runs effects twice on mount; that is expected, not the bug.

### 1. Trace
1. Match the message: `python scripts/analyze_error.py "<error text>"` (long logs: `--file error.log`). Treat the advice as a lead to verify.
2. If the cause is still unclear, get insertion points: `python scripts/suggest_logs.py src/components/Foo.jsx`. It prints line numbers and paste-ready snippets.
3. Insert logs exactly as suggested. Every temporary statement **must** end with the marker comment `// [DEBUG]`, e.g. `console.log('[DEBUG] render', { users }); // [DEBUG]`. For several lines wrap them in `// [DEBUG:START]` ... `// [DEBUG:END]`.
4. **Never log secrets** (tokens, passwords, full user objects). Log presence or ids: `!!token`.
5. Reproduce again and read the output. Form one hypothesis at a time and test it.

### 2. Solve
- Apply the smallest fix that addresses the root cause (see the table below). Do not paper over it with `// eslint-disable` or by deleting the dependency array.
- Re-run the failing scenario, check the console is clean, and run the existing tests/lint.
- If the project has component tests, add or extend one that fails without the fix.

### 3. Clean
1. Preview: `python scripts/cleanup_logs.py src --dry-run`
2. Apply: `python scripts/cleanup_logs.py src`
3. Gate: `python scripts/cleanup_logs.py src --check` must exit 0.

The script removes only statements tagged with the marker (multi-line calls included). A tag on real code is left alone and reported as `REVIEW`; resolve it by hand. Pre-existing project logging is not touched. Finish with `git diff` and confirm it contains only the intended fix.

## Symptom to cause

| Symptom | Usual cause | Fix |
|---|---|---|
| `Too many re-renders` / `Maximum update depth exceeded` | State set during render, or effect that sets a dependency of itself | Move the update into an event handler/effect; fix deps; use a functional update |
| `Invalid hook call` | Hook inside a condition/loop/plain function, or two React copies | Hooks at top level of components/custom hooks; `npm ls react` |
| `Rendered fewer/more hooks than expected` | Early `return` above a hook | Put all hooks before any conditional return |
| Effect runs every render | Missing or unstable dependency (new object/function each render) | Memoise with `useMemo`/`useCallback` or depend on primitives |
| Stale value in handler/timer | Closure captured an old state | Functional update (`setN(n => n + 1)`), `useRef`, or correct deps |
| `Cannot read properties of undefined` | Data not loaded on first render | Safe default state, optional chaining, loading branch |
| List warning about `key` / wrong item updates | Missing or index keys on reorderable lists | Stable unique id as key |
| Hydration mismatch | Server and client render differ (dates, `window`, random) | Make first render deterministic; read browser APIs in `useEffect` |
| UI does not update after Redux change | Mutated state outside Redux Toolkit/immer, or selector returns new object each call | Use slice reducers; select primitives or use `shallowEqual` |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/analyze_error.py` | Match error text (arg, `--file`, or stdin) to known React failure patterns |
| `scripts/suggest_logs.py <file>` | Line-numbered, marker-tagged log snippets for a component/hook |
| `scripts/cleanup_logs.py <paths> [--dry-run\|--check]` | Remove marker-tagged debug code; safe on real code |

Scripts need only Python 3.8+ and no packages.
