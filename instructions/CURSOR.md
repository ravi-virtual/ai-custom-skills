# CURSOR.md — Cursor AI IDE Operating Instructions

## Role in This Workspace
You are the in-IDE AI pair programmer operating within a production AI Operating System. You have real-time access to the codebase and must apply these rules to every suggestion, edit, and generation.

## Codebase-Aware Rules

### Before Any Edit
1. Read the target file fully before modifying it
2. Check ARCHITECTURE.md to understand system boundaries
3. Check CODING_STANDARDS.md for naming/structure conventions
4. Verify the change doesn't break existing interfaces

### Code Generation Rules
Every generated function must have:
- Error handling (try/catch for async, null checks for sync)
- Input validation before processing
- Consistent return types (no `undefined` surprises)
- JSDoc or docstring (language-appropriate)

### Context Window Management
- Keep the most relevant files in context (open tabs)
- Always include the constants file when editing controllers
- Include the model file when editing routes that use it
- Include test files when fixing bugs

## MERN Stack Patterns (Non-Negotiable)

### Backend File Generation
When generating backend files, ALWAYS use:
```
Controller → PascalCase name, JSDoc on every function, try/catch
Route → camelCase name, import chain: auth → guard → validator → controller
Model → PascalCase name, UUID _id, isDeleted flag, timestamps
Validator → camelCase name, express-validator, validateRequest at end of array
Middleware → camelCase name, single responsibility, call next() or return error
```

### Response Formatting (NEVER deviate)
```javascript
// ✅ Success
return new ApiResponse(ResponseCodes.OK, 'Message', { data }).send(res);

// ✅ Error
return sendError(res, { statusCode: ResponseCodes.NOT_FOUND, message: 'Not found', code: ErrorCodes.NOT_FOUND });

// ❌ FORBIDDEN
return res.status(200).json({ data });
return res.json({ error: 'Not found' });
```

### Frontend File Generation
```javascript
// ✅ Correct slice structure
const slice = createSlice({
  name: 'feature',
  initialState: { data: null, loading: false, error: null },
  reducers: {
    clearError: (state) => { state.error = null; }
  }
});

// ✅ Correct API call location (in slice thunk, not component)
export const fetchData = createAsyncThunk('feature/fetch', async (id, { rejectWithValue }) => {
  try {
    const { data } = await fetchDataApi(id);
    return data.data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed');
  }
});
```

## Inline Suggestion Rules
When Cursor suggests code inline:
- Suggestions must follow the active skill patterns (CLAUDE.md, AGENT_RULES.md)
- Do not suggest `console.log` in production paths (use logging utility instead)
- Do not suggest hardcoded strings for error codes or status codes
- Always suggest the full middleware chain, not partial routes

## Refactoring Workflow
When asked to refactor:
1. Map all usages of the target code first
2. Identify all side effects of the change
3. Create the new version without removing the old one
4. Update all call sites
5. Remove the old version only when all sites are updated
6. Run mental test: does the interface remain compatible?

## Debugging Support
When Cursor detects an error:
1. Read the error message fully — identify file, line, type
2. Check FAILURES.md for similar past failures
3. Apply the Trace-Solve-Clean workflow (DEBUGGING.md)
4. Never suggest a fix that introduces `any` types or removes error handling

## Auto-Complete Boundaries
Cursor should NOT auto-complete:
- Hardcoded credentials or tokens
- Raw `process.env.X` outside `constants.js`
- Direct database connections outside model files
- `res.json()` directly — always use ApiResponse utility

## Code Review Assistance
When reviewing a diff or PR:
- Check against CODING_STANDARDS.md checklist
- Flag any security violations (SECURITY.md)
- Identify missing error handling
- Note any naming convention violations
- Check for missing JSDoc on public methods

## File Template Awareness
Always use these templates when creating new files:
- Controller: See BACKEND.md → Controller Pattern section
- Route: See BACKEND.md → Route Definitions section
- Slice: See FRONTEND.md → Redux Toolkit section
- Component: See FRONTEND.md → Component Conventions section
- API function: See FRONTEND.md → Axios Instance section
