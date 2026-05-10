# API.md — API Documentation Reference

## API Overview
- Base URL: `http://localhost:5000` (development)
- Authentication: Bearer Token (JWT) via `Authorization: Bearer <accessToken>` header
- Content-Type: `application/json` for all requests
- Versioning: No versioning currently — all routes under `/api`

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Human-readable success message",
  "data": { /* Response data, always an object */ }
}
```

### Paginated Success Response
```json
{
  "success": true,
  "message": "Users retrieved",
  "data": {
    "items": [/* array of items */],
    "totalCount": 150,
    "page": 1,
    "limit": 20
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Human-readable error message",
  "error": {
    "code": "ERROR_CODE_STRING",
    "details": [
      { "field": "email", "message": "Must be a valid email" }
    ]
  }
}
```

---

## HTTP Status Code Reference
| Code | Meaning | When Used |
|---|---|---|
| 200 OK | Request succeeded | GET, PATCH, DELETE success |
| 201 Created | Resource created | POST success (new resource) |
| 204 No Content | Success, no body | Rarely used |
| 400 Bad Request | Malformed request | Invalid JSON, missing required header |
| 401 Unauthorized | Auth failed | No token, invalid token, expired token |
| 403 Forbidden | Not authorized | Valid token but wrong role |
| 404 Not Found | Resource missing | Resource doesn't exist or is soft-deleted |
| 409 Conflict | Duplicate resource | Email already registered, duplicate key |
| 422 Unprocessable | Validation failed | express-validator errors |
| 500 Internal Server | Server error | Unhandled exception |

---

## Authentication Endpoints

### POST /api/auth/register
Register a new user.

**Auth Required**: No

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Success Response** (201):
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user": { "id": "uuid", "name": "John Doe", "email": "john@example.com", "role": "user" },
    "accessToken": "eyJ...",
    "expiresIn": "15m"
  }
}
```

**Error Codes**:
- 409: Email already registered (`DUPLICATE_ERROR`)
- 422: Validation failed (`VALIDATION_ERROR`)

---

### POST /api/auth/login
Authenticate a user.

**Auth Required**: No

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": { "id": "uuid", "name": "John Doe", "email": "john@example.com", "role": "user" },
    "accessToken": "eyJ...",
    "expiresIn": "15m"
  }
}
```

**Side Effect**: Sets `refreshToken` httpOnly cookie.

**Error Codes**:
- 401: Invalid credentials (`UNAUTHORIZED`)
- 422: Validation failed (`VALIDATION_ERROR`)

---

### POST /api/auth/refresh
Refresh the access token.

**Auth Required**: No (uses httpOnly cookie)

**Request**: No body (refresh token read from httpOnly cookie)

**Success Response** (200):
```json
{
  "success": true,
  "message": "Token refreshed",
  "data": {
    "accessToken": "eyJ...",
    "expiresIn": "15m"
  }
}
```

**Error Codes**:
- 401: Refresh token expired or invalid (`TOKEN_EXPIRED`, `INVALID_TOKEN`)

---

### POST /api/auth/logout
Logout the current user.

**Auth Required**: Yes

**Success Response** (200):
```json
{
  "success": true,
  "message": "Logged out successfully",
  "data": {}
}
```

**Side Effect**: Clears `refreshToken` cookie.

---

## User Endpoints

### GET /api/users/me
Get current authenticated user's profile.

**Auth Required**: Yes (user or admin)

**Success Response** (200):
```json
{
  "success": true,
  "message": "User retrieved",
  "data": {
    "user": { "id": "uuid", "name": "John", "email": "john@example.com", "role": "user" }
  }
}
```

---

### PATCH /api/users/me
Update current user's profile.

**Auth Required**: Yes (user or admin)

**Request Body** (all fields optional):
```json
{
  "name": "Updated Name"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "User updated",
  "data": {
    "user": { "id": "uuid", "name": "Updated Name", "email": "john@example.com" }
  }
}
```

---

## Profile Endpoints

### GET /api/profile
Get all profiles for current user.

**Auth Required**: Yes (user or admin)

**Success Response** (200):
```json
{
  "success": true,
  "message": "Profiles retrieved",
  "data": {
    "profiles": [
      { "id": "uuid", "name": "Profile Name", "createdAt": "2025-01-15" }
    ]
  }
}
```

---

### POST /api/profile
Create a new profile.

**Auth Required**: Yes

**Request Body**: Profile fields (see profile schema)

**Success Response** (201):
```json
{
  "success": true,
  "message": "Profile created",
  "data": { "profile": { /* profile object */ } }
}
```

---

### PATCH /api/profile/:id
Update a profile.

**Auth Required**: Yes (must own the profile)

**Success Response** (200):
```json
{
  "success": true,
  "message": "Profile updated",
  "data": { "profile": { /* updated profile */ } }
}
```

**Error Codes**:
- 403: Does not own this profile (`FORBIDDEN`)
- 404: Profile not found (`NOT_FOUND`)

---

### DELETE /api/profile/:id
Soft-delete a profile.

**Auth Required**: Yes (must own the profile)

**Success Response** (200):
```json
{
  "success": true,
  "message": "Profile deleted",
  "data": {}
}
```

---

## Generation Endpoints

### POST /api/generate/headline
Generate AI-powered content for a profile.

**Auth Required**: Yes

**Request Body**:
```json
{
  "profileId": "uuid",
  "type": "headline"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "Content generated",
  "data": {
    "content": "Generated headline text",
    "model": "gemini"
  }
}
```

---

### POST /api/feedback
Submit feedback on generated content.

**Auth Required**: Yes

**Request Body**:
```json
{
  "generationId": "uuid",
  "rating": true
}
```
> ⚠️ `rating` must be Boolean (`true`/`false`), NOT string (`"up"`/`"down"`)

**Success Response** (200):
```json
{
  "success": true,
  "message": "Feedback submitted",
  "data": {}
}
```
