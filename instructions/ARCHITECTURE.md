# ARCHITECTURE.md — System Architecture Reference

## System Overview
This document is the canonical reference for system architecture. All agents must consult this file before making structural decisions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│   React App (Vite)                                               │
│   ├── Redux Store (RTK)         ← Global state                  │
│   ├── React Router              ← Navigation                    │
│   ├── Axios Instance            ← HTTP with auth interceptors   │
│   └── Components / Pages        ← UI layer                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/HTTPS
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                 │
│   Express.js Application                                         │
│   ├── CORS + Helmet              ← Security headers              │
│   ├── Rate Limiter               ← DDoS protection              │
│   ├── Auth Middleware            ← JWT verification             │
│   ├── Route Handlers             ← Request routing              │
│   ├── Validators                 ← Input validation             │
│   └── Controllers                ← Business logic               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│   MongoDB (via Mongoose)                                         │
│   ├── User Collection            ← UUID _id, soft delete        │
│   ├── [Other Collections]        ← Same pattern                 │
│   └── Indexes                    ← Defined on schema fields     │
└─────────────────────────────────────────────────────────────────┘
```

## Backend Architecture (Express/Node.js)

### Request Lifecycle
```
HTTP Request
    ↓
CORS Middleware (allow cross-origin requests)
    ↓
Helmet (set security headers)
    ↓
Rate Limiter (reject if exceeded)
    ↓
Body Parser (parse JSON body)
    ↓
Morgan (log request)
    ↓
Router (/api prefix)
    ↓
hasToken (extract + verify JWT → set req.user)
    ↓
isAuthenticated (verify req.user.isAuthenticated === true)
    ↓
[isAdmin | isUser] (role-based access control)
    ↓
Validator (validate request body/params/query)
    ↓
Controller (business logic → DB → response)
    ↓
HTTP Response
```

### Error Flow
```
Any layer throws error
    ↓
Global Error Handler (4-arg Express handler, last middleware)
    ↓
Map to appropriate HTTP status + error code
    ↓
sendError() → JSON error response
```

### Folder Architecture
```
backend/
└── src/
    ├── config/
    │   └── constants.js          ← Single source of truth for all config
    ├── controllers/               ← Business logic, PascalCase
    ├── middlewares/               ← Auth, rate limiting, error handling
    ├── models/                    ← Mongoose schemas, PascalCase, UUID _id
    ├── routes/                    ← Route definitions only, camelCase
    ├── validators/                ← express-validator rule sets
    ├── utils/
    │   └── apiResponse.js        ← ApiResponse + sendError utilities
    └── app.js                     ← Express app setup
```

## Frontend Architecture (React/Redux)

### Data Flow
```
User Interaction (click, form submit)
    ↓
Component dispatches Redux action or thunk
    ↓
Redux Thunk calls API function (from api/ folder)
    ↓
Axios Instance (attaches auth header, handles 401)
    ↓
Express API → returns JSON
    ↓
Redux state updated (loading → success/error)
    ↓
Component re-renders with new state
    ↓
User sees updated UI
```

### Folder Architecture
```
frontend/
└── src/
    ├── api/
    │   ├── axiosInstance.js      ← Configured Axios with interceptors
    │   └── [resource]Api.js      ← Per-resource API functions
    ├── components/                ← Reusable UI, PascalCase
    ├── pages/                     ← Route-level pages, PascalCase + Page suffix
    ├── hooks/                     ← Custom hooks, camelCase + use prefix
    ├── routes/
    │   └── AppRoutes.jsx          ← React Router config + ProtectedRoute
    ├── store/
    │   ├── index.js               ← configureStore
    │   └── slices/                ← One slice per feature
    └── utils/
        └── constants.js           ← VITE_ env vars (only place accessed)
```

## Authentication Architecture

### Token System
```
Login → Server generates:
  accessToken:  JWT, expires: 15 minutes
  refreshToken: JWT, expires: 7 days

Client stores:
  accessToken:  localStorage (or memory)
  refreshToken: httpOnly cookie (preferred) or secure storage

On API call:
  Authorization: Bearer <accessToken>

On 401 response:
  → Axios interceptor fires
  → Call POST /api/auth/refresh with refreshToken
  → If successful: store new accessToken, retry original request
  → If failed: clear tokens, redirect to /login
```

## Database Architecture

### MongoDB Design Principles
- All collections use UUID string `_id` (not ObjectId)
- All collections have `isDeleted` flag for soft delete
- All collections have `createdAt` and `updatedAt` (via timestamps)
- Sensitive fields (password) have `select: false`
- Indexes defined at schema level, not in migrations
- No embedded arrays that grow unbounded (use references for large collections)

### Data Access Patterns
```javascript
// Read: always include isDeleted filter + lean()
Model.find({ isDeleted: false }).lean()
Model.findOne({ _id: id, isDeleted: false }).lean()

// Write: normal save/create
Model.create(data)
await record.save()

// Soft delete: set flag, never hard delete
await Model.findOneAndUpdate({ _id: id }, { $set: { isDeleted: true } })

// Pagination: skip/limit
Model.find({ isDeleted: false }).skip(skip).limit(limit).lean()
```

## Scalability Design

### Horizontal Scaling Readiness
- Stateless API (JWT auth, not sessions)
- All state in MongoDB (not in-process memory)
- No sticky sessions required
- Ready for load balancer deployment

### Performance Design
- `.lean()` on all read queries (removes Mongoose overhead)
- Pagination on all list endpoints
- Indexes on frequently queried fields (email, role, createdAt)
- Rate limiting to prevent abuse

## Security Architecture

### Defense Layers
1. **Transport**: HTTPS enforced in production
2. **Headers**: Helmet sets secure HTTP headers
3. **Rate limiting**: Prevent brute force and DDoS
4. **Input validation**: All inputs validated before processing
5. **Authentication**: JWT verification on protected routes
6. **Authorization**: Role-based access at middleware layer
7. **Data**: Sensitive fields never serialized in responses
8. **Secrets**: All secrets in environment variables, never in code

## Dependency Map

### Backend Dependencies
| Package | Purpose | Version Policy |
|---|---|---|
| express | HTTP framework | ^4.x |
| mongoose | MongoDB ODM | ^8.x |
| jsonwebtoken | JWT handling | ^9.x |
| express-validator | Input validation | ^7.x |
| bcryptjs | Password hashing | ^2.x |
| cors | CORS middleware | ^2.x |
| helmet | Security headers | ^7.x |
| morgan | Request logging | ^1.x |
| uuid | UUID generation | ^9.x |
| express-rate-limit | Rate limiting | ^7.x |
| dotenv | Env loading | ^16.x |

### Frontend Dependencies
| Package | Purpose | Version Policy |
|---|---|---|
| react | UI framework | ^18.x |
| react-dom | React DOM | ^18.x |
| @reduxjs/toolkit | State management | ^2.x |
| react-redux | Redux bindings | ^9.x |
| react-router-dom | Client routing | ^6.x |
| axios | HTTP client | ^1.x |
| vite | Build tool | ^5.x |
