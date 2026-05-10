# EXAMPLES.md — Reference Implementation Examples

## Purpose
Working, tested code examples for the most common patterns in this system. Use these as copy-paste starting points, not as learning material — always adapt them to the specific task.

---

## Example 1: Complete Backend Feature (User Preferences API)

### Feature Spec
- GET /api/preferences → Get current user's preferences
- PATCH /api/preferences → Update preferences
- Auth: User required

### constants.js additions
```javascript
// Add to ErrorCodes
PREFERENCES_NOT_FOUND: 'PREFERENCES_NOT_FOUND',
```

### Model: Preferences.js
```javascript
'use strict';

const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const preferencesSchema = new mongoose.Schema(
  {
    _id: { type: String, default: uuidv4 },
    userId: { type: String, required: true, ref: 'User' },
    theme: { type: String, enum: ['light', 'dark', 'system'], default: 'system' },
    emailNotifications: { type: Boolean, default: true },
    language: { type: String, default: 'en' },
    isDeleted: { type: Boolean, default: false },
  },
  {
    timestamps: true,
    _id: false,
    toJSON: {
      transform(doc, ret) {
        delete ret.__v;
        return ret;
      },
    },
  }
);

preferencesSchema.index({ userId: 1 }, { unique: true });

const Preferences = mongoose.model('Preferences', preferencesSchema);
module.exports = Preferences;
```

### Validator: preferencesValidator.js
```javascript
'use strict';

const { body } = require('express-validator');
const { validateRequest } = require('../middlewares/validateRequest');

const updatePreferencesRules = [
  body('theme')
    .optional()
    .trim()
    .isIn(['light', 'dark', 'system'])
    .withMessage('Theme must be light, dark, or system'),
  body('emailNotifications')
    .optional()
    .isBoolean()
    .toBoolean()
    .withMessage('emailNotifications must be a boolean'),
  body('language')
    .optional()
    .trim()
    .isLength({ min: 2, max: 5 })
    .withMessage('Language must be a valid locale code'),
  validateRequest,
];

module.exports = { updatePreferencesRules };
```

### Controller: PreferencesController.js
```javascript
'use strict';

const { ResponseCodes, ErrorCodes } = require('../config/constants');
const { ApiResponse, sendError } = require('../utils/apiResponse');
const Preferences = require('../models/Preferences');

/**
 * @name getPreferences
 * @file PreferencesController.js
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @description Retrieves the authenticated user's preferences
 */
const getPreferences = async (req, res) => {
  try {
    let preferences = await Preferences.findOne({
      userId: req.user.id,
      isDeleted: false,
    }).lean();

    // Auto-create default preferences if none exist
    if (!preferences) {
      preferences = await Preferences.create({ userId: req.user.id });
      preferences = preferences.toJSON();
    }

    return new ApiResponse(ResponseCodes.OK, 'Preferences retrieved', { preferences }).send(res);
  } catch (err) {
    return sendError(res, {
      statusCode: ResponseCodes.SERVER_ERROR,
      message: err.message,
      code: ErrorCodes.SERVER_ERROR,
    });
  }
};

/**
 * @name updatePreferences
 * @file PreferencesController.js
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @description Updates the authenticated user's preferences
 */
const updatePreferences = async (req, res) => {
  try {
    const allowedUpdates = {};
    if (req.body.theme !== undefined) allowedUpdates.theme = req.body.theme;
    if (req.body.emailNotifications !== undefined) allowedUpdates.emailNotifications = req.body.emailNotifications;
    if (req.body.language !== undefined) allowedUpdates.language = req.body.language;

    const updated = await Preferences.findOneAndUpdate(
      { userId: req.user.id, isDeleted: false },
      { $set: allowedUpdates },
      { new: true, upsert: true } // Create if not exists
    ).lean();

    return new ApiResponse(ResponseCodes.OK, 'Preferences updated', { preferences: updated }).send(res);
  } catch (err) {
    return sendError(res, {
      statusCode: ResponseCodes.SERVER_ERROR,
      message: err.message,
      code: ErrorCodes.SERVER_ERROR,
    });
  }
};

module.exports = { getPreferences, updatePreferences };
```

### Route: preferencesRoutes.js
```javascript
'use strict';

const { Router } = require('express');
const { getPreferences, updatePreferences } = require('../controllers/PreferencesController');
const { hasToken } = require('../middlewares/hasToken');
const { isAuthenticated } = require('../middlewares/isAuthenticated');
const { isUser } = require('../middlewares/isUser');
const { updatePreferencesRules } = require('../validators/preferencesValidator');

const router = Router();

router.get('/', hasToken, isAuthenticated, isUser, getPreferences);
router.patch('/', hasToken, isAuthenticated, isUser, updatePreferencesRules, updatePreferences);

module.exports = router;
```

---

## Example 2: Complete Frontend Feature (Preferences Slice + Component)

### API: preferencesApi.js
```javascript
import axiosInstance from './axiosInstance';

export const fetchPreferencesApi = () =>
  axiosInstance.get('/api/preferences');

export const updatePreferencesApi = (data) =>
  axiosInstance.patch('/api/preferences', data);
```

### Slice: preferencesSlice.js
```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchPreferencesApi, updatePreferencesApi } from '../../api/preferencesApi';

export const fetchPreferences = createAsyncThunk(
  'preferences/fetch',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await fetchPreferencesApi();
      return data.data.preferences;
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Failed to load preferences');
    }
  }
);

export const updatePreferences = createAsyncThunk(
  'preferences/update',
  async (updates, { rejectWithValue }) => {
    try {
      const { data } = await updatePreferencesApi(updates);
      return data.data.preferences;
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Failed to update preferences');
    }
  }
);

const preferencesSlice = createSlice({
  name: 'preferences',
  initialState: {
    preferences: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => { state.error = null; },
  },
  extraReducers: (builder) => {
    const handlePending = (state) => { state.loading = true; state.error = null; };
    const handleFulfilled = (state, action) => { state.loading = false; state.preferences = action.payload; };
    const handleRejected = (state, action) => { state.loading = false; state.error = action.payload; };

    builder
      .addCase(fetchPreferences.pending, handlePending)
      .addCase(fetchPreferences.fulfilled, handleFulfilled)
      .addCase(fetchPreferences.rejected, handleRejected)
      .addCase(updatePreferences.pending, handlePending)
      .addCase(updatePreferences.fulfilled, handleFulfilled)
      .addCase(updatePreferences.rejected, handleRejected);
  },
});

export const { clearError } = preferencesSlice.actions;
export default preferencesSlice.reducer;
```

### Hook: usePreferences.js
```javascript
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchPreferences, updatePreferences, clearError } from '../store/slices/preferencesSlice';

const usePreferences = () => {
  const dispatch = useDispatch();
  const { preferences, loading, error } = useSelector((state) => state.preferences);

  useEffect(() => {
    dispatch(fetchPreferences());
    return () => { dispatch(clearError()); };
  }, [dispatch]);

  const handleUpdate = (updates) => dispatch(updatePreferences(updates));

  return { preferences, loading, error, handleUpdate };
};

export default usePreferences;
```

---

## Example 3: Pagination Pattern

### Backend Pagination
```javascript
const getPaginatedUsers = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = Math.min(parseInt(req.query.limit) || 20, 100); // Cap at 100
    const skip = (page - 1) * limit;

    const [users, totalCount] = await Promise.all([
      User.find({ isDeleted: false, role: Roles.USER })
        .select('name email role createdAt')
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .lean(),
      User.countDocuments({ isDeleted: false, role: Roles.USER }),
    ]);

    return new ApiResponse(ResponseCodes.OK, 'Users retrieved', {
      items: users,
      totalCount,
      page,
      limit,
      totalPages: Math.ceil(totalCount / limit),
    }).send(res);
  } catch (err) {
    return sendError(res, {
      statusCode: ResponseCodes.SERVER_ERROR,
      message: err.message,
      code: ErrorCodes.SERVER_ERROR,
    });
  }
};
```
