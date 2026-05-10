# TESTING.md — Testing Standards & Strategy

## Testing Philosophy
Tests are the executable specification of the system. They verify correctness, prevent regressions, and document behavior. Every feature must be testable — if it can't be tested, the design is wrong.

## Testing Pyramid

```
        ┌─────────────────┐
        │   E2E Tests      │  ← Fewest, slowest, most realistic
        ├─────────────────────┤
        │  Integration Tests  │  ← Medium count, moderate speed
        ├────────────────────────┤
        │     Unit Tests         │  ← Most, fastest, isolated
        └────────────────────────┘
```

---

## Section 1: Mental Testing Protocol (Required Before Every Delivery)

Before writing automated tests, mentally verify all paths:

### For Every Backend Endpoint
```
□ Happy Path: Valid input, authenticated, authorized → 2xx response with correct data
□ Missing Token: No Authorization header → 401 UNAUTHORIZED
□ Invalid Token: Malformed JWT → 401 INVALID_TOKEN
□ Expired Token: Valid JWT but expired → 401 TOKEN_EXPIRED
□ Wrong Role: Valid token but wrong role → 403 FORBIDDEN
□ Validation Failure: Missing/invalid body fields → 422 VALIDATION_ERROR with field details
□ Not Found: Resource doesn't exist or isDeleted → 404 NOT_FOUND
□ Conflict: Duplicate unique field (email) → 409 DUPLICATE_ERROR
□ Server Error: DB connection fails → 500 SERVER_ERROR (no stack trace in production)
```

### For Every Frontend Component
```
□ Loading State: Shows loading indicator while Redux state.loading is true
□ Success State: Renders correctly with populated data
□ Error State: Shows error message when Redux state.error is set
□ Empty State: Handles null/undefined data without crashing
□ User Interaction: Click/submit dispatches correct thunk
□ Cleanup: useEffect cleanup prevents state updates on unmounted component
```

---

## Section 2: Unit Testing

### What Gets Unit Tests
- Utility functions in `utils/`
- Custom hooks (with renderHook)
- Redux slice reducers
- Validator rule sets
- Auth middleware logic

### Unit Test Structure (Jest)
```javascript
describe('[Module Name]', () => {
  describe('[Function Name]', () => {
    it('should [expected behavior] when [condition]', () => {
      // Arrange
      const input = { ... };
      const expected = { ... };

      // Act
      const result = functionUnderTest(input);

      // Assert
      expect(result).toEqual(expected);
    });

    it('should throw when [error condition]', () => {
      expect(() => functionUnderTest(invalidInput)).toThrow('Expected message');
    });
  });
});
```

### Slice Reducer Tests
```javascript
import userReducer, { clearError } from './userSlice';

describe('userSlice', () => {
  const initialState = { user: null, loading: false, error: null };

  it('should return initial state', () => {
    expect(userReducer(undefined, { type: '@@INIT' })).toEqual(initialState);
  });

  it('should clear error on clearError action', () => {
    const stateWithError = { ...initialState, error: 'Something failed' };
    expect(userReducer(stateWithError, clearError())).toEqual(initialState);
  });

  it('should set loading on fetchUser.pending', () => {
    const action = { type: 'user/fetchUser/pending' };
    const state = userReducer(initialState, action);
    expect(state.loading).toBe(true);
    expect(state.error).toBeNull();
  });
});
```

---

## Section 3: Integration Testing (API Tests)

### What Gets Integration Tests
- Every Express route/endpoint
- Auth middleware chain
- Database operations

### API Test Structure (Jest + Supertest)
```javascript
const request = require('supertest');
const app = require('../src/app');
const { connectDB, disconnectDB } = require('../src/config/database');
const User = require('../src/models/User');

describe('POST /api/auth/login', () => {
  beforeAll(async () => { await connectDB(); });
  afterAll(async () => { await disconnectDB(); });

  beforeEach(async () => {
    await User.deleteMany({}); // clean test DB
    await User.create({ email: 'test@test.com', password: 'hashed', role: 'user' });
  });

  it('should return 200 and tokens on valid credentials', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@test.com', password: 'plaintext' });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.data.accessToken).toBeDefined();
  });

  it('should return 401 on wrong password', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@test.com', password: 'wrongpass' });

    expect(res.status).toBe(401);
    expect(res.body.success).toBe(false);
  });

  it('should return 422 on invalid email format', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'not-an-email', password: 'password123' });

    expect(res.status).toBe(422);
    expect(res.body.error.code).toBe('VALIDATION_ERROR');
  });
});
```

### Protected Route Test Pattern
```javascript
const getValidToken = async () => {
  const res = await request(app)
    .post('/api/auth/login')
    .send({ email: 'test@test.com', password: 'password123' });
  return res.body.data.accessToken;
};

it('should return 401 without token', async () => {
  const res = await request(app).get('/api/users/me');
  expect(res.status).toBe(401);
});

it('should return 200 with valid token', async () => {
  const token = await getValidToken();
  const res = await request(app)
    .get('/api/users/me')
    .set('Authorization', `Bearer ${token}`);
  expect(res.status).toBe(200);
});
```

---

## Section 4: Test Coverage Requirements

| Code Area | Minimum Coverage |
|---|---|
| Utility functions | 100% |
| Controller functions | Happy path + all error paths |
| Middleware | 100% (critical security code) |
| Validators | All fields, all rule variations |
| Redux slices | All reducers + critical thunks |
| React components | Key render states |

---

## Section 5: Test Environment Setup

### Backend Test Config
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.test.js'],
  setupFilesAfterFramework: ['./jest.setup.js'],
  coverageReporters: ['text', 'lcov'],
};

// .env.test
NODE_ENV=test
MONGO_URI=mongodb://localhost:27017/myapp_test  // ← Separate test DB
JWT_SECRET=test-secret-32-chars-minimum-length
JWT_REFRESH_SECRET=test-refresh-secret-32-chars
```

### Test Database Rules
- Use a separate `_test` database — never test against development or production
- Clean collections before each test (beforeEach)
- Seed only what the test needs (no shared global test data)
- Close database connection afterAll to prevent jest from hanging

---

## Section 6: Continuous Testing

### Pre-Commit Checks
```bash
npm test                  # Run all tests
npm run test:coverage     # Check coverage thresholds
npm run lint              # Run ESLint
```

### CI Pipeline Testing
```yaml
# Runs on every PR
- Install dependencies
- Run linter
- Run unit tests with coverage
- Run integration tests (with test MongoDB)
- Fail pipeline if coverage drops below threshold
- Fail pipeline if any test fails
```
