---
name: backend-expressjs
description: Builds and reviews production-grade Express / Node.js backends with Mongoose or PostgreSQL, following one consistent set of conventions for folder structure, naming, constants, a standard JSON response envelope, express-validator validation, JWT auth middleware, error handling and controllers. Use when the user asks to add or change an API endpoint, route, middleware, controller, model, validator or constant, to scaffold or review an Express backend, or to add authentication. Apply it even to small isolated tasks (one route, one constant) so the project stays consistent. For Sails.js backends use sailsjs-api; for React code use frontend-reactjs.
---

# Express / Node.js Backend

Production-grade conventions for an Express backend. This file holds the workflow, structure, naming rules and the final checklist. The code templates live in `references/` and should be read **only for the part you are touching**.

## Reference map

| If the task involves... | Read |
|---|---|
| `config/constants.js`, env vars, `ResponseCodes`, `ErrorCodes`, `Roles` | `references/config-and-constants.md` |
| URL design, HTTP verbs, response/error JSON shape, `apiResponse.js` | `references/api-design-and-responses.md` |
| `app.js` middleware order, JWT/auth guards, `errorHandler.js`, rate limiting | `references/middleware.md` |
| Mongoose schema (UUID `_id`, soft delete), PostgreSQL `schema.sql` | `references/models-and-database.md` |
| Validators, controllers (JSDoc + try/catch), route chains, `server.js` | `references/validation-controllers-routes.md` |

## Non-negotiables (details in the references)

- Success and error bodies come only from `ApiResponse` / `sendError`; never call `res.json()` directly in a controller.
- Status codes and error codes come from `ResponseCodes` / `ErrorCodes`; no raw numbers or strings.
- `process.env` is read only in `config/constants.js`; the app exits at startup if a required variable is missing.
- Route chain order: auth, guards, validator, controller. `errorHandler` is the last middleware, the 404 handler sits just before it.
- Passwords and tokens use `select: false` and never appear in responses or logs.
- Controllers use `try/catch` and no service layer; every method has a JSDoc block.

## Workflow: adding a new feature

When adding a new API endpoint or resource to an **existing project**, follow this systematic sequence:

1.  **Step 1: Define Constants & Statics**: Identify if new `ErrorCodes`, `ResponseCodes`, `Roles`, or other static variables are needed in `src/config/constants.js`.
2.  **Step 2: Create/Update Model**: Define the Mongoose/PostgreSQL schema with:
    - UUID `_id` (not MongoDB ObjectId).
    - `timestamps: true`.
    - Soft-delete flag (`isDeleted: false`).
3.  **Step 3: Define Middlewares & Guards**: Implement necessary guards (e.g., `isAdmin`, `isAuthor`, `hasPermission`) in `src/middlewares/` if they don't already exist.
4.  **Step 4: Create Request Validator**: Define the `express-validator` rules in `src/validators/` for the new payload.
5.  **Step 5: Implement the Controller**:
    - Write the controller functions in PascalCase.
    - Add a JSDoc block to every method (`@name`, `@description`, etc.).
    - Use `try/catch` and return responses using the `apiResponse` utility.
6.  **Step 6: Register Routes**:
    - Build the route chain (Auth -> Middlewares/Guards -> Validator -> Controller).
    - Ensure the route file (e.g., `userRoutes.js`) is imported into `src/routes/index.js`.

---

## Folder Structure

The backend lives at `project-name/backend/`.

```
project-name/
└── backend/
    ├── src/
    │   ├── config/
    │   │   └── constants.js          # config (env), ResponseCodes, Roles, ErrorCodes — single source of truth
    │   ├── controllers/              # PascalCase files. JSDoc on every method. try/catch blocks.
    │   │   └── UserController.js
    │   ├── middlewares/              # camelCase files, one responsibility per file
    │   │   ├── hasToken.js           # Verifies JWT, attaches req.user, sets isAuthenticated = true
    │   │   ├── isAuthenticated.js    # Guards: checks req.user.isAuthenticated === true
    │   │   ├── isAdmin.js            # Guards: checks req.user.role === Roles.ADMIN
    │   │   ├── isUser.js             # Guards: checks req.user.role === Roles.USER
    │   │   ├── errorHandler.js       # Global error handler (4-arg, registered last in app.js)
    │   │   └── rateLimiter.js        # express-rate-limit config
    │   ├── models/                   # PascalCase files, UUID _id, no dots in filename
    │   │   └── User.js
    │   ├── routes/                   # camelCase files, route definitions only — no logic
    │   │   ├── index.js              # Aggregates all routers, mounts under /api
    │   │   └── userRoutes.js
    │   ├── utils/
    │   │   └── apiResponse.js        # ApiResponse class + sendError function
    │   ├── validators/               # camelCase files, express-validator rule sets
    │   │   ├── userValidator.js
    │   │   └── adminValidator.js
    │   └── app.js                    # Express app setup — middleware stack and routes
    ├── database/
    │   └── schema.sql                # PostgreSQL table definitions (if using PostgreSQL)
    ├── .env
    ├── .env.example
    ├── .gitignore
    ├── package.json
    └── server.js                     # Entry point — connects DB, starts server
```

---

## Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Controller files | PascalCase | `UserController.js` |
| Model files | PascalCase | `User.js`, `FavouriteService.js` |
| Route files | camelCase | `userRoutes.js` |
| Middleware files | camelCase | `isAdmin.js`, `errorHandler.js` |
| Validator files | camelCase | `userValidator.js`, `adminValidator.js` |
| Util files | camelCase | `apiResponse.js` |
| Routes / URLs | kebab-case, plural nouns | `/api/user-profiles` |
| Variables / functions | camelCase | `getUserById` |
| Constants / Enums | UPPER_SNAKE_CASE | `MAX_LOGIN_ATTEMPTS` |
| Env vars | UPPER_SNAKE_CASE | `JWT_SECRET` |

> **Hard rule: Never use `.` in a filename except for the extension.** `user.controller.js` ✗ → `UserController.js` ✓

---

## Production Checklist

### Naming & Structure
- [ ] Controller filenames are PascalCase — `UserController.js`
- [ ] Model filenames are PascalCase — `User.js`, `FavouriteService.js`
- [ ] Route, middleware, validator, and util filenames are camelCase
- [ ] No dots in filenames except the extension (`.js`, `.json`, `.sql`)
- [ ] No service layer — all logic lives directly in controllers

### API & Responses
- [ ] All routes follow `/api/{resource}` (no `/v1/` prefix)
- [ ] Every success response uses `new ApiResponse(...).send(res)`
- [ ] Every error response uses `sendError(res, { ... })`
- [ ] `data` field is always an object — never a raw array or primitive
- [ ] Paginated responses include `totalCount` only — not `page`, `limit`, or `totalPages`
- [ ] HTTP status codes always reference `ResponseCodes` — never raw numbers
- [ ] Error codes always reference `ErrorCodes` — never raw strings

### Controllers
- [ ] Every method has a JSDoc block (`@name`, `@file`, `@param`, `@description`, `@author`)
- [ ] Every async method uses `try/catch` — no catchAsync wrapper
- [ ] No direct `res.json()` or `res.status()` calls

### Security & Auth
- [ ] `password` has `select: false` on schema — never returned in any response
- [ ] Other sensitive fields (tokens, secrets) also have `select: false`
- [ ] Protected routes use `hasToken → isAuthenticated` chain
- [ ] Role-restricted routes add `isAdmin` or `isUser` after `isAuthenticated`
- [ ] Auth endpoints have stricter rate limiting

### Models & Database
- [ ] All Mongoose models use UUID `_id` (`default: uuidv4`, `_id: false` in schema options)
- [ ] All schemas include `timestamps: true`
- [ ] `toJSON` transform removes `__v` and `password`
- [ ] Soft delete via `{ isDeleted: false }` — all find queries include this filter
- [ ] PostgreSQL: `database/schema.sql` has UUID PKs, `is_deleted`, timestamps, and a trigger per table

### Config & Environment
- [ ] `process.env.X` only accessed inside `config/constants.js`
- [ ] All static values and env config imported from `config/constants.js`
- [ ] App exits at startup if required env vars are missing

### Error Handling
- [ ] `errorHandler.js` registered as the very last middleware in `app.js`
- [ ] 404 handler registered after all routes, before `errorHandler`
- [ ] Stack traces never included in production error responses
