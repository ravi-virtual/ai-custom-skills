---
name: debug-mern-stack-error
description: Debugs full-stack MERN (MongoDB, Express, React, Node) bugs that cross the client/server boundary, using a Reproduce, Trace, Solve, Clean workflow that guarantees temporary logging is removed in both layers. Use for CORS errors, "Network Error", 401/403/404/500 seen from React, cookie or JWT flows that fail between login and the next request, dev-proxy problems, an HTML page returned where JSON was expected, and data that saves but does not show in the UI. Use it when the symptom appears in the browser but the cause might be on either side. For a bug clearly confined to one layer use debug-reactjs-error or debug-expressjs-error.
---

# Debug MERN Stack Errors

MERN bugs hide in the hand-off between layers. Trace one request end to end, fix the layer that is actually wrong, and clean up both layers.

## Workflow: Reproduce, Trace, Solve, Clean

### 0. Reproduce and localise
1. Open the browser **Network** tab for the failing call: URL, method, status, request headers, response body. Copy as cURL.
2. Replay that cURL against the server directly. If it also fails, the bug is server-side (or data); if it works, suspect the client (URL, headers, payload, CORS, cookies).
3. Check the server terminal for the matching request and the first error.

### 1. Trace
1. Match the error text: `python scripts/analyze_error.py "<text>"` (use `--file` for long logs).
2. Get insertion points on both sides: `python scripts/suggest_logs.py client/src/api/userApi.js` and `... server/src/routes/user.routes.js`. Tags are `[client]`, `[server]`, `[auth]`.
3. Insert tagged logs: `console.log('[DEBUG][client] request', url); // [DEBUG]`. Use `// [DEBUG:START]`/`// [DEBUG:END]` for blocks.
4. **Never log secrets.** For tokens log presence (`!!token`), never the value.
5. Follow one request: component handler, Axios call (URL, headers, payload), Express route, middleware chain, controller, Mongoose query, response, reducer/state, render. Stop at the first mismatch.

### 2. Solve
- Fix at the source layer. Examples: CORS belongs in the server (`cors({ origin, credentials: true })` before routes); wrong URL belongs in the client base URL or the dev proxy; response-shape drift needs one side changed, not both patched.
- Re-test the full user flow in the browser (not just cURL), including the unhappy path. Run existing tests in both packages.

### 3. Clean
Run from the repo root so both `client/` and `server/` are covered:
1. `python scripts/cleanup_logs.py client/src server/src --dry-run`
2. `python scripts/cleanup_logs.py client/src server/src`
3. `python scripts/cleanup_logs.py client/src server/src --check` must exit 0.

Only marker-tagged statements are removed. Tags on real code are reported as `REVIEW` and left in place. Finish with `git diff` in both packages.

## Symptom to cause

| Symptom | Usual cause | Fix |
|---|---|---|
| `blocked by CORS policy` | Server does not allow the exact origin, or `*` used with credentials | `cors({ origin: CLIENT_URL, credentials: true })` before routes |
| `Network Error` / `ERR_CONNECTION_REFUSED` | Server down, wrong port/base URL, mixed content | Check server log, `VITE_API_URL`/proxy target |
| `Unexpected token '<'` ... `not valid JSON` | Got `index.html`: wrong URL or missing proxy | Fix path/proxy; inspect real response |
| 401 right after login | Token not stored/sent, cookie dropped | Axios interceptor header; `withCredentials`; `SameSite`/`Secure` |
| 404 from React only | `/api` prefix mismatch | Align client URL and `app.use('/api', ...)` |
| 400 with valid-looking form | Client payload differs from schema/validator | Compare payload with validator field names/types |
| Saves but UI stale | State not updated or re-fetched after mutation | Update store from the response or invalidate/refetch |
| Works in dev, fails in prod | Env vars, CORS origin, HTTPS, proxy rewrite | Diff env and the built bundle's base URL |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/analyze_error.py` | Match error text (arg, `--file`, stdin) to full-stack patterns |
| `scripts/suggest_logs.py <file>` | Line-numbered, marker-tagged snippets for client or server files |
| `scripts/cleanup_logs.py <paths> [--dry-run\|--check]` | Remove marker-tagged debug code in many files/directories |

Python 3.8+, no packages needed.
