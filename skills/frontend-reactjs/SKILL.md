---
name: frontend-reactjs
description: >
  Use this skill whenever the user asks to scaffold, design, build, or review the React frontend of
  a MERN stack application. Triggers include: "set up the frontend", "create the frontend folder
  structure", "create a React component", "set up Redux Toolkit", "add a Redux slice", "create an
  API helper", "set up React Router", "create a custom hook", "set up Axios", "build a page
  component", "add global state", or any request to generate React / frontend code. Also trigger
  when the user shares existing frontend code and asks for a review, refactor, or
  production-readiness check. Always use this skill even if the user only asks about one part
  (e.g. just a slice or just a hook) — the standards here apply to every layer of the frontend.
---

# MERN Frontend Skill

Production-grade rulebook for the React frontend.
Covers folder structure, Redux Toolkit state management, API layer, routing, hooks, and component conventions.

---

## 1. Folder Structure

The frontend lives at `project-name/frontend/`.

```
project-name/
└── frontend/
    ├── public/
    ├── src/
    │   ├── api/                      # Axios instance + per-resource API functions
    │   │   ├── axiosInstance.js      # Single configured Axios instance (base URL, interceptors)
    │   │   └── userApi.js            # All API calls for the user resource
    │   ├── assets/                   # Images, fonts, icons, static files
    │   ├── components/               # Reusable UI — PascalCase filenames
    │   │   └── UserCard.jsx
    │   ├── hooks/                    # Custom hooks — camelCase prefixed with "use"
    │   │   ├── useAuth.js
    │   │   └── useFetch.js
    │   ├── pages/                    # Route-level page components — PascalCase
    │   │   ├── LoginPage.jsx
    │   │   └── DashboardPage.jsx
    │   ├── routes/                   # React Router config
    │   │   └── AppRoutes.jsx
    │   ├── store/                    # Redux Toolkit — all global state
    │   │   ├── index.js              # configureStore — imports all slices
    │   │   └── slices/               # One slice per feature
    │   │       ├── userSlice.js
    │   │       └── authSlice.js
    │   ├── utils/                    # Frontend helpers (formatDate, truncate, etc.)
    │   │   └── formatters.js
    │   ├── App.jsx
    │   └── main.jsx                  # Entry point — wraps app in <Provider>
    ├── .env
    ├── .env.example
    └── package.json
```

---

## 2. Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Component files | PascalCase | `UserCard.jsx`, `LoginPage.jsx` |
| Page files | PascalCase + "Page" suffix | `DashboardPage.jsx` |
| Hook files | camelCase + "use" prefix | `useAuth.js`, `useFetch.js` |
| Slice files | camelCase + "Slice" suffix | `userSlice.js`, `authSlice.js` |
| API files | camelCase + "Api" suffix | `userApi.js`, `authApi.js` |
| Util files | camelCase | `formatters.js`, `validators.js` |
| Route config | PascalCase | `AppRoutes.jsx` |
| Variables / functions | camelCase | `fetchUser`, `handleSubmit` |
| Constants | UPPER_SNAKE_CASE | `API_BASE_URL` |
| Env vars | UPPER_SNAKE_CASE with VITE_ prefix | `VITE_API_BASE_URL` |

> **Hard rule: Never use `.` in a filename except for the extension.** `user.slice.js` ✗ → `userSlice.js` ✓

---

## 3. Environment Variables

All env vars are prefixed with `VITE_` and accessed only through a single constants file — never `import.meta.env.X` scattered throughout the codebase.

```js
// src/utils/constants.js
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
```

```
# .env
VITE_API_BASE_URL=http://localhost:5000
```

---

## 4. Axios Instance & API Layer

### `src/api/axiosInstance.js` — single shared instance
```js
import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token on every request
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Global response error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

### `src/api/userApi.js` — per-resource API functions
```js
import axiosInstance from './axiosInstance';

export const fetchUserApi     = (id)   => axiosInstance.get(`/api/users/${id}`);
export const fetchAllUsersApi = ()     => axiosInstance.get('/api/users');
export const createUserApi    = (data) => axiosInstance.post('/api/users', data);
export const updateUserApi    = (id, data) => axiosInstance.patch(`/api/users/${id}`, data);
export const deleteUserApi    = (id)   => axiosInstance.delete(`/api/users/${id}`);
```

**Rules:**
- All API functions are named with the resource + action + "Api" suffix — e.g. `fetchUserApi`, `createUserApi`
- No raw `axios.get(...)` anywhere outside `api/` — always use `axiosInstance`
- One file per backend resource — `userApi.js`, `authApi.js`, `orderApi.js`

---

## 5. Redux Toolkit — Global State

All global state uses **Redux Toolkit**. Context API is not used for global state.

### `src/store/index.js` — store setup
```js
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './slices/userSlice';
import authReducer from './slices/authSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    auth: authReducer,
  },
});
```

### Slice pattern — `src/store/slices/userSlice.js`
```js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchUserApi, fetchAllUsersApi } from '../../api/userApi';

// ─── Async thunks ─────────────────────────────────────────────────────────────
export const fetchUser = createAsyncThunk('user/fetchUser', async (id, { rejectWithValue }) => {
  try {
    const { data } = await fetchUserApi(id);
    return data.data.user;
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to fetch user');
  }
});

export const fetchAllUsers = createAsyncThunk('user/fetchAllUsers', async (_, { rejectWithValue }) => {
  try {
    const { data } = await fetchAllUsersApi();
    return data.data;            // { users: [], totalCount: N }
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to fetch users');
  }
});

// ─── Slice ────────────────────────────────────────────────────────────────────
const userSlice = createSlice({
  name: 'user',
  initialState: {
    currentUser: null,
    users: [],
    totalCount: 0,
    loading: false,
    error: null,
  },
  reducers: {
    clearUser:  (state) => { state.currentUser = null; },
    clearError: (state) => { state.error = null; },
  },
  extraReducers: (builder) => {
    builder
      // fetchUser
      .addCase(fetchUser.pending,   (state) => { state.loading = true; state.error = null; })
      .addCase(fetchUser.fulfilled, (state, action) => { state.loading = false; state.currentUser = action.payload; })
      .addCase(fetchUser.rejected,  (state, action) => { state.loading = false; state.error = action.payload; })
      // fetchAllUsers
      .addCase(fetchAllUsers.pending,   (state) => { state.loading = true; state.error = null; })
      .addCase(fetchAllUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload.users;
        state.totalCount = action.payload.totalCount;
      })
      .addCase(fetchAllUsers.rejected, (state, action) => { state.loading = false; state.error = action.payload; });
  },
});

export const { clearUser, clearError } = userSlice.actions;
export default userSlice.reducer;
```

**Redux rules:**
- One slice per feature — `userSlice.js`, `authSlice.js`, `orderSlice.js`
- Async API calls always via `createAsyncThunk` — never fetch/axios inside a reducer
- `rejectWithValue` always used in the catch block to pass clean error messages
- Slice `initialState` always has: `loading`, `error`, and the feature's data fields
- `clearError` action always included in every slice

---

## 6. Auth Slice

```js
// src/store/slices/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { loginApi, logoutApi } from '../../api/authApi';

export const login = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const { data } = await loginApi(credentials);
    localStorage.setItem('accessToken', data.data.accessToken);
    return data.data.user;
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Login failed');
  }
});

export const logout = createAsyncThunk('auth/logout', async (_, { rejectWithValue }) => {
  try {
    await logoutApi();
    localStorage.removeItem('accessToken');
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Logout failed');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, loading: false, error: null },
  reducers: {
    clearAuthError: (state) => { state.error = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending,   (state) => { state.loading = true; state.error = null; })
      .addCase(login.fulfilled, (state, action) => { state.loading = false; state.user = action.payload; })
      .addCase(login.rejected,  (state, action) => { state.loading = false; state.error = action.payload; })
      .addCase(logout.fulfilled, (state) => { state.user = null; });
  },
});

export const { clearAuthError } = authSlice.actions;
export default authSlice.reducer;
```

---

## 7. Custom Hooks

Hooks encapsulate repeated logic — always prefixed with `use`.

```js
// src/hooks/useAuth.js
import { useSelector, useDispatch } from 'react-redux';
import { login, logout, clearAuthError } from '../store/slices/authSlice';

const useAuth = () => {
  const dispatch = useDispatch();
  const { user, loading, error } = useSelector((state) => state.auth);

  return {
    user,
    loading,
    error,
    isLoggedIn: !!user,
    login:      (credentials) => dispatch(login(credentials)),
    logout:     ()            => dispatch(logout()),
    clearError: ()            => dispatch(clearAuthError()),
  };
};

export default useAuth;
```

**Hook rules:**
- One hook per domain — `useAuth.js`, `useUser.js`, `useOrders.js`
- Hooks never directly call `axiosInstance` — they always dispatch thunks from the store
- Hooks return derived state (e.g. `isLoggedIn`) alongside raw state where useful

---

## 8. React Router Setup

```jsx
// src/routes/AppRoutes.jsx
import { Routes, Route, Navigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import LoginPage    from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';

const ProtectedRoute = ({ children }) => {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? children : <Navigate to="/login" replace />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/login" replace />} />
  </Routes>
);

export default AppRoutes;
```

---

## 9. Entry Point

```jsx
// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from './store';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);
```

```jsx
// src/App.jsx
import AppRoutes from './routes/AppRoutes';

const App = () => <AppRoutes />;

export default App;
```

---

## 10. Component Conventions

```jsx
// src/components/UserCard.jsx
import { useDispatch } from 'react-redux';
import { fetchUser } from '../store/slices/userSlice';

const UserCard = ({ userId }) => {
  const dispatch = useDispatch();

  const handleView = () => dispatch(fetchUser(userId));

  return (
    <div className="user-card">
      <button onClick={handleView}>View</button>
    </div>
  );
};

export default UserCard;
```

**Component rules:**
- PascalCase filename and component name — always match
- Default export per file — one component per file
- No inline API calls — always dispatch a thunk or use a custom hook
- No direct `useState` for server data — use Redux slice state
- Local `useState` is fine for UI-only state (modal open, form input, toggle)
- Never use `<form>` with `action` — use `onSubmit` with `e.preventDefault()`

---

## 11. Production Checklist

### Naming & Structure
- [ ] Component and page filenames are PascalCase
- [ ] Pages have "Page" suffix — `DashboardPage.jsx`
- [ ] Hook filenames are camelCase with "use" prefix — `useAuth.js`
- [ ] Slice filenames are camelCase with "Slice" suffix — `userSlice.js`
- [ ] API filenames are camelCase with "Api" suffix — `userApi.js`
- [ ] No dots in filenames except the extension

### State Management
- [ ] Redux Toolkit used for all global state — no Context API for global data
- [ ] One slice per feature in `store/slices/`
- [ ] Every slice has `loading`, `error`, and `clearError` action
- [ ] All async API calls via `createAsyncThunk` with `rejectWithValue` in catch
- [ ] `store/index.js` is the single place all reducers are combined

### API Layer
- [ ] All API calls go through `axiosInstance` — no raw `axios` in components or hooks
- [ ] One `*Api.js` file per backend resource
- [ ] Request interceptor attaches `Authorization: Bearer <token>` header
- [ ] Response interceptor handles 401 (redirect to login, clear token)

### Routing
- [ ] `ProtectedRoute` wrapper used for all authenticated routes
- [ ] Unauthenticated users redirected to `/login`
- [ ] Catch-all `*` route redirects to a sensible default

### Components
- [ ] No inline API calls in components — always dispatch thunks or use hooks
- [ ] `useState` only for local UI state — never for server data
- [ ] All forms use `onSubmit` + `e.preventDefault()` — never native `<form action>`
- [ ] One component per file, default export

### Environment
- [ ] All env vars prefixed with `VITE_`
- [ ] `import.meta.env.X` only accessed in `src/utils/constants.js`
- [ ] `.env.example` kept up to date with all required vars
