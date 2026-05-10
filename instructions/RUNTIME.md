# RUNTIME.md — Runtime Environment & Configuration

## Purpose
Defines all runtime behavior, environment configuration, server startup sequences, process management, and runtime error handling for the application.

---

## Runtime Architecture

```
┌─────────────────────────────────────────────────┐
│  PM2 Process Manager                            │
│  ├── app-backend (Node.js / Express)  Port 5000 │
│  └── [Optional: Worker processes]               │
└─────────────────────────────────────────────────┘
            │
            │ HTTP
            ▼
┌─────────────────────────────────────────────────┐
│  Nginx Reverse Proxy (Production)               │
│  ├── / → Frontend static files (dist/)          │
│  └── /api/ → Backend (localhost:5000)           │
└─────────────────────────────────────────────────┘
            │
            │
┌─────────────────┐    ┌────────────────────────┐
│  MongoDB Atlas  │    │  AI Provider APIs      │
│  (Database)     │    │  Gemini / Grok / OpenAI│
└─────────────────┘    └────────────────────────┘
```

---

## Section 1: Server Startup Sequence

### startup order in server.js
```javascript
// src/server.js — correct startup order
'use strict';

const app = require('./app');
const { connectDB } = require('./config/database');
const { config } = require('./config/constants');

const startServer = async () => {
  // 1. Validate critical environment variables (fail fast)
  validateEnvironment();

  // 2. Connect to database BEFORE starting HTTP server
  await connectDB();

  // 3. Start HTTP server only after DB is ready
  app.listen(config.PORT, () => {
    console.log(JSON.stringify({
      level: 'info',
      message: 'Server started',
      port: config.PORT,
      environment: config.NODE_ENV,
      timestamp: new Date().toISOString(),
    }));
  });
};

// Fail fast — validate required env vars at startup
const validateEnvironment = () => {
  const required = [
    'MONGO_URI', 'JWT_SECRET', 'JWT_REFRESH_SECRET',
    'JWT_EXPIRES_IN', 'JWT_REFRESH_EXPIRES_IN', 'CORS_ORIGIN'
  ];

  const missing = required.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    console.error(`Missing required environment variables: ${missing.join(', ')}`);
    process.exit(1); // Hard fail — don't start without required config
  }
};

startServer().catch((err) => {
  console.error(JSON.stringify({
    level: 'error',
    message: 'Failed to start server',
    error: err.message,
  }));
  process.exit(1);
});
```

---

## Section 2: Express App Configuration

### app.js middleware registration order
```javascript
// src/app.js — middleware registration order matters
'use strict';

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const rateLimit = require('express-rate-limit');

const { config } = require('./config/constants');
const { attachRequestId } = require('./middlewares/requestId');
const { errorHandler } = require('./middlewares/errorHandler');
const { notFoundHandler } = require('./middlewares/notFoundHandler');

// Import routes
const authRoutes = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const profileRoutes = require('./routes/profileRoutes');
const generateRoutes = require('./routes/generateRoutes');

const app = express();

// ─── SECURITY MIDDLEWARE (First) ───────────────────────────────────────────
app.use(helmet());

app.use(cors({
  origin: config.CORS_ORIGIN,
  credentials: true,               // Required for httpOnly cookies
  methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// ─── RATE LIMITING ──────────────────────────────────────────────────────────
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,       // 15 minutes
  max: 10,                          // 10 attempts per window
  message: { success: false, message: 'Too many attempts. Try again in 15 minutes.' },
  standardHeaders: true,
  legacyHeaders: false,
});

const generalLimiter = rateLimit({
  windowMs: 1 * 60 * 1000,        // 1 minute
  max: 100,                         // 100 requests per minute
  standardHeaders: true,
});

app.use('/api/', generalLimiter);
app.use('/api/auth/', authLimiter);

// ─── REQUEST PARSING ────────────────────────────────────────────────────────
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(cookieParser());

// ─── OBSERVABILITY ──────────────────────────────────────────────────────────
app.use(attachRequestId);
app.use(morgan(config.NODE_ENV === 'production' ? 'combined' : 'dev'));

// ─── ROUTES ─────────────────────────────────────────────────────────────────
app.get('/api/health', (req, res) => res.json({ status: 'healthy', timestamp: new Date().toISOString() }));
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/profile', profileRoutes);
app.use('/api/generate', generateRoutes);

// ─── ERROR HANDLING (Last) ──────────────────────────────────────────────────
app.use(notFoundHandler);   // 404 for unknown routes
app.use(errorHandler);      // 500 for unhandled errors

module.exports = app;
```

---

## Section 3: Runtime Error Handling

### Global Error Handler
```javascript
// src/middlewares/errorHandler.js
'use strict';

const { sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes } = require('../config/constants');

/**
 * @name errorHandler
 * @file errorHandler.js
 * @description Global Express error handler — catches all unhandled errors
 */
const errorHandler = (err, req, res, next) => {
  // Log the full error server-side
  console.error(JSON.stringify({
    level: 'error',
    requestId: req.id,
    method: req.method,
    path: req.path,
    userId: req.user?.id,
    error: err.message,
    stack: err.stack,
  }));

  // Send safe error response (never expose stack trace to client)
  return sendError(res, {
    statusCode: err.statusCode || ResponseCodes.SERVER_ERROR,
    message: err.isOperational ? err.message : 'An unexpected error occurred',
    code: err.code || ErrorCodes.SERVER_ERROR,
  });
};

module.exports = { errorHandler };
```

### Process-Level Error Handling
```javascript
// src/server.js — add after startServer() call

// Unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error(JSON.stringify({
    level: 'error',
    message: 'Unhandled Promise Rejection',
    reason: reason?.message || reason,
  }));
  // Graceful shutdown — let PM2 restart
  process.exit(1);
});

// Uncaught synchronous exceptions
process.on('uncaughtException', (err) => {
  console.error(JSON.stringify({
    level: 'error',
    message: 'Uncaught Exception',
    error: err.message,
    stack: err.stack,
  }));
  // Immediate exit — state is now corrupted
  process.exit(1);
});

// Graceful shutdown on SIGTERM (from PM2 or Docker)
process.on('SIGTERM', async () => {
  console.log(JSON.stringify({ level: 'info', message: 'SIGTERM received — graceful shutdown' }));
  // Close HTTP server (stop accepting new connections)
  // Wait for in-flight requests to complete (max 10s)
  // Close DB connection
  // Exit
  process.exit(0);
});
```

---

## Section 4: Environment Variable Reference

### Complete `.env` Template
```bash
# ── Server ──────────────────────────────────────
PORT=5000
NODE_ENV=development   # development | staging | production

# ── Database ────────────────────────────────────
MONGO_URI=mongodb://localhost:27017/appname_development

# ── JWT Authentication ───────────────────────────
JWT_SECRET=your-minimum-32-char-secret-here-change-in-production
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=another-minimum-32-char-secret-change-in-production
JWT_REFRESH_EXPIRES_IN=15m

# ── CORS ────────────────────────────────────────
CORS_ORIGIN=http://localhost:5173

# ── AI Services ─────────────────────────────────
GEMINI_API_KEY=your-gemini-api-key-here
GROK_API_KEY=your-grok-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# ── Email ────────────────────────────────────────
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
EMAIL_FROM=noreply@yourdomain.com
APP_NAME=ProfilePro

# ── Frontend (Vite) ─────────────────────────────
VITE_API_BASE_URL=http://localhost:5000
```

---

## Section 5: Runtime Performance Tuning

### Node.js Process Flags
```bash
# Increase heap memory if needed (default: ~1.5GB)
node --max-old-space-size=512 src/server.js

# Enable V8 optimizations
node --optimize-for-size src/server.js  # Smaller memory, trades CPU
```

### MongoDB Connection Tuning
```javascript
// Mongoose 8.x — connection options
await mongoose.connect(config.MONGO_URI, {
  maxPoolSize: 10,         // Max concurrent connections (default: 5)
  serverSelectionTimeoutMS: 5000,  // Fail fast if DB unreachable
  socketTimeoutMS: 45000,  // Close idle sockets after 45s
});
```

---

## Runtime Health Indicators

| Indicator | Healthy | Degraded | Critical |
|---|---|---|---|
| `GET /api/health` | 200 | 200 with warnings | 503 |
| DB ping | < 10ms | 10-100ms | > 100ms or timeout |
| Node.js heap | < 70% | 70-85% | > 85% |
| Event loop lag | < 10ms | 10-50ms | > 50ms |
| Request queue | 0 | 1-5 pending | > 5 pending |
