# SECURITY.md — Security Engineering Standards

## Security Philosophy
Security is a first-class engineering concern, not a last-minute checkbox. Every feature must be designed with the threat model in mind before any code is written.

## Threat Model Summary

| Threat Category | Risk Level | Primary Defense |
|---|---|---|
| Credential theft | Critical | JWT short expiry, httpOnly cookies, bcrypt |
| Unauthorized access | Critical | Auth middleware on all protected routes |
| Injection attacks | High | express-validator, parameterized queries |
| Brute force | High | Rate limiting, account lockout |
| Data exposure | High | select: false on sensitive fields, toJSON transform |
| XSS | Medium | Helmet CSP, input sanitization |
| CSRF | Medium | SameSite cookies, CORS policy |
| Information leakage | Medium | No stack traces in responses, masked errors |

---

## Section 1: Authentication Security

### 1.1 JWT Rules
```javascript
// Access token: short-lived
jwt.sign(payload, config.JWT_SECRET, { expiresIn: '15m' });

// Refresh token: longer-lived, rotated on use
jwt.sign(payload, config.JWT_REFRESH_SECRET, { expiresIn: '15m' });

// Verification — always check BOTH error types
try {
  const decoded = jwt.verify(token, config.JWT_SECRET);
} catch (err) {
  if (err.name === 'TokenExpiredError') {
    // Return TOKEN_EXPIRED code — different handling on frontend
  } else {
    // Return INVALID_TOKEN code
  }
}
```

### 1.2 Token Storage
```
Server-side:
✅ httpOnly cookie for refresh token (not accessible to JavaScript)
✅ In-memory or localStorage for access token (short-lived, acceptable)
❌ Never store refresh token in localStorage
❌ Never store tokens in Redux state (persisted to localStorage)
```

### 1.3 Password Rules
```javascript
// Hashing — always bcrypt with cost 10+
const hash = await bcrypt.hash(password, 10);

// Comparison — always bcrypt.compare, never string compare
const isMatch = await bcrypt.compare(plaintext, hash);

// Schema — always select: false
password: { type: String, required: true, select: false }

// toJSON — always strip password from responses
toJSON: { transform(doc, ret) { delete ret.password; return ret; } }
```

---

## Section 2: Authorization Security

### 2.1 Middleware Chain (Non-Negotiable)
```
hasToken → isAuthenticated → [isAdmin | isUser] → validator → controller

hasToken:        Verifies JWT, sets req.user
isAuthenticated: Verifies user still active (not banned/deleted)
isAdmin/isUser:  Checks role before allowing access
```

### 2.2 Role-Based Access Control
```javascript
// isAdmin.js — never check role in controller
const isAdmin = (req, res, next) => {
  if (req.user.role !== Roles.ADMIN) {
    return sendError(res, { statusCode: ResponseCodes.FORBIDDEN, message: 'Insufficient permissions', code: ErrorCodes.FORBIDDEN });
  }
  next();
};

// isUser.js — allows user and admin (admin can access user routes)
const isUser = (req, res, next) => {
  if (![Roles.USER, Roles.ADMIN].includes(req.user.role)) {
    return sendError(res, { statusCode: ResponseCodes.FORBIDDEN, message: 'Insufficient permissions', code: ErrorCodes.FORBIDDEN });
  }
  next();
};
```

### 2.3 Resource Authorization
```javascript
// When user can only access their own resource:
const getProfile = async (req, res) => {
  try {
    const { id } = req.params;
    // Check ownership: req.user.id from JWT must match resource owner
    if (req.user.id !== id && req.user.role !== Roles.ADMIN) {
      return sendError(res, { statusCode: ResponseCodes.FORBIDDEN, message: 'Access denied' });
    }
    // proceed
  } catch (err) { /* ... */ }
};
```

---

## Section 3: Input Security

### 3.1 Validation Rules (express-validator)
```javascript
// Always validate and sanitize
body('email').trim().isEmail().normalizeEmail()
body('password').isLength({ min: 8, max: 128 })
body('name').trim().isLength({ min: 2, max: 100 }).escape()
body('phone').optional().isMobilePhone()

// For IDs in params
param('id').isUUID(4)

// For pagination
query('page').optional().isInt({ min: 1 }).toInt()
query('limit').optional().isInt({ min: 1, max: 100 }).toInt()
```

### 3.2 MongoDB Injection Prevention
```javascript
// ✅ Safe — Mongoose parameterizes all queries
const user = await User.findOne({ email });

// ✅ Safe — UUID validation prevents injection
const user = await User.findOne({ _id: validatedUUID });

// ❌ Unsafe — never use raw user input in query operators
const users = await User.find({ $where: `this.name == '${name}'` }); // NEVER
```

### 3.3 Body Size Limits
```javascript
app.use(express.json({ limit: '10kb' })); // Prevent large payload attacks
app.use(express.urlencoded({ extended: true, limit: '10kb' }));
```

---

## Section 4: HTTP Security Headers (Helmet)

```javascript
app.use(helmet()); // Sensible defaults include:
// X-Content-Type-Options: nosniff
// X-Frame-Options: DENY
// X-XSS-Protection: 0 (modern browsers use CSP instead)
// Strict-Transport-Security (in production)
// Referrer-Policy: no-referrer

// Additional custom headers for production
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
  }
}));
```

---

## Section 5: CORS Configuration

```javascript
const corsOptions = {
  origin: (origin, callback) => {
    const allowed = config.CORS_ORIGIN.split(',').map(o => o.trim());
    if (!origin || allowed.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
};
app.use(cors(corsOptions));
```

---

## Section 6: Sensitive Data Rules

### 6.1 Never Expose
- Passwords (even hashed) in API responses
- JWT secrets or private keys
- Database connection strings
- Internal error messages or stack traces in production
- User PII in logs beyond what's operationally necessary

### 6.2 Response Scrubbing
```javascript
// toJSON transform on every model
toJSON: {
  transform(doc, ret) {
    delete ret.__v;
    delete ret.password;
    delete ret.refreshToken; // if stored on model
    return ret;
  }
}

// Error handler: mask server errors in production
if (config.NODE_ENV === 'production' && statusCode === 500) {
  message = 'Internal server error'; // Don't expose err.message
}
```

### 6.3 Environment Variables
```
✅ Store in .env file, never commit to version control
✅ Always list in .env.example with placeholder values
✅ Access ONLY in src/config/constants.js
✅ Validate existence at startup (fail fast)
❌ Never log env vars
❌ Never embed in client-side code (except VITE_ vars)
❌ Never hardcode in any source file
```

---

## Section 7: Rate Limiting

```javascript
import rateLimit from 'express-rate-limit';

// General API rate limit
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: 'Too many requests, please try again later',
});

// Stricter limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,  // Only 10 login/register attempts per 15 min
  message: 'Too many authentication attempts',
});

app.use('/api', apiLimiter);
app.use('/api/auth', authLimiter);
```

---

## Security Audit Checklist
Before any deployment, verify:
- [ ] All protected routes have `hasToken + isAuthenticated` middleware
- [ ] Admin routes additionally have `isAdmin` middleware
- [ ] No `process.env.X` outside constants.js
- [ ] No sensitive data in API responses (test with Postman)
- [ ] Helmet middleware is active
- [ ] CORS is restricted to known origins
- [ ] Rate limiting is active on all routes
- [ ] Input validation on all POST/PUT/PATCH endpoints
- [ ] No stack traces in production error responses
- [ ] Password has `select: false` on all User-like schemas
- [ ] JWT uses strong secrets (minimum 32 characters)
- [ ] Access token expires in 15 minutes or less
