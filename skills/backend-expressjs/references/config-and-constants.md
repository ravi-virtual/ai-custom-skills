# Config & Constants

Part of the `backend-expressjs` skill. Read this when the task touches the topics below.

## Contents
- [Config & Constants](#config--constants)

## Config & Constants

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
  // Exact origin of the React app (no trailing slash). Used by CORS in app.js.
  clientUrl: process.env.CLIENT_URL || 'http://localhost:5173',
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
