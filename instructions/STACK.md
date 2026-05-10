# STACK.md — Technology Stack Reference

## Core Stack: MERN

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Database | MongoDB | 7.x | Document database |
| Backend | Node.js | 20.x LTS | JavaScript runtime |
| Backend Framework | Express.js | 4.x | HTTP framework |
| Frontend | React | 18.x | UI library |
| Frontend Build | Vite | 5.x | Build tool + dev server |
| State Management | Redux Toolkit | 2.x | Frontend state |

---

## Backend Stack Detail

### Node.js (20.x LTS)
- Runtime for Express server
- Use `require()` / `module.exports` (CommonJS)
- No top-level await (use async IIFE or wrap in async function)
- Environment: `process.env` accessed ONLY in `constants.js`

### Express.js (4.x)
```javascript
// Middleware order (CRITICAL — never reorder)
app.use(cors());           // 1. CORS (must be first)
app.use(helmet());         // 2. Security headers
app.use(rateLimiter);      // 3. Rate limiting
app.use(express.json({ limit: '10kb' }));  // 4. Body parsing
app.use(express.urlencoded({ extended: true }));  // 5. Form data
app.use(morgan('dev'));     // 6. Logging

app.use('/api', router);   // Routes

// After all routes:
app.use(notFoundHandler);  // 404
app.use(errorHandler);     // Global error handler (4-arg, ALWAYS last)
```

### Mongoose (8.x)
- ODM for MongoDB
- Always use UUID string `_id` (not ObjectId)
- Schema options: `{ timestamps: true, _id: false }`
- Query pattern: `.lean()` on all reads
- Always include `{ isDeleted: false }` in queries
- `toJSON transform`: remove `__v` and `password`

### express-validator (7.x)
```javascript
// Usage pattern
const { body, validationResult } = require('express-validator');

const rules = [
  body('email').trim().isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }),
  validateRequest,  // Always last in array
];
```

### jsonwebtoken (9.x)
```javascript
// Sign
jwt.sign(payload, secret, { expiresIn: '15m' });

// Verify
const decoded = jwt.verify(token, secret);
// Throws TokenExpiredError or JsonWebTokenError on failure

// Token extraction
const token = req.headers.authorization?.split(' ')[1];
```

### bcryptjs (2.x)
```javascript
// Hash
const hash = await bcrypt.hash(password, 10);

// Compare
const isMatch = await bcrypt.compare(plaintext, hash);
```

### uuid (9.x)
```javascript
const { v4: uuidv4 } = require('uuid');
// Usage in schema:
_id: { type: String, default: uuidv4 }
```

### express-rate-limit (7.x)
```javascript
const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                    // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});
```

---

## Frontend Stack Detail

### React (18.x)
- Functional components only (no class components)
- Hooks for all state and side effects
- StrictMode enabled in development
- JSX files use `.jsx` extension

### Vite (5.x)
```bash
# Dev server
npm run dev      # http://localhost:5173

# Environment variables
VITE_API_BASE_URL=http://localhost:5000  # .env file
# Access: import.meta.env.VITE_API_BASE_URL
# BUT: only in src/utils/constants.js
```

### Redux Toolkit (2.x)
```javascript
// Store setup
import { configureStore } from '@reduxjs/toolkit';

// Slice creation
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// In components
import { useSelector, useDispatch } from 'react-redux';
```

### React Router (6.x)
```jsx
// Setup
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Navigation
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
navigate('/path');

// Protected routes
<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
```

### Axios (1.x)
```javascript
// Instance creation
const instance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Interceptors
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

instance.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) { /* handle */ }
    return Promise.reject(error);
  }
);
```

---

## Development Tools

| Tool | Purpose | Config File |
|------|---------|------------|
| ESLint | Code linting | `.eslintrc.js` |
| Prettier | Code formatting | `.prettierrc` |
| nodemon | Auto-restart dev server | `nodemon.json` |
| dotenv | Env var loading | `.env` |

---

## Environment Variable Reference

### Backend `.env`
```
PORT=5000
NODE_ENV=development
MONGO_URI=mongodb://localhost:27017/dbname
JWT_SECRET=your-very-long-random-jwt-secret
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=your-very-long-random-refresh-secret
JWT_REFRESH_EXPIRES_IN=15m
CORS_ORIGIN=http://localhost:5173
```

### Frontend `.env`
```
VITE_API_BASE_URL=http://localhost:5000
```

---

## Package Manager: npm
```bash
# Install
npm install

# Add dependency
npm install package-name

# Add dev dependency
npm install -D package-name

# Run scripts
npm run dev      # Start development server
npm run build    # Build for production
npm test         # Run tests
```

---

## Version Upgrade Policy
- **Patch versions** (x.x.1 → x.x.2): Apply immediately (bug fixes)
- **Minor versions** (x.1.0 → x.2.0): Apply after reviewing changelog
- **Major versions** (1.x.x → 2.x.x): Plan migration with full testing
- Never upgrade multiple major dependencies simultaneously
- Always test after any dependency upgrade
