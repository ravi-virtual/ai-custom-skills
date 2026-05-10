# VALIDATION.md — Validation Standards & Patterns

## Purpose
Defines the validation strategy at every layer of the stack — input validation, business rule validation, data integrity validation, and output validation.

---

## Validation Layers

```
Layer 1: Frontend (Client-side)   — Immediate feedback before API call
Layer 2: Express Validator (API)  — Authoritative validation on server
Layer 3: Mongoose Schema          — Database-level type enforcement
Layer 4: Business Logic           — Domain rule enforcement in controllers
Layer 5: Output Validation        — Ensure API responses match expected shape
```

---

## Layer 1: Frontend Validation

### Rules
- Frontend validation is for UX only — it is NOT a security control
- Every field validated server-side must also be validated frontend
- Never assume frontend validation passed — always validate server-side too

### React Form Validation Pattern
```javascript
// useFormValidation.js — reusable validation hook
import { useState } from 'react';

const useFormValidation = (rules) => {
  const [errors, setErrors] = useState({});

  const validate = (data) => {
    const newErrors = {};

    Object.entries(rules).forEach(([field, fieldRules]) => {
      const value = data[field];

      if (fieldRules.required && (!value || value.toString().trim() === '')) {
        newErrors[field] = `${field} is required`;
        return;
      }
      if (fieldRules.minLength && value?.length < fieldRules.minLength) {
        newErrors[field] = `Minimum ${fieldRules.minLength} characters`;
        return;
      }
      if (fieldRules.maxLength && value?.length > fieldRules.maxLength) {
        newErrors[field] = `Maximum ${fieldRules.maxLength} characters`;
        return;
      }
      if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
        newErrors[field] = fieldRules.message || 'Invalid format';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  return { errors, validate, setErrors };
};

// Usage:
const { errors, validate } = useFormValidation({
  email: { required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email' },
  password: { required: true, minLength: 8 },
  name: { required: true, minLength: 2, maxLength: 100 },
});
```

---

## Layer 2: Express Validator (Authoritative)

### Standard Validator Patterns

```javascript
// Common reusable rules — add to a shared validators/common.js

const emailRule = () =>
  body('email')
    .trim()
    .toLowerCase()
    .notEmpty().withMessage('Email is required')
    .isEmail().withMessage('Must be a valid email address');

const passwordRule = (field = 'password') =>
  body(field)
    .notEmpty().withMessage('Password is required')
    .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
    .matches(/[A-Z]/).withMessage('Password must contain at least one uppercase letter')
    .matches(/[0-9]/).withMessage('Password must contain at least one number');

const uuidRule = (field) =>
  param(field)
    .notEmpty().withMessage(`${field} is required`)
    .isUUID(4).withMessage(`${field} must be a valid UUID`);

const booleanRule = (field) =>
  body(field)
    .notEmpty().withMessage(`${field} is required`)
    .isBoolean().withMessage(`${field} must be true or false`)
    .toBoolean();  // ← CRITICAL: converts "true"/"false" strings to Boolean

const positiveIntRule = (field) =>
  query(field)
    .optional()
    .isInt({ min: 1 }).withMessage(`${field} must be a positive integer`)
    .toInt();

const paginationRules = [
  query('page').optional().isInt({ min: 1 }).toInt(),
  query('limit').optional().isInt({ min: 1, max: 100 }).toInt(),
];
```

### validateRequest Middleware
```javascript
// middleware/validateRequest.js
'use strict';

const { validationResult } = require('express-validator');
const { sendError } = require('../utils/apiResponse');
const { ResponseCodes, ErrorCodes } = require('../config/constants');

/**
 * @name validateRequest
 * @file validateRequest.js
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 * @description Checks express-validator results and rejects invalid requests
 */
const validateRequest = (req, res, next) => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    return sendError(res, {
      statusCode: ResponseCodes.UNPROCESSABLE,
      message: 'Validation failed',
      code: ErrorCodes.VALIDATION_ERROR,
      details: errors.array().map((err) => ({
        field: err.path,
        message: err.msg,
      })),
    });
  }

  next();
};

module.exports = { validateRequest };
```

---

## Layer 3: Mongoose Schema Validation

### Schema-Level Constraints
```javascript
const userSchema = new mongoose.Schema({
  _id: { type: String, default: uuidv4 },
  
  name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true,
    minlength: [2, 'Name must be at least 2 characters'],
    maxlength: [100, 'Name cannot exceed 100 characters'],
  },
  
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,   // Auto-lowercase before saving
    trim: true,
    match: [/^[^\s@]+@[^\s@]+\.[^\s@]+$/, 'Invalid email format'],
  },
  
  role: {
    type: String,
    enum: {
      values: ['admin', 'user'],
      message: '{VALUE} is not a valid role',
    },
    default: 'user',
  },
  
  rating: {
    type: Boolean,     // Never accept string "true" — Mongoose enforces type
  },
  
  isDeleted: { type: Boolean, default: false },
}, { timestamps: true, _id: false });
```

---

## Layer 4: Business Rule Validation

### Ownership Validation (Authorization)
```javascript
// In controller — verify user owns the resource
const profile = await Profile.findOne({ _id: req.params.id, isDeleted: false }).lean();

if (!profile) {
  return sendError(res, {
    statusCode: ResponseCodes.NOT_FOUND,
    message: 'Profile not found',
    code: ErrorCodes.NOT_FOUND,
  });
}

// Check ownership — only owner or admin can modify
if (profile.userId !== req.user.id && req.user.role !== 'admin') {
  return sendError(res, {
    statusCode: ResponseCodes.FORBIDDEN,
    message: 'You do not have permission to modify this profile',
    code: ErrorCodes.FORBIDDEN,
  });
}
```

### Business Rule Examples
```javascript
// Rule: User cannot have more than 5 active profiles
const profileCount = await Profile.countDocuments({
  userId: req.user.id,
  isDeleted: false,
});

if (profileCount >= 5) {
  return sendError(res, {
    statusCode: ResponseCodes.UNPROCESSABLE,
    message: 'Maximum of 5 profiles allowed per account',
    code: ErrorCodes.LIMIT_EXCEEDED,
  });
}

// Rule: Cannot rate the same generation twice
const existingFeedback = await Feedback.findOne({
  generationId: req.body.generationId,
  userId: req.user.id,
  isDeleted: false,
});

if (existingFeedback) {
  return sendError(res, {
    statusCode: ResponseCodes.CONFLICT,
    message: 'You have already rated this generation',
    code: ErrorCodes.DUPLICATE_ERROR,
  });
}
```

---

## Layer 5: Output Validation

### Response Shape Validation (Development Only)
```javascript
// Validate your own API response shapes during development
const validateResponseShape = (data, expectedShape) => {
  const missing = Object.keys(expectedShape).filter(key => !(key in data));
  if (missing.length > 0) {
    console.warn(`// [DEBUG] Response missing fields: ${missing.join(', ')}`);
  }
};

// Usage in dev:
validateResponseShape(responseData, { user: null, accessToken: null, expiresIn: null });
```

---

## Validation Rules Reference

| Field Type | Required Rules |
|---|---|
| Email | `.isEmail().toLowerCase().trim()` |
| Password (new) | `.isLength({ min: 8 }).matches(/[A-Z]/).matches(/[0-9]/)` |
| UUID path param | `param('id').isUUID(4)` |
| Boolean | `.isBoolean().toBoolean()` |
| Integer | `.isInt({ min: X, max: Y }).toInt()` |
| Enum string | `.isIn(['value1', 'value2'])` |
| Optional field | `.optional()` before all other rules |
| Trim whitespace | `.trim()` on all string inputs |

---

## Validation Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| Trusting frontend validation | Always validate server-side |
| Using `!req.body.field` for existence check | Use `body('field').notEmpty()` |
| Sending Boolean schema with string "true" | Use `.toBoolean()` in validator |
| Custom regex for email | Use `.isEmail()` — it handles edge cases |
| Not sanitizing input | Use `.trim()` + `.escape()` for HTML |
| Skipping validateRequest at end of array | It's mandatory — never skip it |
