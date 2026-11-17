# Middleware Stack & Middleware Files

Part of the `backend-expressjs` skill. Read this when the task touches the topics below.

## Contents
- [Middleware Stack Order](#middleware-stack-order)
- [Middleware Files](#middleware-files)

## Middleware Stack Order

Configure in `src/app.js` in exactly this order:

```js
const { config } = require('./config/constants');

// An exact origin is required when credentials (cookies / Authorization) are used;
// `origin: '*'` together with `credentials: true` is rejected by browsers.
const corsOptions = {
  origin: config.clientUrl,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
};

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

## Middleware Files

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
