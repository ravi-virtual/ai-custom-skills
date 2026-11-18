---
name: debug-expressjs-error
description: Debugs Express.js / Node.js backend problems with a Reproduce, Trace, Solve, Clean workflow that guarantees temporary logging is removed afterwards. Use for 500 errors, requests that hang, ERR_HTTP_HEADERS_SENT, EADDRINUSE, middleware order bugs, req.body undefined, async errors that crash the process, JWT/auth failures, and Mongoose/MongoDB errors (validation, CastError, duplicate key, connection). Use it even when the user only pastes a stack trace. For issues that span React and Express, use debug-mern-stack-error instead.
---

# Debug Express.js Errors

Fix the root cause, prove it with a real request, and leave no debugging scaffolding behind.

## Workflow: Reproduce, Trace, Solve, Clean

### 0. Reproduce
- Capture the failing request exactly: method, URL, headers (without secrets), body. Replay it with `curl` or the project's REST client so the bug is repeatable without the UI.
- Read the server terminal (nodemon/pm2/morgan) for the **first** error and its stack. Note the Node and Express versions: Express 4 does not forward rejected promises from async handlers; Express 5 does.

### 1. Trace
1. Match the message: `python scripts/analyze_error.py "<error text>"` (long logs: `--file error.log`, or pipe stdin). Treat the advice as a lead to verify.
2. Find insertion points: `python scripts/suggest_logs.py src/controllers/user.controller.js`. It prints line numbers and ready snippets for handlers, DB calls, `next()`, responses and `catch` blocks.
3. Insert logs tagged with the marker: `console.log('[DEBUG] getUser', req.params); // [DEBUG]`. Multi-line groups go between `// [DEBUG:START]` and `// [DEBUG:END]`.
4. **Never log secrets**: passwords, tokens, `Authorization` headers, full `req.body` of auth routes. Log keys, ids, or `!!value`.
5. Replay the request; follow the log from the route to the controller to the DB call to the response, and find the first step where reality differs from expectation.

### 2. Solve
- Apply the smallest fix at the root cause. Prefer centralised handling (error middleware, async wrapper, validation layer) over per-route patches.
- Replay the original request, plus one invalid-input case, and check status codes and body shape. Run existing tests; add a test that fails without the fix when a test setup exists.

### 3. Clean
1. Preview: `python scripts/cleanup_logs.py src --dry-run`
2. Apply: `python scripts/cleanup_logs.py src`
3. Gate: `python scripts/cleanup_logs.py src --check` must exit 0.

Only marker-tagged statements are removed (multi-line calls included); a tag on real code is reported as `REVIEW` and left in place. The project's own logger calls are never touched. Finish with `git diff`.

## Symptom to cause

| Symptom | Usual cause | Fix |
|---|---|---|
| Request hangs | Handler/middleware never responds or calls `next()` | Ensure every path sends once or calls `next` |
| `ERR_HTTP_HEADERS_SENT` | Second response after `res.json` | `return res.json(...)`; avoid code after sending |
| `req.body` undefined | No body parser before routes, or wrong `Content-Type` | `app.use(express.json())` above routes |
| Process dies on an unhandled rejection | Async handler without catch (Express 4) | Async wrapper or `try/catch` + `next(err)` |
| `Cannot GET /x` | Wrong method/prefix, router not mounted, 404 handler registered too early | Check mount path and order |
| `EADDRINUSE` | Another process on the port | Find with `lsof -i :<port>`; stop it or change `PORT` |
| `CastError` on `:id` | Invalid ObjectId | Validate ids before querying |
| `E11000 duplicate key` | Unique index hit | Catch code 11000, return 409 |
| `jwt malformed` / `jwt expired` | Bad/missing/expired token | Check header format, secret, expiry; return 401 |
| Works locally, fails in prod | Env vars, CORS origin, trusted proxy, case-sensitive paths | Compare env and logs |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/analyze_error.py` | Match error text (arg, `--file`, or stdin) to known Express/Mongoose/JWT patterns |
| `scripts/suggest_logs.py <file>` | Line-numbered, marker-tagged log snippets |
| `scripts/cleanup_logs.py <paths> [--dry-run\|--check]` | Remove marker-tagged debug code safely |

Python 3.8+, no packages needed.
