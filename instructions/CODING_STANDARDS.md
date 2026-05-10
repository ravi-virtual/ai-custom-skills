# CODING_STANDARDS.md — Code Quality Standards

## Philosophy
Code is written once and read many times. Every standard here exists to make code predictable, safe, and maintainable by any engineer (human or AI) without needing to ask questions.

---

## Section 1: Universal Standards

### 1.1 File Header
Every new file begins with:
```javascript
'use strict';
// For backend files (CommonJS)
```
Or:
```javascript
// src/[path/to/file.js] — optional but helpful in large projects
```

### 1.2 Variable Declarations
- Use `const` by default
- Use `let` only when reassignment is needed
- Never use `var`
- Declare one variable per line

### 1.3 Naming
| Entity | Convention | Example |
|---|---|---|
| Variables | camelCase | `userProfile`, `isLoading` |
| Constants (module-level) | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_LIMIT` |
| Functions | camelCase | `getUserById`, `formatDate` |
| Classes | PascalCase | `ApiResponse`, `UserService` |
| Files (controllers/models) | PascalCase | `UserController.js`, `User.js` |
| Files (routes/middleware/utils) | camelCase | `userRoutes.js`, `hasToken.js` |
| React components | PascalCase | `UserCard.jsx`, `LoginPage.jsx` |
| React hooks | camelCase with `use` | `useAuth.js`, `useProfile.js` |

### 1.4 Comments
**Do write:**
```javascript
// Normalize email before DB comparison (avoids case-sensitive duplicates)
const normalizedEmail = email.toLowerCase();

// Soft delete: never physically remove records per AGENT_RULES Rule 5
await User.findOneAndUpdate({ _id: id }, { $set: { isDeleted: true } });
```

**Don't write:**
```javascript
// Get the user
const user = await User.findOne({ _id: id }); // (obvious, no value)
```

**JSDoc (required on all controller methods):**
```javascript
/**
 * @name createUser
 * @file UserController.js
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @description Creates a new user account with hashed password
 */
```

---

## Section 2: Backend Standards

### 2.1 Async/Await
```javascript
// ✅ Correct — explicit try/catch
const getUser = async (req, res) => {
  try {
    const user = await User.findOne({ _id: req.params.id, isDeleted: false }).lean();
    // ...
  } catch (err) {
    return sendError(res, { statusCode: ResponseCodes.SERVER_ERROR, message: err.message });
  }
};

// ❌ Wrong — no error handling
const getUser = async (req, res) => {
  const user = await User.findOne({ _id: req.params.id }).lean();
  res.json(user);
};
```

### 2.2 Response Pattern
```javascript
// ✅ Correct
return new ApiResponse(ResponseCodes.OK, 'Success message', { user }).send(res);
return sendError(res, { statusCode: ResponseCodes.NOT_FOUND, message: 'Not found', code: ErrorCodes.NOT_FOUND });

// ❌ Forbidden
return res.json({ data: user });
return res.status(404).json({ error: 'Not found' });
res.status(200).json({ success: true }); // missing return = risk of "headers already sent"
```

**Always `return` response calls** — prevents "Cannot set headers after they are sent" errors.

### 2.3 Database Queries
```javascript
// ✅ Correct
const user = await User.findOne({ _id: id, isDeleted: false }).lean();
const users = await User.find({ isDeleted: false, role: 'user' }).lean();

// ❌ Wrong — missing isDeleted filter
const user = await User.findOne({ _id: id });
const users = await User.find({});

// ❌ Wrong — no .lean() (Mongoose document overhead)
const user = await User.findOne({ _id: id, isDeleted: false });
```

### 2.4 Destructuring from Constants
```javascript
// ✅ Correct
const { config, ResponseCodes, ErrorCodes, Roles } = require('../config/constants');

// ❌ Wrong — accessing process.env directly in controller
const secret = process.env.JWT_SECRET;
```

### 2.5 Module Exports
```javascript
// ✅ Named exports (preferred for controllers)
const getUser = async (req, res) => { /* ... */ };
const createUser = async (req, res) => { /* ... */ };
module.exports = { getUser, createUser };

// ❌ Default export for controllers (reduces explicit naming)
module.exports = { default: getUser };
```

---

## Section 3: Frontend Standards

### 3.1 Component Structure Order
```jsx
// 1. Imports
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { someAction } from '../store/slices/someSlice';
import './ComponentName.css'; // (if component-scoped CSS)

// 2. Component function
const ComponentName = ({ prop1, prop2 }) => {
  // 3. Hooks (in this order)
  const dispatch = useDispatch();
  const data = useSelector((state) => state.feature.data);
  const [localState, setLocalState] = useState(initialValue);

  // 4. Effects
  useEffect(() => {
    // side effects
    return () => { /* cleanup */ };
  }, [dependencies]);

  // 5. Event handlers
  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(someAction(data));
  };

  // 6. Derived state
  const isReady = Boolean(data && !loading);

  // 7. Early returns
  if (loading) return <div>Loading...</div>;
  if (!data) return null;

  // 8. Render
  return (
    <div className="component-name">
      {/* JSX */}
    </div>
  );
};

// 9. Default export
export default ComponentName;
```

### 3.2 Event Handlers
```jsx
// ✅ Correct — prevent default, no inline functions in JSX
<form onSubmit={handleSubmit}>

// ❌ Wrong — inline function (creates new reference every render)
<button onClick={() => dispatch(someAction())}>

// ✅ Better — extracted handler
const handleClick = () => dispatch(someAction());
<button onClick={handleClick}>
```

### 3.3 State Management Rules
```javascript
// ✅ Server data → Redux
const { user } = useSelector((state) => state.user);

// ✅ Local UI state → useState
const [isOpen, setIsOpen] = useState(false);
const [formData, setFormData] = useState({ name: '', email: '' });

// ❌ Wrong — server data in local state
const [user, setUser] = useState(null);
useEffect(() => { fetchUser().then(setUser); }, []);
```

### 3.4 CSS Standards
```css
/* Use BEM-inspired naming */
.user-card { }
.user-card__title { }
.user-card__actions { }
.user-card--highlighted { }

/* CSS custom properties for theming */
:root {
  --color-primary: #2563eb;
  --color-error: #dc2626;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --border-radius: 8px;
}
```

---

## Section 4: Error Handling Standards

### 4.1 Error Classification
```javascript
// 4xx — Client errors (user can fix)
400 → Bad request (malformed data)
401 → Unauthorized (no/invalid token)
403 → Forbidden (valid token, wrong role)
404 → Not found
409 → Conflict (duplicate resource)
422 → Unprocessable (validation failed)

// 5xx — Server errors (we need to fix)
500 → Internal server error (unhandled exception)
```

### 4.2 Error Response Format
```json
{
  "success": false,
  "message": "Human-readable error description",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": [
      { "field": "email", "message": "Must be a valid email" }
    ]
  }
}
```

### 4.3 Frontend Error Handling
```javascript
// In thunk — map to user-friendly message
return rejectWithValue(err.response?.data?.message || 'Something went wrong');

// In component — show error to user, provide retry
if (error) return (
  <div className="error-message">
    <p>{error}</p>
    <button onClick={() => dispatch(clearError())}>Dismiss</button>
  </div>
);
```

---

## Section 5: Code Review Checklist

### Pre-Delivery Checklist
- [ ] All file names follow naming conventions
- [ ] All controller methods have JSDoc
- [ ] All async functions have try/catch
- [ ] All responses use ApiResponse or sendError (never raw res.json)
- [ ] All database queries include `{ isDeleted: false }` and `.lean()`
- [ ] No `process.env.X` outside `constants.js`
- [ ] No hardcoded status codes (use ResponseCodes)
- [ ] No hardcoded error strings (use ErrorCodes)
- [ ] No debug logs (`console.log` without `// [DEBUG]` prefix)
- [ ] Redux slices have `loading`, `error`, `clearError`
- [ ] All API calls go through `axiosInstance`
- [ ] No inline API calls in React components
- [ ] CSS uses CSS custom properties for colors/spacing
