---
name: mern-stack-project
description: Plans, scaffolds and reviews a full MERN (MongoDB, Express, React, Node) application at project level - repository layout, the client/server contract (response envelope, auth flow, CORS, env vars), and building a feature across both layers. Use when the user wants to start a MERN project, add a feature that touches both frontend and backend, connect React to an Express API, decide folder structure, or review a whole MERN codebase for production readiness. Layer-specific rules come from backend-expressjs and frontend-reactjs, which this skill depends on. For MERN bugs use debug-mern-stack-error.
---

# MERN Stack Project

This skill owns the **project level**: how the repos fit together and how the two layers agree with each other. Layer details live in two sibling skills; read the one for the layer you are about to touch before writing code in it:

| Layer | Skill | Covers |
|---|---|---|
| Express / Node / Mongoose | `backend-expressjs` | structure, constants, response envelope, middleware, models, controllers |
| React / Redux Toolkit | `frontend-reactjs` | structure, Axios layer, slices, hooks, routing, components |

Full repository tree and the combined naming table: `references/repository-and-naming.md`.

## Layout

Separate backend and frontend repos (or packages) under one parent folder:

```
project-name/
├── backend/     # Express API    -> follow backend-expressjs
└── frontend/    # React (Vite)   -> follow frontend-reactjs
```

Each has its own `package.json`, `.env` and `.env.example`. Never share `node_modules` or secrets between them.

## Starting a new project

1. Confirm the choices that change code: MongoDB only or PostgreSQL too, auth style (Bearer JWT vs cookie), roles needed, Vite as the React toolchain.
2. Scaffold `backend/` from `backend-expressjs` (constants first, then `app.js`, `server.js`, `errorHandler`, `apiResponse`).
3. Scaffold `frontend/` from `frontend-reactjs` (constants, Axios instance, store, router).
4. Write both `.env.example` files with the **contract variables** below and make sure they agree.
5. Build one vertical slice (auth + one resource) end to end before adding more resources.

## Building a feature across both layers

1. **Contract first.** Write down the endpoint(s): method, path, request body, success `data` shape, error codes. Agree it before coding either side.
2. **Backend** following the backend workflow (constants, model, guards, validator, controller, routes). Test with `curl`.
3. **Frontend**: `api/<resource>Api.js` function, Redux slice (thunk, loading/error state), then components/pages.
4. **Integrate** in the browser: happy path, validation error, unauthenticated, server error. Verify the UI shows the server's `message`.
5. **Tidy**: both checklists pass; no debug logging left (see `debug-mern-stack-error`).

## The client/server contract

| Topic | Backend does | Frontend does |
|---|---|---|
| Base URL | Mounts all routes under `/api` | `VITE_API_BASE_URL` is the server origin; API functions include `/api/...` |
| Success body | `{ success: true, status, message, data: {...} }` via `ApiResponse` | Reads `response.data.data.<key>` in thunks |
| Error body | `{ success: false, status, message, error: { code, details } }` via `sendError` | Shows `err.response?.data?.message`; maps `error.details` to field errors |
| Lists | `data: { <plural-name>: [...], totalCount }` with `?page&limit&sort&search` | Keeps page/limit in UI state; derives page count from `totalCount` |
| Auth | Verifies `Authorization: Bearer <token>`; 401 on invalid/expired | Axios request interceptor adds the header; 401 interceptor clears the session and redirects to `/login` |
| CORS | `cors({ origin: CLIENT_URL, credentials: true })` before routes | Never calls the API from another origin without it being allowed |
| Env vars | `CLIENT_URL`, `JWT_SECRET`, `MONGO_URI`... read only in `config/constants.js` | `VITE_*` read only in `utils/constants.js` |
| IDs | UUID `_id` strings | Treats ids as opaque strings |

If either side changes the envelope, the Axios interceptors and every thunk change with it: update both in the same change.

## Cross-layer review checklist

- [ ] Both `.env.example` files list every variable the code reads; `CLIENT_URL` matches the frontend origin per environment
- [ ] Every endpoint the frontend calls exists with the same method, path and body field names
- [ ] Validation exists on the server (authoritative) and, for UX, on the client; error `details[].field` names match form field names
- [ ] 401 triggers logout on the client; 403 shows a permission message instead
- [ ] No secrets or tokens are logged or rendered; passwords never leave the server
- [ ] Production build points at the production API URL (HTTPS) and the server's CORS origin matches it
- [ ] `backend-expressjs` and `frontend-reactjs` production checklists both pass

> **Trade-off to state to the user:** the default frontend pattern keeps the access token in `localStorage`, which any XSS can read. If the app handles sensitive data, propose short-lived access tokens with an httpOnly, `SameSite` refresh cookie instead (it needs `credentials: true` on both sides).
