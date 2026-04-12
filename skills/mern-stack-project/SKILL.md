---
name: mern-stack-project
description: >
  Use this skill whenever the user asks to scaffold, design, build, or review any part of a MERN
  stack application intended for production. Triggers include: "create a MERN project", "set up
  folder structure", "design the API", "build a REST endpoint", "add auth", "set up Express routes",
  "create a Mongoose model", "add middleware", "set up error handling", "write a controller",
  "add validation", or any request to generate backend or frontend code within a MERN context.
  Also trigger when the user shares existing MERN code and asks for a review, refactor, or
  production-readiness check. Always use this skill even if the user only asks about one part
  (e.g. just a model or just a route) — the standards here apply to every layer.
---

# MERN Production Skill

A complete rulebook for scaffolding and building production-grade MERN stack applications.
Covers folder structure, API design, response formatting, validation, auth, error handling, and more.

---

## 1. Repository Structure

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

---

## 2. Naming Conventions

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

---

## 3. Config & Constants

There is only **one file** in `src/config/` — `constants.js`. It handles both environment loading and all static app values. There is no separate `index.js`.

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
  status: ResponseCodes.OK,           // numeric HTTP status from constants
  message: "User fetched successfully",
  data: { }                           // always an object — never a raw array or primitive
}
```

### Paginated Response
```js
{
  status: ResponseCodes.OK,
  message: "Users fetched successfully",
  data: {
    users: [ ],        // list nested inside data object
    totalCount: 150    // only totalCount — no page/limit/totalPages in response
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

**Usage in controllers:**
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
    req.user = { ...user, isAuthenticated: true };   // isAuthenticated flag set here
    next();
  } catch (err) {
    const code = err.name === 'TokenExpiredError' ? ErrorCodes.TOKEN_EXPIRED : ErrorCodes.INVALID_TOKEN;
    return sendError(res, { statusCode: ResponseCodes.UNAUTHORIZED, message: err.message, code });
  }
};

module.exports = hasToken;
```

### `isAuthenticated.js` — guards any route requiring a verified user
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

### Middleware chain pattern on routes
```js
// Public route (no auth)
router.post('/register', createUserRules, UserController.register);

// Any authenticated user
router.get('/profile', hasToken, isAuthenticated, UserController.getProfile);

// Admin only
router.get('/all', hasToken, isAuthenticated, isAdmin, UserController.getAllUsers);
```

### `errorHandler.js` — global Express error handler
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

All Mongoose models use UUID strings as `_id` instead of the default ObjectId.

```js
// src/models/User.js
const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { Roles } = require('../config/constants');

const userSchema = new mongoose.Schema(
  {
    _id: { type: String, default: uuidv4 },
    name: { type: String, required: [true, 'Name is required'], trim: true },
    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true,
      index: true,
    },
    password:        { type: String, required: true, select: false },  // never returned by default
    role:            { type: String, enum: Object.values(Roles), default: Roles.USER },
    isAuthenticated: { type: Boolean, default: false },
    isDeleted:       { type: Boolean, default: false },
  },
  {
    timestamps: true,
    _id: false,         // disable auto ObjectId — UUID is supplied via default above
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

When PostgreSQL is used instead of or alongside MongoDB, maintain `database/schema.sql` with UUID primary keys.

```sql
-- database/schema.sql

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
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

-- Auto-update updated_at on row change
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users(role);
```

> Add a new `CREATE TABLE` block per model following the same UUID + `is_deleted` + timestamp pattern. Every table gets its own `update_updated_at` trigger.

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

Every controller file is **PascalCase**, has a **JSDoc block on every method**, and uses **try/catch** directly.

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
      return sendError(res, {
        statusCode: ResponseCodes.NOT_FOUND,
        message: 'User not found',
        code: ErrorCodes.NOT_FOUND,
      });
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
      return sendError(res, {
        statusCode: ResponseCodes.CONFLICT,
        message: 'Email already in use',
        code: ErrorCodes.DUPLICATE,
      });
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
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;

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
- No `res.json()` or `res.status()` called directly — always go through the utilities
- Passwords and all sensitive fields must **never** appear in any response

---

## 13. Route Definitions

```js
// src/routes/userRoutes.js
const express = require('express');
const router = express.Router();
const hasToken = require('../middlewares/hasToken');
const isAuthenticated = require('../middlewares/isAuthenticated');
const isAdmin = require('../middlewares/isAdmin');
const { createUserRules, updateUserRules } = require('../validators/userValidator');
const { getUser, createUser, getAllUsers } = require('../controllers/UserController');

router.get('/:id', hasToken, isAuthenticated, getUser);
router.get('/',    hasToken, isAuthenticated, isAdmin, getAllUsers);
router.post('/',   hasToken, isAuthenticated, isAdmin, createUserRules, createUser);

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

## 14. Frontend — Redux Toolkit

All global state is managed with **Redux Toolkit**. Context API is not used for global state.

```js
// src/store/index.js
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './slices/userSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
  },
});
```

```js
// src/store/slices/userSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchUserApi } from '../../api/userApi';

export const fetchUser = createAsyncThunk('user/fetchUser', async (id, { rejectWithValue }) => {
  try {
    const { data } = await fetchUserApi(id);
    return data.data.user;
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to fetch user');
  }
});

const userSlice = createSlice({
  name: 'user',
  initialState: { currentUser: null, loading: false, error: null },
  reducers: {
    clearUser: (state) => { state.currentUser = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending,   (state) => { state.loading = true; state.error = null; })
      .addCase(fetchUser.fulfilled, (state, action) => { state.loading = false; state.currentUser = action.payload; })
      .addCase(fetchUser.rejected,  (state, action) => { state.loading = false; state.error = action.payload; });
  },
});

export const { clearUser } = userSlice.actions;
export default userSlice.reducer;
```

---

## 15. Entry Point

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

## 16. Production Checklist

### Naming & Structure
- [ ] Controller filenames are PascalCase — `UserController.js`
- [ ] Model filenames are PascalCase — `User.js`, `FavouriteService.js`
- [ ] Route, middleware, validator, and util filenames are camelCase
- [ ] No dots in filenames except the file extension (`.js`, `.json`, `.sql`)
- [ ] No service layer files — all logic lives directly in controllers

### API & Responses
- [ ] All routes follow `/api/{resource}` pattern (no `/v1/` prefix)
- [ ] Every success response uses `new ApiResponse(...).send(res)`
- [ ] Every error response uses `sendError(res, { ... })`
- [ ] `data` field is always an object — never a raw array or primitive
- [ ] Paginated responses include `totalCount` only — not `page`, `limit`, or `totalPages`
- [ ] HTTP status codes always reference `ResponseCodes` — never raw numbers
- [ ] Error codes always reference `ErrorCodes` — never raw strings

### Controllers
- [ ] Every controller method has a JSDoc block (`@name`, `@file`, `@param`, `@description`, `@author`)
- [ ] Every async method uses `try/catch` — no catchAsync wrapper
- [ ] No direct `res.json()` or `res.status()` calls — always use utilities

### Security & Auth
- [ ] `password` field has `select: false` on schema — never returned in any response
- [ ] Other sensitive fields (tokens, secrets) also have `select: false`
- [ ] Protected routes use `hasToken → isAuthenticated` middleware chain
- [ ] Role-restricted routes add `isAdmin` or `isUser` after `isAuthenticated`
- [ ] Auth endpoints have stricter rate limiting

### Models & Database
- [ ] All Mongoose models use UUID `_id` (`default: uuidv4`, `_id: false` in schema options)
- [ ] All schemas include `timestamps: true`
- [ ] `toJSON` transform removes `__v` and `password`
- [ ] Soft delete via `isDeleted: false` — all find queries include this filter
- [ ] PostgreSQL: `database/schema.sql` maintained with UUID PKs, `is_deleted`, and timestamp columns per table

### Config & Environment
- [ ] `process.env.X` only accessed inside `config/constants.js`
- [ ] All static values and env config imported from `config/constants.js`
- [ ] App exits at startup if required env vars are missing

### Error Handling
- [ ] `errorHandler.js` registered as the very last middleware in `app.js`
- [ ] 404 handler registered after all routes, before `errorHandler`
- [ ] Stack traces never included in production error responses

### Frontend
- [ ] Redux Toolkit used for all global state — no Context API for global data
- [ ] One slice per feature inside `store/slices/`
- [ ] All API calls isolated in `src/api/` files
