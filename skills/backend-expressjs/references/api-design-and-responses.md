# API Design, Response Format & apiResponse Utility

Part of the `backend-expressjs` skill. Read this when the task touches the topics below.

## Contents
- [API Design Rules](#api-design-rules)
- [Request & Response Format](#request--response-format)
- [apiResponse Utility](#apiresponse-utility)

## API Design Rules

### URL Structure
```
/api/{resource}              → collection
/api/{resource}/:id          → single item
/api/{resource}/:id/{sub}    → sub-resource (use sparingly)
```

### HTTP Method Mapping
| Action | Method | Example |
|---|---|---|
| List all | GET | `GET /api/users` |
| Get one | GET | `GET /api/users/:id` |
| Create | POST | `POST /api/users` |
| Full update | PUT | `PUT /api/users/:id` |
| Partial update | PATCH | `PATCH /api/users/:id` |
| Delete | DELETE | `DELETE /api/users/:id` |

### Query Parameter Conventions
```
?page=1&limit=20    → pagination
?sort=-createdAt    → sort descending (-) / ascending (no prefix)
?search=john        → text search
?status=active      → field filter
```

## Request & Response Format

### Standard Success Response
```js
{
  success: true,
  status: ResponseCodes.OK,
  message: "User fetched successfully",
  data: { }       // always an object — never a raw array or primitive
}
```

### Paginated Response
```js
{
  success: true,
  status: ResponseCodes.OK,
  message: "Users fetched successfully",
  data: {
    users: [ ],     // list nested inside data object
    totalCount: 150 // only totalCount — no page/limit/totalPages
  }
}
```

### Standard Validation Error
```js
{
  success: false,
  status: ResponseCodes.BAD_REQUEST,
  message: "Validation failed",
  error: {
    code: ErrorCodes.VALIDATION_ERROR,
    details: [
      { field: "email", message: "Email is required" }
    ]
  }
}
```

### Standard Server / App Error
```js
{
  success: false,
  status: ResponseCodes.SERVER_ERROR,
  message: "Something went wrong",
  error: { code: ErrorCodes.SERVER_ERROR, details: [] }
}
```

> Stack traces are **never** included in production responses.

### HTTP Status Code Map
| Situation | Constant | Code |
|---|---|---|
| Success (read) | `ResponseCodes.OK` | 200 |
| Created | `ResponseCodes.CREATED` | 201 |
| No content | `ResponseCodes.NO_CONTENT` | 204 |
| Validation / Bad request | `ResponseCodes.BAD_REQUEST` | 400 |
| Unauthenticated | `ResponseCodes.UNAUTHORIZED` | 401 |
| Forbidden | `ResponseCodes.FORBIDDEN` | 403 |
| Not found | `ResponseCodes.NOT_FOUND` | 404 |
| Conflict / Duplicate | `ResponseCodes.CONFLICT` | 409 |
| Server error | `ResponseCodes.SERVER_ERROR` | 500 |

## apiResponse Utility

```js
// src/utils/apiResponse.js
const { ResponseCodes, ErrorCodes } = require('../config/constants');

class ApiResponse {
  constructor(statusCode, message, data = {}) {
    this.statusCode = statusCode;
    this.success = statusCode < 400;
    this.message = message;
    this.data = data;
  }

  send(res) {
    return res.status(this.statusCode).json({
      success: this.success,
      status: this.statusCode,
      message: this.message,
      data: this.data,
    });
  }
}

const sendError = (res, {
  statusCode = ResponseCodes.SERVER_ERROR,
  message = 'Something went wrong',
  code = ErrorCodes.SERVER_ERROR,
  details = [],
} = {}) => {
  return res.status(statusCode).json({
    success: false,
    status: statusCode,
    message,
    error: { code, details },
  });
};

module.exports = { ApiResponse, sendError };
```

**Usage:**
```js
// Success
return new ApiResponse(ResponseCodes.OK, 'User fetched', { user }).send(res);

// Error
return sendError(res, { statusCode: ResponseCodes.NOT_FOUND, message: 'User not found', code: ErrorCodes.NOT_FOUND });
```
