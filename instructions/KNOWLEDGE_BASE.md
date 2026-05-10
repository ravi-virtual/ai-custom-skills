# KNOWLEDGE_BASE.md — Verified Domain Knowledge

## Purpose
Verified, tested facts about the system, technologies, and patterns used. Every entry here has been confirmed against the actual codebase or trusted source — not assumed.

---

## Section 1: Express.js Verified Facts

### Middleware Order Matters
**Fact**: In Express, middleware executes in the order it's registered. If `cors()` is registered after your routes, CORS headers won't be set for those routes.
**Verified**: Through debugging CORS failures in the codebase.

### Error Handler Signature
**Fact**: Express error handlers MUST have exactly 4 arguments `(err, req, res, next)`. If the function has 3 arguments, Express treats it as a regular middleware, not an error handler.
**Verified**: Express 4.x documentation, confirmed in debugging sessions.

### res.json() vs res.send()
**Fact**: `res.json()` is equivalent to `res.send()` with Content-Type set to `application/json` and JSON stringification applied automatically.
**Verified**: Express source code.

### express-validator validationResult
**Fact**: `validationResult(req)` returns an object. Use `.isEmpty()` to check for errors and `.array()` to get the error list. Each error in the array has `.path` (field name) and `.msg` (message) properties in v7.x.
**Verified**: express-validator v7 documentation and usage.

---

## Section 2: Mongoose Verified Facts

### lean() Returns Plain Objects
**Fact**: `.lean()` returns plain JavaScript objects instead of Mongoose Documents. This eliminates Mongoose document overhead but means Mongoose methods (like `.save()`) are unavailable on the result.
**Verified**: Mongoose documentation, performance testing.

### select: false on Query
**Fact**: Adding `select: false` to a schema field excludes it from all queries by default. To include it in a specific query, add `.select('+password')`.
**Verified**: Mongoose documentation and usage in User model.

### toJSON Transform Timing
**Fact**: The `toJSON.transform` function runs when `res.json()` or `JSON.stringify()` is called on a Mongoose document. It does NOT run on `.lean()` results — lean results are already plain objects.
**Verified**: Mongoose documentation.

### UUID _id with _id: false
**Fact**: When setting a custom `_id` type in a Mongoose schema, you must also set `_id: false` in the schema options to prevent Mongoose from adding its own auto-generated `_id` field.
**Verified**: Schema definition and testing.

---

## Section 3: JWT Verified Facts

### TokenExpiredError vs JsonWebTokenError
**Fact**: `jsonwebtoken` throws `TokenExpiredError` when a token is expired and `JsonWebTokenError` for any other invalid token (malformed, wrong signature, etc.). Check `err.name` to distinguish them.
**Verified**: jsonwebtoken documentation and error handling implementation.

### jwt.verify is Synchronous
**Fact**: `jwt.verify()` is synchronous (not a Promise). It either returns the decoded payload or throws an error. No await needed.
**Verified**: jsonwebtoken source code.

### Bearer Token Extraction
**Fact**: The standard format is `Authorization: Bearer <token>`. Extraction: `req.headers.authorization?.split(' ')[1]`. The `?.` is important — headers.authorization may be undefined.
**Verified**: RFC 6750 and implementation.

---

## Section 4: React/Redux Verified Facts

### useEffect Cleanup Order
**Fact**: React calls the useEffect cleanup function BEFORE running the effect again (on re-render with changed deps) and when the component unmounts. Return a cleanup function from useEffect to prevent memory leaks.
**Verified**: React documentation.

### createSlice State Mutation
**Fact**: In Redux Toolkit's `createSlice`, you CAN directly mutate `state` in reducers because RTK uses Immer under the hood to produce immutable updates. Outside of RTK reducers, state must never be mutated.
**Verified**: Redux Toolkit documentation.

### useSelector Equality
**Fact**: `useSelector` uses reference equality by default. Objects returned from selectors will cause re-renders even if their content didn't change. Use `shallowEqual` from react-redux or `createSelector` from reselect for object comparisons.
**Verified**: React-Redux documentation.

### Thunk rejectWithValue
**Fact**: In createAsyncThunk, `rejectWithValue(value)` sets `action.payload` in the rejected case. Without it, `action.error` contains the serialized error (less readable). Always use `rejectWithValue` for user-friendly error messages.
**Verified**: Redux Toolkit documentation.

---

## Section 5: Axios Verified Facts

### Interceptor Execution Order
**Fact**: Request interceptors run in reverse registration order (last in, first out). Response interceptors run in forward order (first in, first out). Register auth interceptors before error interceptors.
**Verified**: Axios documentation.

### Error Response Data
**Fact**: When a request fails with a 4xx or 5xx status, Axios throws an error. The response data is at `error.response.data`. Always access error response as `err.response?.data?.message` (optional chain to handle network errors where response may be undefined).
**Verified**: Axios documentation and debugging sessions.

### withCredentials for Cookies
**Fact**: To send cookies cross-origin (e.g., httpOnly refresh token cookie), both the Axios request must include `withCredentials: true` AND the backend CORS must have `credentials: true`. Both are required — one without the other won't work.
**Verified**: CORS specification, debugging sessions.

---

## Section 6: Security Facts

### bcrypt Cost Factor
**Fact**: A cost factor of 10 produces ~100ms hash time on modern hardware, which is acceptable for registration/login. Increasing to 12 means ~300ms. Never use cost factor < 10.
**Verified**: bcrypt security guidelines.

### CORS credentials and wildcard origin
**Fact**: When CORS credentials mode is enabled, the `Access-Control-Allow-Origin` header CANNOT be a wildcard (`*`). It must specify an exact origin. Browsers reject the response otherwise.
**Verified**: CORS specification.

### helmet() Default Headers
**Fact**: `app.use(helmet())` adds: Content-Security-Policy, Cross-Origin-Embedder-Policy, Cross-Origin-Opener-Policy, Cross-Origin-Resource-Policy, DNS-Prefetch-Control, X-Content-Type-Options, X-DNS-Prefetch-Control, X-Download-Options, X-Frame-Options, X-Permitted-Cross-Domain-Policies, X-XSS-Protection.
**Verified**: Helmet documentation.

---

## Section 7: Node.js Facts

### require() Caching
**Fact**: Node.js caches `require()` calls — the same module returns the same instance. This is why circular requires can cause `{}` to be returned (the module isn't fully initialized yet when it's first required in the cycle).
**Verified**: Node.js documentation on module system.

### process.env Values are Always Strings
**Fact**: All `process.env.X` values are strings. Numeric values like `PORT=5000` are strings `"5000"` and must be converted with `parseInt()` or `Number()`. Boolean values like `DEBUG=true` are strings `"true"` — use comparison `=== 'true'`.
**Verified**: Node.js process documentation.
