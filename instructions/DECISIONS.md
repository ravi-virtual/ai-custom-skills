# DECISIONS.md — Architectural Decision Records

## Format
Each entry follows this structure:
```markdown
## Decision [ID]: [Title]
**Date**: YYYY-MM-DD
**Status**: Active | Deprecated | Superseded by [ID]
**Context**: [Situation that prompted this decision]
**Decision**: [What was decided]
**Rationale**: [Why this was the right choice]
**Alternatives Rejected**: [Other approaches and why rejected]
**Consequences**: [Known tradeoffs]
```

---

## Decision ARCH-001: UUID for MongoDB _id
**Date**: Project Start  
**Status**: Active  

**Context**: We needed to choose an identifier strategy for MongoDB documents.

**Decision**: Use UUID v4 strings as `_id` instead of MongoDB's native ObjectId.

**Rationale**:
- UUIDs are portable — can be generated on client or server without coordination
- No serialization issues (ObjectId requires special handling in JSON)
- Consistent with SQL-style ID patterns, easier for frontend consumption
- Enables pre-generating IDs before insertion (useful for idempotent creation)

**Alternatives Rejected**:
- ObjectId: Serialization overhead, confusing for developers used to UUIDs, not web-friendly
- Auto-incrementing integer: Doesn't work in distributed systems, requires coordination

**Consequences**: 
- Slightly larger storage than ObjectId (36 chars vs 12 bytes)
- Cannot rely on ObjectId timestamp ordering — use `createdAt` field instead
- Must add `_id: false` to schema options and manually set default

---

## Decision ARCH-002: Soft Delete with isDeleted Flag
**Date**: Project Start  
**Status**: Active  

**Context**: Needed a deletion strategy for user data.

**Decision**: Never physically delete records. Use `isDeleted: true` flag for all user-facing deletes.

**Rationale**:
- Data recovery capability if user requests restoration
- Audit trail preserved for compliance
- Referential integrity maintained (related records still point to valid IDs)
- Easier to implement "undo delete" features in the future

**Alternatives Rejected**:
- Hard delete: Irreversible, breaks referential integrity, no audit trail
- Archive table: Complex queries, maintenance burden

**Consequences**:
- Every read query MUST include `{ isDeleted: false }` filter — a required discipline
- Database grows over time (mitigated with background cleanup jobs if needed)
- "Deleted" records still occupy indexes

---

## Decision ARCH-003: Express-Validator over Joi
**Date**: Project Start  
**Status**: Active  

**Context**: Needed input validation for Express APIs.

**Decision**: Use express-validator instead of Joi for input validation.

**Rationale**:
- Native integration with Express middleware chain (validator as middleware)
- No need to convert validated result to req.body
- Familiar pattern, good documentation
- Supports async validation rules natively

**Alternatives Rejected**:
- Joi: Requires separate validation step, standalone — doesn't integrate as middleware naturally
- Zod: TypeScript-first, overhead for CommonJS backend
- Manual validation: Error-prone, inconsistent, not maintainable

**Consequences**:
- Validation errors must be extracted with `validationResult(req)` in `validateRequest` middleware
- Less powerful schema composition than Joi or Zod for complex nested objects

---

## Decision ARCH-004: Single constants.js for All Config
**Date**: Project Start  
**Status**: Active  

**Context**: Needed a strategy for managing environment variables and constants.

**Decision**: All `process.env.X` access is confined to `src/config/constants.js`. All other files import from there.

**Rationale**:
- Single place to validate env vars at startup (fail fast)
- Easy to audit what environment variables the app depends on
- Prevents scattered env access across files (maintenance nightmare)
- Makes mocking env vars in tests trivial

**Alternatives Rejected**:
- Access process.env anywhere: Scattered, hard to audit, can't validate at startup
- Multiple config files per domain: Duplication risk, harder to see full picture

**Consequences**:
- All engineers (human and AI) must be disciplined about not adding `process.env.X` elsewhere
- constants.js grows larger in big applications (mitigated with sections/comments)

---

## Decision ARCH-005: JWT over Sessions
**Date**: Project Start  
**Status**: Active  

**Context**: Chose authentication strategy.

**Decision**: Use stateless JWT authentication (15m access token + 15m refresh token) instead of server-side sessions.

**Rationale**:
- Stateless: API servers can scale horizontally without shared session store
- No Redis dependency for session management
- Mobile-friendly (no cookies required for basic auth)
- Refresh token rotation provides reasonable security

**Alternatives Rejected**:
- Server sessions: Requires sticky sessions or shared Redis, adds infrastructure dependency
- API keys: Not user-friendly, requires key rotation UI, not standard for user auth

**Consequences**:
- Access tokens cannot be invalidated before expiry (mitigated by 15m expiry)
- Refresh tokens must be rotated on use to limit breach window
- Token refresh adds frontend complexity (interceptor logic)

---

## Decision ARCH-006: Redux Toolkit for Global State
**Date**: Project Start  
**Status**: Active  

**Context**: Chose frontend state management approach.

**Decision**: Use Redux Toolkit for all global and shared state. Context API only for low-frequency, low-scope concerns.

**Rationale**:
- Predictable state updates through Redux DevTools
- Excellent async support via createAsyncThunk
- Standardized pattern across all features (one slice per feature)
- Strong TypeScript support (future-proofing)

**Alternatives Rejected**:
- Context API for global state: No DevTools, performance issues with frequent updates, prop drilling risk
- Zustand: Smaller but less mature ecosystem, less team familiarity
- React Query: Excellent for server state, but adds complexity alongside Redux

**Consequences**:
- More boilerplate than Context API for simple cases
- Requires discipline to not misuse local state as Redux state

---

## Decision FEED-001: Feedback Rating as Boolean
**Date**: 2026-04-12  
**Status**: Active  
**Reference**: Conversation 9a00e0dc - Fixing Feedback Validation Error  

**Context**: CastError occurred when "up"/"down" strings were sent to a Boolean field.

**Decision**: The feedback/rating field must be a Boolean (`true` = positive, `false` = negative).

**Rationale**:
- Backend schema defined it as Boolean — the source of truth
- Boolean is simpler to query ("find all positive feedback")
- Frontend should transform string values to Boolean before API call

**Alternatives Rejected**:
- Change schema to String: Breaks boolean query patterns, complicates aggregation
- Use enum string in schema: Adds complexity without benefit

**Consequences**:
- Frontend must always send `true`/`false`, never `"up"`/`"down"`
- Any UI that shows "thumbs up/down" must map to Boolean in the API call

---

## Decision DEPLOY-001: Gemini → Grok → Free OpenAI Fallback
**Date**: 2026-04-12  
**Status**: Active  
**Reference**: Conversation e5e1b2e6 - Configuring Multi-Model AI Fallback  

**Context**: Needed a resilient AI model strategy with free-tier models.

**Decision**: Use Gemini as primary, Grok as secondary, free OpenAI model as tertiary fallback.

**Rationale**:
- Gemini has generous free tier and excellent performance
- Grok (via xAI) provides good alternative without cost
- Free OpenAI tier as last resort ensures availability
- Fallback chain ensures 99%+ AI availability

**Consequences**:
- Each model has different response format — normalization layer required
- Each model has different rate limits — timeout config must be per-model
- API keys needed for all three services
