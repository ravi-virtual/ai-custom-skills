# BACKEND.md — Backend Engineering Reference

## Backend Stack
- Runtime: Node.js 20.x LTS
- Framework: Express.js 4.x
- Database: MongoDB 7.x (via Mongoose 8.x)
- Auth: JWT (jsonwebtoken 9.x)
- Validation: express-validator 7.x
- Password: bcryptjs 2.x

---

## Project Structure
```
backend/
├── src/
│   ├── config/
│   │   └── constants.js         ← ALL env vars + ALL constants here
│   ├── controllers/              ← Business logic (PascalCase)
│   ├── middlewares/              ← Auth, validation, rate limit (camelCase)
│   ├── models/                   ← Mongoose schemas (PascalCase)
│   ├── routes/                   ← Route definitions only (camelCase)
│   ├── validators/               ← express-validator rules (camelCase)
│   ├── utils/
│   │   └── apiResponse.js       ← ApiResponse + sendError
│   └── app.js                   ← Express app configuration
├── .env                          ← Environment variables (never commit)
├── .env.example                  ← Template (safe to commit)
├── package.json
└── server.js                     ← Entry point (connect DB, start server)
```

---

## constants.js Template
```javascript
'use strict';

const config = {
  PORT: process.env.PORT || 5000,
  NODE_ENV: process.env.NODE_ENV || 'development',
  MONGO_URI: process.env.MONGO_URI,
  JWT_SECRET: process.env.JWT_SECRET,
  JWT_EXPIRES_IN: process.env.JWT_EXPIRES_IN || '15m',
  JWT_REFRESH_SECRET: process.env.JWT_REFRESH_SECRET,
  JWT_REFRESH_EXPIRES_IN: process.env.JWT_REFRESH_EXPIRES_IN || '15m',
  CORS_ORIGIN: process.env.CORS_ORIGIN || 'http://localhost:5173',
};

// Fail fast: validate critical env vars at startup
const required = ['MONGO_URI', 'JWT_SECRET', 'JWT_REFRESH_SECRET'];
required.forEach(key => {
  if (!config[key]) throw new Error(`Missing required env var: ${key}`);
});

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

const ErrorCodes = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  DUPLICATE_ERROR: 'DUPLICATE_ERROR',
  INVALID_TOKEN: 'INVALID_TOKEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  SERVER_ERROR: 'SERVER_ERROR',
};

const Roles = {
  ADMIN: 'admin',
  USER: 'user',
};

module.exports = { config, ResponseCodes, ErrorCodes, Roles };
```

---

## Controller Pattern
```javascript
'use strict';

const { ResponseCodes, ErrorCodes } = require('../config/constants');
const { ApiResponse, sendError } = require('../utils/apiResponse');
const User = require('../models/User');

/**
 * @name getUser
 * @file UserController.js
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @description Retrieves a single user by ID
 */
const getUser = async (req, res) => {
  try {
    const { id } = req.params;
    const user = await User.findOne({ _id: id, isDeleted: false }).lean();
    if (!user) {
      return sendError(res, {
        statusCode: ResponseCodes.NOT_FOUND,
        message: 'User not found',
        code: ErrorCodes.NOT_FOUND,
      });
    }
    return new ApiResponse(ResponseCodes.OK, 'User retrieved', { user }).send(res);
  } catch (err) {
    return sendError(res, {
      statusCode: ResponseCodes.SERVER_ERROR,
      message: err.message,
      code: ErrorCodes.SERVER_ERROR,
    });
  }
};

module.exports = { getUser };
```

---

## Route Pattern
```javascript
'use strict';

const { Router } = require('express');
const { getUser, updateUser, deleteUser } = require('../controllers/UserController');
const { hasToken } = require('../middlewares/hasToken');
const { isAuthenticated } = require('../middlewares/isAuthenticated');
const { isAdmin } = require('../middlewares/isAdmin');
const { isUser } = require('../middlewares/isUser');
const { updateUserRules } = require('../validators/userValidator');

const router = Router();

// Routes with full middleware chain
router.get('/:id', hasToken, isAuthenticated, isUser, getUser);
router.patch('/:id', hasToken, isAuthenticated, isUser, updateUserRules, updateUser);
router.delete('/:id', hasToken, isAuthenticated, isAdmin, deleteUser);

module.exports = router;
```

---

## Model Pattern
```javascript
'use strict';

const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const userSchema = new mongoose.Schema(
  {
    _id: { type: String, default: uuidv4 },
    name: { type: String, required: true, trim: true },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },
    password: { type: String, required: true, select: false },
    role: { type: String, enum: ['admin', 'user'], default: 'user' },
    isDeleted: { type: Boolean, default: false },
  },
  {
    timestamps: true,
    _id: false,
    toJSON: {
      transform(doc, ret) {
        delete ret.__v;
        delete ret.password;
        return ret;
      },
    },
  }
);

const User = mongoose.model('User', userSchema);
module.exports = User;
```

---

## Validator Pattern
```javascript
'use strict';

const { body } = require('express-validator');
const { validateRequest } = require('../middlewares/validateRequest');

const updateUserRules = [
  body('name').optional().trim().isLength({ min: 2, max: 100 }).withMessage('Name must be 2-100 characters'),
  body('email').optional().trim().isEmail().normalizeEmail().withMessage('Must be a valid email'),
  validateRequest,  // Always last
];

module.exports = { updateUserRules };
```

---

## ApiResponse Utility
```javascript
'use strict';

const { ResponseCodes } = require('../config/constants');

class ApiResponse {
  constructor(statusCode, message, data = {}) {
    this.statusCode = statusCode;
    this.message = message;
    this.data = data;
    this.success = statusCode < 400;
  }

  send(res) {
    return res.status(this.statusCode).json({
      success: this.success,
      message: this.message,
      data: this.data,
    });
  }
}

const sendError = (res, { statusCode, message, code, details = [] }) => {
  return res.status(statusCode).json({
    success: false,
    message,
    error: { code, details },
  });
};

module.exports = { ApiResponse, sendError };
```

---

## Middleware Patterns

### hasToken.js
```javascript
'use strict';
const jwt = require('jsonwebtoken');
const { config, ResponseCodes, ErrorCodes } = require('../config/constants');
const { sendError } = require('../utils/apiResponse');

const hasToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return sendError(res, { statusCode: ResponseCodes.UNAUTHORIZED, message: 'No token provided', code: ErrorCodes.UNAUTHORIZED });
  }
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, config.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    const code = err.name === 'TokenExpiredError' ? ErrorCodes.TOKEN_EXPIRED : ErrorCodes.INVALID_TOKEN;
    return sendError(res, { statusCode: ResponseCodes.UNAUTHORIZED, message: err.message, code });
  }
};

module.exports = { hasToken };
```

### validateRequest.js
```javascript
'use strict';
const { validationResult } = require('express-validator');
const { ResponseCodes, ErrorCodes } = require('../config/constants');
const { sendError } = require('../utils/apiResponse');

const validateRequest = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return sendError(res, {
      statusCode: ResponseCodes.UNPROCESSABLE,
      message: 'Validation failed',
      code: ErrorCodes.VALIDATION_ERROR,
      details: errors.array().map(e => ({ field: e.path, message: e.msg })),
    });
  }
  next();
};

module.exports = { validateRequest };
```
