# Validation, Controllers, Routes & Entry Point

Part of the `backend-expressjs` skill. Read this when the task touches the topics below.

## Contents
- [Validation Layer (express-validator)](#validation-layer-express-validator)
- [Controller Pattern](#controller-pattern)
- [Route Definitions](#route-definitions)
- [Entry Point](#entry-point)

## Validation Layer (express-validator)

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

## Controller Pattern

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

## Route Definitions

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

## Entry Point

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
