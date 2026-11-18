# Repository Structure & Naming Conventions

Part of the `mern-stack-project` skill. Full-project layout (backend + frontend) and the naming table that covers both layers.

## Contents
- [Repository Structure](#repository-structure)
- [Naming Conventions](#naming-conventions)

## Repository Structure

Projects use **separate repos** for backend and frontend, both living under a single parent `project-name/` folder.

```
project-name/
├── backend/                          # Backend repo (Express / Node.js)
│   ├── src/
│   │   ├── config/
│   │   │   └── constants.js          # config (env), ResponseCodes, Roles, ErrorCodes — single source of truth
│   │   ├── controllers/              # PascalCase files. JSDoc on every method. try/catch blocks.
│   │   │   └── UserController.js
│   │   ├── middlewares/              # camelCase files, one responsibility per file
│   │   │   ├── hasToken.js           # Verifies JWT, attaches req.user, sets isAuthenticated = true
│   │   │   ├── isAuthenticated.js    # Guards: checks req.user.isAuthenticated === true
│   │   │   ├── isAdmin.js            # Guards: checks req.user.role === Roles.ADMIN
│   │   │   ├── isUser.js             # Guards: checks req.user.role === Roles.USER
│   │   │   ├── errorHandler.js       # Global error handler (4-arg, registered last in app.js)
│   │   │   └── rateLimiter.js        # express-rate-limit config
│   │   ├── models/                   # PascalCase files, UUID _id, no dots in filename
│   │   │   └── User.js
│   │   ├── routes/                   # camelCase files, route definitions only — no logic
│   │   │   ├── index.js              # Aggregates all routers, mounts under /api
│   │   │   └── userRoutes.js
│   │   ├── utils/
│   │   │   └── apiResponse.js        # ApiResponse class + sendError function
│   │   ├── validators/               # camelCase files, express-validator rule sets
│   │   │   ├── userValidator.js
│   │   │   └── adminValidator.js
│   │   └── app.js                    # Express app setup — middleware stack and routes
│   ├── database/
│   │   └── schema.sql                # PostgreSQL table definitions (if using PostgreSQL)
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── package.json
│   └── server.js                     # Entry point — connects DB, starts server
│
└── frontend/                         # Frontend repo (React)
    ├── public/
    ├── src/
    │   ├── api/                      # Axios instance and per-resource API functions
    │   │   └── userApi.js
    │   ├── assets/
    │   ├── components/               # Reusable UI — PascalCase filenames
    │   ├── hooks/                    # Custom hooks: useAuth.js, useFetch.js etc.
    │   ├── pages/                    # Route-level page components — PascalCase
    │   ├── routes/                   # React Router config
    │   ├── store/                    # Redux Toolkit — required for all global state
    │   │   ├── index.js              # configureStore
    │   │   └── slices/               # One slice per feature
    │   │       └── userSlice.js
    │   ├── utils/                    # Frontend helpers
    │   ├── App.jsx
    │   └── main.jsx
    ├── .env
    ├── .env.example
    └── package.json
```

## Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Controller files | PascalCase | `UserController.js` |
| Model files | PascalCase | `User.js`, `FavouriteService.js` |
| Route files | camelCase | `userRoutes.js` |
| Middleware files | camelCase | `isAdmin.js`, `errorHandler.js` |
| Validator files | camelCase | `userValidator.js` |
| Util files | camelCase | `apiResponse.js` |
| React components | PascalCase | `UserCard.jsx` |
| Frontend API files | camelCase | `userApi.js` |
| Redux slices | camelCase | `userSlice.js` |
| Routes/URLs | kebab-case, plural nouns | `/api/user-profiles` |
| Variables/functions | camelCase | `getUserById` |
| Constants/Enums | UPPER_SNAKE_CASE | `MAX_LOGIN_ATTEMPTS` |
| Env vars | UPPER_SNAKE_CASE | `JWT_SECRET` |

> **Hard rule: Never use `.` in a filename except for the extension.** `user.controller.js` ✗ → `UserController.js` ✓
