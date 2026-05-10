# FRONTEND.md — Frontend Engineering Reference

## Frontend Stack
- Framework: React 18.x
- Build Tool: Vite 5.x
- State: Redux Toolkit 2.x
- Routing: React Router 6.x
- HTTP: Axios 1.x
- Styling: Vanilla CSS

---

## Project Structure
```
frontend/
└── src/
    ├── api/
    │   ├── axiosInstance.js      ← Base configured Axios instance
    │   └── [resource]Api.js     ← Resource-specific API functions
    ├── assets/                   ← Static assets (images, fonts)
    ├── components/               ← Reusable UI components (PascalCase)
    ├── hooks/                    ← Custom hooks (camelCase, use prefix)
    ├── pages/                    ← Page-level components (PascalCase + Page)
    ├── routes/
    │   └── AppRoutes.jsx        ← Router + ProtectedRoute
    ├── store/
    │   ├── index.js             ← configureStore
    │   └── slices/              ← Feature slices (camelCase + Slice)
    ├── styles/
    │   └── index.css            ← Global styles
    └── utils/
        └── constants.js         ← ONLY place for import.meta.env access
```

---

## Axios Instance
```javascript
// src/api/axiosInstance.js
import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';
import store from '../store';
import { clearAuth } from '../store/slices/authSlice';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      try {
        const { data } = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {}, { withCredentials: true });
        const newToken = data.data.accessToken;
        localStorage.setItem('accessToken', newToken);
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axiosInstance.request(error.config);
      } catch {
        localStorage.removeItem('accessToken');
        store.dispatch(clearAuth());
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

---

## API Function Pattern
```javascript
// src/api/userApi.js
import axiosInstance from './axiosInstance';

export const fetchUserApi = (userId) =>
  axiosInstance.get(`/api/users/${userId}`);

export const updateUserApi = (userId, data) =>
  axiosInstance.patch(`/api/users/${userId}`, data);

export const deleteUserApi = (userId) =>
  axiosInstance.delete(`/api/users/${userId}`);
```

---

## Redux Toolkit Slice Pattern
```javascript
// src/store/slices/userSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchUserApi, updateUserApi } from '../../api/userApi';

// Async thunks
export const fetchUser = createAsyncThunk(
  'user/fetchUser',
  async (userId, { rejectWithValue }) => {
    try {
      const { data } = await fetchUserApi(userId);
      return data.data.user;
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Failed to fetch user');
    }
  }
);

export const updateUser = createAsyncThunk(
  'user/updateUser',
  async ({ userId, userData }, { rejectWithValue }) => {
    try {
      const { data } = await updateUserApi(userId, userData);
      return data.data.user;
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || 'Failed to update user');
    }
  }
);

// Slice
const userSlice = createSlice({
  name: 'user',
  initialState: {
    user: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => { state.error = null; },
    clearUser: (state) => { state.user = null; },
  },
  extraReducers: (builder) => {
    // fetchUser
    builder
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
    // updateUser
    builder
      .addCase(updateUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(updateUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError, clearUser } = userSlice.actions;
export default userSlice.reducer;
```

---

## Redux Store Setup
```javascript
// src/store/index.js
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    // Add more slices here as features grow
  },
});

export default store;
```

---

## React Component Pattern
```jsx
// src/components/UserCard.jsx
import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { clearError } from '../store/slices/userSlice';

const UserCard = ({ userId }) => {
  const dispatch = useDispatch();
  const { user, loading, error } = useSelector((state) => state.user);

  // Local UI state only (modal, toggle, etc.)
  const [isEditing, setIsEditing] = React.useState(false);

  React.useEffect(() => {
    return () => { dispatch(clearError()); };  // Cleanup on unmount
  }, [dispatch]);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!user) return null;

  return (
    <div className="user-card">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      {/* ... */}
    </div>
  );
};

export default UserCard;
```

---

## Custom Hook Pattern
```javascript
// src/hooks/useUser.js
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUser, clearError } from '../store/slices/userSlice';

const useUser = (userId) => {
  const dispatch = useDispatch();
  const { user, loading, error } = useSelector((state) => state.user);

  useEffect(() => {
    if (userId) dispatch(fetchUser(userId));
    return () => { dispatch(clearError()); };
  }, [userId, dispatch]);

  return { user, loading, error };
};

export default useUser;
```

---

## React Router Setup
```jsx
// src/routes/AppRoutes.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes>
);

export default AppRoutes;
```

---

## Frontend Constants
```javascript
// src/utils/constants.js
// ONLY place in the frontend that accesses import.meta.env

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// Add other env vars and app-level constants here
export const APP_NAME = 'My Application';
```

---

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|---|---|---|
| `axios.get(url)` in component | Bypasses interceptors, untracked | Use `axiosInstance` via API file |
| `useState` for server data | Duplicates Redux state, stale | Use Redux slice via selector |
| API call in `useEffect` directly | Untracked, no loading state | Dispatch thunk in hook |
| `res.json()` in Backend | Bypasses format enforcement | Use `ApiResponse` / `sendError` |
| Multiple slices for one feature | Fragment state, hard to reason | One slice per feature |
| Context API for global data | Prop drilling, no DevTools | Redux Toolkit |
| Inline styles in JSX | Unmaintainable, no theming | CSS classes |
