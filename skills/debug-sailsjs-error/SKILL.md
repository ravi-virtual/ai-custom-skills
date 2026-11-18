---
name: debug-sailsjs-error
description: Debugs Sails.js backend problems with a Reproduce, Trace, Solve, Clean workflow that guarantees temporary logging is removed afterwards. Use for Waterline errors (E_UNIQUE, E_INVALID_CRITERIA, AdapterError, E_NOT_FOUND), actions or helpers that hang or hit missing exits, E_MISSING_OR_INVALID_PARAMS, policy blocks (E_UNAUTHENTICATED, E_FORBIDDEN), route or blueprint conflicts, helpers not found, and errors printed by sails lift. Use it even when the user only pastes a Sails stack trace.
---

# Debug Sails.js Errors

Fix the root cause, prove it with a real request, and leave no debugging scaffolding behind.

## Workflow: Reproduce, Trace, Solve, Clean

### 0. Reproduce
- Capture the failing request (method, URL, headers without secrets, body) and replay it with `curl`.
- Read the `sails lift` output for the first error and its stack. Note the Sails version (`package.json`) and whether the action is a classic controller (`req, res`) or an actions2 file (`inputs, exits`).

### 1. Trace
1. Match the message: `python scripts/analyze_error.py "<error text>"` (long logs: `--file`).
2. Get insertion points: `python scripts/suggest_logs.py api/controllers/meeting/terminate.js`. It handles actions, controllers, helpers, Waterline calls, exits, lifecycle callbacks and policies, with line numbers.
3. Insert tagged logs: `console.log('[DEBUG] inputs', inputs); // [DEBUG]`. Group several lines with `// [DEBUG:START]` ... `// [DEBUG:END]`.
   - **Actions/helpers:** log `inputs` at the top of `fn` and the value before each exit.
   - **Models:** log `valuesToSet` inside lifecycle callbacks.
   - **Policies:** log `req.method`, `req.path` and the user id before `proceed()`.
4. **Never log secrets** (tokens, passwords, session ids). Log presence or ids.
5. Replay the request and find the first step that deviates.

### 2. Solve
- Fix the root cause (table below), then replay the original request and one invalid-input case. Check the status code, response shape, and that `sails lift` shows no unhandled rejections. Run the project's tests.
- Every code path in `fn` must reach exactly one exit. Classic controllers must send exactly one response.

### 3. Clean
1. Preview: `python scripts/cleanup_logs.py api config --dry-run`
2. Apply: `python scripts/cleanup_logs.py api config`
3. Gate: `python scripts/cleanup_logs.py api config --check` must exit 0.

Only marker-tagged statements are removed. Tags on real code are reported as `REVIEW`; resolve those by hand. The project's own logging (`sails.log`, SQS error reporters) is never touched. Finish with `git diff`.

## Symptom to cause

| Symptom | Usual cause | Fix |
|---|---|---|
| `E_UNIQUE` | Duplicate value on a `unique: true` attribute | Catch it, return a 4xx naming the field |
| `E_MISSING_OR_INVALID_PARAMS` | Caller input does not match the `inputs` contract | Align types/required flags with the caller |
| `E_INVALID_CRITERIA` | `undefined` in `findOne`/`find` criteria | Validate input before querying |
| Request hangs | An `fn` branch never calls an exit | Add the missing exit/`return` |
| "Cannot call an exit after the machine has already exited" | Exit called twice | `return exits.success(...)` |
| `E_UNAUTHENTICATED` / `E_FORBIDDEN` | Policy rejected (token/session/role) | Check header, session, policy logic and `config/policies.js` |
| `sails.helpers.x is not a function` | File-name/camelCase mismatch or helpers hook off | `send-email.js` -> `sails.helpers.sendEmail` |
| Custom route ignored | Blueprint or earlier route shadows it | Review `config/routes.js` order and blueprint settings |
| `AdapterError` / `ECONNREFUSED` | Datastore unreachable or misconfigured | Check `config/datastores.js` and the DB service |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/analyze_error.py` | Match error text (arg, `--file`, stdin) to Sails/Waterline patterns |
| `scripts/suggest_logs.py <file>` | Line-numbered, marker-tagged log snippets |
| `scripts/cleanup_logs.py <paths> [--dry-run\|--check]` | Remove marker-tagged debug code safely |

Python 3.8+, no packages needed.
