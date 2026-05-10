# TERMINOLOGY.md — Domain Terminology & Definitions

## Purpose
Standardized definitions for all terms used in this system. When in doubt about a term's meaning, reference this file. Consistent terminology prevents miscommunication between agents.

---

## Architecture Terms

| Term | Definition |
|------|-----------|
| **AI-OS** | AI Operating System — the markdown-based framework of files that govern AI agent behavior in this workspace |
| **MERN Stack** | MongoDB + Express.js + React + Node.js — the technology stack for this project |
| **Middleware Chain** | The sequence of Express middleware functions: hasToken → isAuthenticated → role → validator → controller |
| **Orchestrator** | The high-level agent responsible for planning, decomposing tasks, and coordinating specialist agents |
| **Specialist Agent** | An AI agent with a defined area of expertise (MERN Developer, Debugger, QA, etc.) |
| **Context Bundle** | The set of files loaded at session start to give an AI agent operational context |
| **Skill** | A specialized instruction set for a specific task domain (e.g., backend-expressjs skill) |
| **Handoff Package** | The structured document ORCH-01 sends to a specialist agent when assigning a task |
| **Output Report** | The structured document a specialist agent sends back to ORCH-01 on task completion |

---

## Backend Terms

| Term | Definition |
|------|-----------|
| **Controller** | An Express module containing request handler functions for a specific resource (PascalCase filename) |
| **Route file** | An Express Router module that defines URL paths and their middleware chains (camelCase filename) |
| **Middleware** | An Express function that runs before the controller; handles auth, validation, rate limiting |
| **hasToken** | First auth middleware; extracts and verifies JWT, sets req.user |
| **isAuthenticated** | Second auth middleware; confirms req.user is a valid, non-deleted account |
| **isAdmin** | Role middleware; ensures req.user.role === 'admin' |
| **isUser** | Role middleware; ensures req.user.role is 'user' or 'admin' |
| **Validator** | An array of express-validator rules + validateRequest middleware |
| **validateRequest** | The final item in every validator array; checks validationResult and sends 422 if errors |
| **ApiResponse** | Success response utility class; produces `{ success: true, message, data }` |
| **sendError** | Error response utility function; produces `{ success: false, message, error: { code, details } }` |
| **soft delete** | Setting `isDeleted: true` instead of physically removing a record |
| **constants.js** | The single file where all process.env values and application constants are defined |
| **UUID** | Universally Unique Identifier (v4 string); used as `_id` for all MongoDB documents |

---

## Frontend Terms

| Term | Definition |
|------|-----------|
| **Slice** | A Redux Toolkit slice — manages state, reducers, and thunks for one feature domain |
| **Thunk** | An async Redux action created with createAsyncThunk; handles API calls and state updates |
| **axiosInstance** | The pre-configured Axios instance with base URL and auth interceptors |
| **API function** | A function in an `*Api.js` file that calls axiosInstance for one specific backend endpoint |
| **Selector** | A function used with useSelector to derive state from the Redux store |
| **Protected route** | A React Router route that redirects unauthenticated users to login |
| **ProtectedRoute** | The wrapper component that checks authentication and conditionally renders |
| **clearError** | The standard Redux reducer action that resets `state.error` to null |
| **rejectWithValue** | Redux Toolkit's mechanism to set action.payload in the rejected case of a thunk |

---

## AI/Agent Terms

| Term | Definition |
|------|-----------|
| **CO-STAR** | Context, Objective, Style, Tone, Audience, Response — prompt engineering framework |
| **Chain of Thought (CoT)** | Prompting technique that instructs the model to reason step-by-step |
| **Few-Shot** | Prompting technique that provides examples of desired input-output patterns |
| **Confidence score** | A percentage (0-100%) indicating how certain an agent is about a decision |
| **Trace-Solve-Clean** | Three-phase debugging workflow: locate the bug → fix it → remove debug artifacts |
| **Memory file** | A markdown file in the AI-OS that stores persistent knowledge across sessions |
| **Context window** | The maximum amount of text an AI model can process in one interaction |
| **Hallucination** | When an AI generates plausible-sounding but factually incorrect information |
| **Grounding** | Verifying AI claims against actual files or external sources |
| **Vector memory** | A semantic search-based memory system using embeddings for meaning-based retrieval |
| **Skill activation** | The process of recognizing that a task matches a skill trigger and applying that skill |

---

## DevOps Terms

| Term | Definition |
|------|-----------|
| **CI/CD** | Continuous Integration/Continuous Deployment — automated build, test, deploy pipeline |
| **Production** | The live environment serving real users |
| **Staging** | A pre-production environment for testing before production deployment |
| **Environment variable** | Configuration value stored outside the code (in .env file), never committed to git |
| **PM2** | Process manager for Node.js; keeps the server running and restarts on crash |
| **Rollback** | Reverting to a previous version of the code after a failed deployment |

---

## Security Terms

| Term | Definition |
|------|-----------|
| **JWT** | JSON Web Token — a signed token used for stateless authentication |
| **Access token** | Short-lived JWT (15m) used to authenticate API requests |
| **Refresh token** | Short-lived JWT (15m) used to obtain new access tokens |
| **httpOnly cookie** | A cookie not accessible to JavaScript; safer for storing refresh tokens |
| **bcrypt** | Password hashing algorithm; always used with cost factor 10+ |
| **CORS** | Cross-Origin Resource Sharing — controls which origins can access the API |
| **Helmet** | Express middleware that sets secure HTTP headers |
| **Rate limiting** | Restricting the number of requests per IP per time window |
| **Soft delete** | Marking a record as deleted (isDeleted: true) without physically removing it |
| **Bearer token** | Authentication scheme where the token is sent in the Authorization header |

---

## Error Code Reference

| Code String | Meaning |
|---|---|
| `VALIDATION_ERROR` | Input failed express-validator rules |
| `NOT_FOUND` | Resource doesn't exist or is soft-deleted |
| `UNAUTHORIZED` | No token or invalid credentials |
| `FORBIDDEN` | Valid token but insufficient permissions |
| `DUPLICATE_ERROR` | Unique constraint violated (e.g., duplicate email) |
| `INVALID_TOKEN` | JWT is malformed or has wrong signature |
| `TOKEN_EXPIRED` | JWT is valid but past its expiry time |
| `SERVER_ERROR` | Unhandled exception (generic 500 error) |
