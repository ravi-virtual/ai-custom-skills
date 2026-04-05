---
name: backend-expressjs
description: Production-grade system for the Express / Node.js backend. Use this skill whenever the user asks to scaffold, design, build, extend, or review any part of a backend application. Triggers include: "add a new API", "create a route with middleware", "setup constants", "design a Mongoose model", "build a REST endpoint", "add authentication", or any request to generate Express/Node.js code. Use this skill even for isolated tasks (like adding one route or one constant) to ensure consistency with the established production standards.
---

# MERN Backend Skill

Production-grade rulebook for the Express / Node.js backend.
Covers folder structure, API design, response formatting, validation, auth, error handling, models, and more.

---

## 0. Workflow: Adding a New Feature

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

## 1. Folder Structure

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

## 2. Naming Conventions

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

## 3. Config & Constants

There is only **one file** in `src/config/` — `constants.js`. It handles env loading and all static app values. There is no separate `index.js`.

### `src/config/constants.js`
```js
// ─── Environment validation (fail fast on startup) ───────────────────────────
const requiredEnvVars = ['PORT', 'MONGO_URI', 'JWT_SECRET', 'JWT_REFRESH_SECRET'];

requiredEnvVars.forEach((key) => {
  if (!process.env[key]) {
    console.error(`FATAL: Missing required env var: ${key}`);
    process.exit(1);
  }
});

// ─── Environment config ───────────────────────────────────────────────────────
const config = {
  port: process.env.PORT || 5000,
  nodeEnv: process.env.NODE_ENV || 'development',
  mongo: { uri: process.env.MONGO_URI },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '15m',
    refreshSecret: process.env.JWT_REFRESH_SECRET,
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
  },
};

// ─── HTTP response codes ──────────────────────────────────────────────────────
const ResponseCodes = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE: 422,
  SERVER_ERROR: 500,
};

// ─── Roles ────────────────────────────────────────────────────────────────────
const Roles = {
  ADMIN: 'admin',
  USER: 'user',
};

// ─── Error codes ──────────────────────────────────────────────────────────────
const ErrorCodes = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  DUPLICATE: 'DUPLICATE_ERROR',
  INVALID_TOKEN: 'INVALID_TOKEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  SERVER_ERROR: 'SERVER_ERROR',
};

module.exports = { config, ResponseCodes, Roles, ErrorCodes };
```

> **Rule:** `process.env.X` is only accessed inside `config/constants.js`. Every other file imports `config`, `ResponseCodes`, `Roles`, or `ErrorCodes` from there.

---

## 4. API Design Rules

### URL Structure
```
/api/{resource}              → collection
/api/{resource}/:id          → single item
/api/{resource}/:id/{sub}    → sub-resource (use sparingly)
```

### HTTP Method Mapping
| Action | Method | Example |
|---|---|---|
| List all | GET | `GET /api/users` |
| Get one | GET | `GET /api/users/:id` |
| Create | POST | `POST /api/users` |
| Full update | PUT | `PUT /api/users/:id` |
| Partial update | PATCH | `PATCH /api/users/:id` |
| Delete | DELETE | `DELETE /api/users/:id` |

### Query Parameter Conventions
```
?page=1&limit=20    → pagination
?sort=-createdAt    → sort descending (-) / ascending (no prefix)
?search=john        → text search
?status=active      → field filter
```

---

## 5. Request & Response Format

### Standard Success Response
```js
{
  status: ResponseCodes.OK,
  message: "User fetched successfully",
  data: { }       // always an object — never a raw array or primitive
}
```

### Paginated Response
```js
{
  status: ResponseCodes.OK,
  message: "Users fetched successfully",
  data: {
    users: [ ],     // list nested inside data object
    totalCount: 150 // only totalCount — no page/limit/totalPages
  }
}
```

### Standard Validation Error
```js
{
  status: ResponseCodes.BAD_REQUEST,
  message: "Validation failed",
  error: {
    code: ErrorCodes.VALIDATION_ERROR,
    details: [
      { field: "email", message: "Email is required" }
    ]
  }
}
```

### Standard Server / App Error
```js
{
  success: false,
  message: "Something went wrong",
  error: { code: ErrorCodes.SERVER_ERROR, details: [] }
}
```

> Stack traces are **never** included in production responses.

### HTTP Status Code Map
| Situation | Constant | Code |
|---|---|---|
| Success (read) | `ResponseCodes.OK` | 200 |
| Created | `ResponseCodes.CREATED` | 201 |
| No content | `ResponseCodes.NO_CONTENT` | 204 |
| Validation / Bad request | `ResponseCodes.BAD_REQUEST` | 400 |
| Unauthenticated | `ResponseCodes.UNAUTHORIZED` | 401 |
| Forbidden | `ResponseCodes.FORBIDDEN` | 403 |
| Not found | `ResponseCodes.NOT_FOUND` | 404 |
| Conflict / Duplicate | `ResponseCodes.CONFLICT` | 409 |
| Server error | `ResponseCodes.SERVER_ERROR` | 500 |

---

## 6. apiResponse Utility

```js
// src/utils/apiResponse.js
const { ResponseCodes, ErrorCodes } = require('../config/constants');

class ApiResponse {
  constructor(statusCode, message, data = {}) {
    this.statusCode = statusCode;
    this.success = statusCode < 400;
    this.message = message;
    this.data = data;
  }

  send(res) {
    return res.status(this.statusCode).json({
      success: this.success,
      message: this.message,
      data: this.data,
    });
  }
}

const sendError = (res, {
  statusCode = ResponseCodes.SERVER_ERROR,
  message = 'Something went wrong',
  code = ErrorCodes.SERVER_ERROR,
  details = [],
} = {}) => {
  return res.status(statusCode).json({
    success: false,
    message,
    error: { code, details },
  });
};

module.exports = { ApiResponse, sendError };
```

**Usage:**
```js
// Success
return new ApiResponse(ResponseCodes.OK, 'User fetched', { user }).send(res);

// Error
return sendError(res, { statusCode: ResponseCodes.NOT_FOUND, message: 'User not found', code: ErrorCodes.NOT_FOUND });
```

---

## 7. Middleware Stack Order

Configure in `src/app.js` in exactly this order:

```js
app.use(cors(corsOptions));
app.use(helmet());
app.use(rateLimiter);
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));

// Routes
app.use('/api', router);

// 404 Handler — after all routes
app.use((req, res) => {
  const { sendError } = require('./utils/apiResponse');
  const { ResponseCodes, ErrorCodes } = require('./config/constants');
  sendError(res, {
    statusCode: ResponseCodes.NOT_FOUND,
    message: `Route ${req.originalUrl} not found`,
    code: ErrorCodes.NOT_FOUND,
  });
});

// Global Error Handler — always last
app.use(errorHandler);
```

---

## 8. Middleware Files

### `hasToken.js` — verifies JWT, seeds req.user
```js
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { config, ResponseCodes, ErrorCodes } = require('../config/constants');
const { sendError } = require('../utils/apiResponse');

const hasToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return sendError(res, {
        statusCode: ResponseCodes.UNAUTHORIZED,
        message: 'No token provided',
        code: ErrorCodes.UNAUTHORIZED,
      });
    }
    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, config.jwt.secret);
    const user = await User.findOne({ _id: decoded.id, isDeleted: false }).lean();
    if (!user) {
      return sendError(res, {
        statusCode: ResponseCodes.UNAUTHORIZED,
        message: 'Invalid token',
        code: ErrorCodes.INVALID_TOKEN,
      });
    }
    req.user = { ...user, isAuthenticated: true };  // flag set here
    next();
  } catch (err) {
    const code = err.name === 'TokenExpiredError' ? ErrorCodes.TOKEN_EXPIRED : ErrorCodes.INVALID_TOKEN;
    return sendError(res, { statusCode: ResponseCodes.UNAUTHORIZED, message: err.message, code });
  }
};

module.exports = hasToken;
```

### `isAuthenticated.js`
```js
const { sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes } = require('../config/constants');

const isAuthenticated = (req, res, next) => {
  if (req.user && req.user.isAuthenticated === true) return next();
  return sendError(res, {
    statusCode: ResponseCodes.UNAUTHORIZED,
    message: 'Not authenticated',
    code: ErrorCodes.UNAUTHORIZED,
  });
};

module.exports = isAuthenticated;
```

### `isAdmin.js`
```js
const { sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes, Roles } = require('../config/constants');

const isAdmin = (req, res, next) => {
  if (req.user && req.user.role === Roles.ADMIN) return next();
  return sendError(res, {
    statusCode: ResponseCodes.FORBIDDEN,
    message: 'Admin access required',
    code: ErrorCodes.FORBIDDEN,
  });
};

module.exports = isAdmin;
```

### `isUser.js`
```js
const { sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes, Roles } = require('../config/constants');

const isUser = (req, res, next) => {
  if (req.user && req.user.role === Roles.USER) return next();
  return sendError(res, {
    statusCode: ResponseCodes.FORBIDDEN,
    message: 'User access required',
    code: ErrorCodes.FORBIDDEN,
  });
};

module.exports = isUser;
```

### Middleware chain pattern
```js
// Public route
router.post('/register', createUserRules, UserController.register);

// Any authenticated user
router.get('/profile', hasToken, isAuthenticated, UserController.getProfile);

// Admin only
router.get('/all', hasToken, isAuthenticated, isAdmin, UserController.getAllUsers);
```

### `errorHandler.js` — global Express error handler (4-arg, always last)
```js
const { sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes } = require('../config/constants');

const errorHandler = (err, req, res, next) => {
  let statusCode = err.statusCode || ResponseCodes.SERVER_ERROR;
  let code = ErrorCodes.SERVER_ERROR;
  let message = 'Something went wrong';
  let details = [];

  if (err.name === 'CastError') {
    statusCode = ResponseCodes.BAD_REQUEST; code = 'INVALID_ID'; message = 'Invalid ID format';
  }
  if (err.name === 'ValidationError') {
    statusCode = ResponseCodes.BAD_REQUEST; code = ErrorCodes.VALIDATION_ERROR;
    message = 'Validation failed';
    details = Object.values(err.errors).map(e => ({ field: e.path, message: e.message }));
  }
  if (err.code === 11000) {
    statusCode = ResponseCodes.CONFLICT; code = ErrorCodes.DUPLICATE;
    message = `${Object.keys(err.keyValue)[0]} already exists`;
  }
  if (err.name === 'JsonWebTokenError') {
    statusCode = ResponseCodes.UNAUTHORIZED; code = ErrorCodes.INVALID_TOKEN; message = 'Invalid token';
  }
  if (err.name === 'TokenExpiredError') {
    statusCode = ResponseCodes.UNAUTHORIZED; code = ErrorCodes.TOKEN_EXPIRED; message = 'Token expired';
  }

  if (process.env.NODE_ENV === 'development') console.error(err);

  return sendError(res, { statusCode, message, code, details });
};

module.exports = errorHandler;
```

---

## 9. Mongoose Model (UUID `_id`)

```js
// src/models/User.js
const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { Roles } = require('../config/constants');

const userSchema = new mongoose.Schema(
  {
    _id:             { type: String, default: uuidv4 },
    name:            { type: String, required: [true, 'Name is required'], trim: true },
    email:           { type: String, required: [true, 'Email is required'], unique: true, lowercase: true, trim: true, index: true },
    password:        { type: String, required: true, select: false },
    role:            { type: String, enum: Object.values(Roles), default: Roles.USER },
    isAuthenticated: { type: Boolean, default: false },
    isDeleted:       { type: Boolean, default: false },
  },
  {
    timestamps: true,
    _id: false,
    toJSON: {
      transform(doc, ret) {
        delete ret.__v;
        delete ret.password;
      },
    },
  }
);

module.exports = mongoose.model('User', userSchema);
```

### Mongoose Query Rules
- `.lean()` on all read-only queries
- Always include `{ isDeleted: false }` in every find query
- Soft delete only — never `.deleteOne()` on user-facing records
- Indexes defined inline on schema fields
- `password` has `select: false` — add `.select('+password')` only when explicitly needed (e.g. login)

---

## 10. PostgreSQL Schema (if used)

When PostgreSQL is used, maintain `database/schema.sql` with UUID primary keys.

```sql
-- database/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(100) NOT NULL,
  email             VARCHAR(255) NOT NULL UNIQUE,
  password          VARCHAR(255) NOT NULL,
  role              VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  is_authenticated  BOOLEAN NOT NULL DEFAULT FALSE,
  is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
  created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users(role);
```

> Add a `CREATE TABLE` block per model following the same UUID + `is_deleted` + timestamps pattern. Every table gets its own trigger.

---

## 11. Validation Layer (express-validator)

```js
// src/validators/userValidator.js
const { body, validationResult } = require('express-validator');
const { sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes } = require('../config/constants');

const validateRequest = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const details = errors.array().map(e => ({ field: e.path, message: e.msg }));
    return sendError(res, {
      statusCode: ResponseCodes.BAD_REQUEST,
      message: 'Validation failed',
      code: ErrorCodes.VALIDATION_ERROR,
      details,
    });
  }
  next();
};

const createUserRules = [
  body('name').trim().notEmpty().withMessage('Name is required'),
  body('email').trim().isEmail().normalizeEmail().withMessage('Valid email is required'),
  body('password')
    .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
    .matches(/\d/).withMessage('Password must contain a number'),
  validateRequest,
];

const updateUserRules = [
  body('name').optional().trim().notEmpty().withMessage('Name cannot be empty'),
  body('email').optional().trim().isEmail().normalizeEmail().withMessage('Valid email is required'),
  validateRequest,
];

module.exports = { createUserRules, updateUserRules };
```

**Rules:**
- Validation always runs **before** the controller in the route chain
- `validateRequest` is always the **last item** in every rules array
- Always sanitize: `.trim()`, `.normalizeEmail()`, `.escape()` where applicable

---

## 12. Controller Pattern

Every controller is **PascalCase**, has a **JSDoc block on every method**, and uses **try/catch** directly.

```js
// src/controllers/UserController.js
const User = require('../models/User');
const { ApiResponse, sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes } = require('../config/constants');

/**
 * @name getUser
 * @file UserController.js
 * @param {Request} req
 * @param {Response} res
 * @description Fetches a single user by ID. Requires a valid Access Token.
 * @author Ravi Patel
 */
const getUser = async (req, res) => {
  try {
    const user = await User.findOne({ _id: req.params.id, isDeleted: false }).lean();
    if (!user) {
      return sendError(res, { statusCode: ResponseCodes.NOT_FOUND, message: 'User not found', code: ErrorCodes.NOT_FOUND });
    }
    return new ApiResponse(ResponseCodes.OK, 'User fetched successfully', { user }).send(res);
  } catch (err) {
    return sendError(res, { statusCode: ResponseCodes.SERVER_ERROR, message: err.message });
  }
};

/**
 * @name createUser
 * @file UserController.js
 * @param {Request} req
 * @param {Response} res
 * @description Creates a new user. Requires a valid Admin Access Token.
 * @author Ravi Patel
 */
const createUser = async (req, res) => {
  try {
    const { name, email, password } = req.body;
    const existing = await User.findOne({ email, isDeleted: false }).lean();
    if (existing) {
      return sendError(res, { statusCode: ResponseCodes.CONFLICT, message: 'Email already in use', code: ErrorCodes.DUPLICATE });
    }
    const user = await User.create({ name, email, password });
    return new ApiResponse(ResponseCodes.CREATED, 'User created successfully', { user }).send(res);
  } catch (err) {
    return sendError(res, { statusCode: ResponseCodes.SERVER_ERROR, message: err.message });
  }
};

/**
 * @name getAllUsers
 * @file UserController.js
 * @param {Request} req
 * @param {Response} res
 * @description Returns a paginated list of all users with totalCount. Admin only.
 * @author Ravi Patel
 */
const getAllUsers = async (req, res) => {
  try {
    const page  = parseInt(req.query.page)  || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip  = (page - 1) * limit;

    const [users, totalCount] = await Promise.all([
      User.find({ isDeleted: false }).lean().skip(skip).limit(limit),
      User.countDocuments({ isDeleted: false }),
    ]);

    return new ApiResponse(ResponseCodes.OK, 'Users fetched successfully', { users, totalCount }).send(res);
  } catch (err) {
    return sendError(res, { statusCode: ResponseCodes.SERVER_ERROR, message: err.message });
  }
};

module.exports = { getUser, createUser, getAllUsers };
```

**Controller rules:**
- JSDoc comment block **always first**, then the function
- Direct DB calls (Mongoose) inside the controller — no service layer
- `try/catch` in every async method — no catchAsync wrapper
- Response always uses `ApiResponse` (success) or `sendError` (failure)
- Never call `res.json()` or `res.status()` directly
- Passwords and all sensitive fields must **never** appear in any response

---

## 13. Route Definitions

```js
// src/routes/userRoutes.js
const express = require('express');
const router = express.Router();
const hasToken        = require('../middlewares/hasToken');
const isAuthenticated = require('../middlewares/isAuthenticated');
const isAdmin         = require('../middlewares/isAdmin');
const { createUserRules, updateUserRules } = require('../validators/userValidator');
const { getUser, createUser, getAllUsers } = require('../controllers/UserController');

router.get('/:id', hasToken, isAuthenticated,          getUser);
router.get('/',    hasToken, isAuthenticated, isAdmin,  getAllUsers);
router.post('/',   hasToken, isAuthenticated, isAdmin,  createUserRules, createUser);

module.exports = router;
```

```js
// src/routes/index.js
const express = require('express');
const router = express.Router();

router.use('/users', require('./userRoutes'));
router.use('/auth',  require('./authRoutes'));

module.exports = router;
```

---

## 14. Entry Point

```js
// server.js
require('dotenv').config();
const mongoose = require('mongoose');
const app = require('./src/app');
const { config } = require('./src/config/constants');

const start = async () => {
  await mongoose.connect(config.mongo.uri);
  console.log('MongoDB connected');
  app.listen(config.port, () => {
    console.log(`Server running on port ${config.port} [${config.nodeEnv}]`);
  });
};

start().catch((err) => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
```

---

## 15. Production Checklist

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
