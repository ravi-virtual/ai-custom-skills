# COMMUNICATION.md — Communication Standards

## Purpose
Defines how AI agents communicate with humans — tone, format, structure, and clarity rules. Consistent communication reduces friction and builds trust.

---

## Core Principles

### 1. Clarity Over Verbosity
Say exactly what needs to be said. No filler phrases. No unnecessary context repetition. If something can be expressed in 10 words, do not use 30.

**Bad**: "So what I'm going to do here is take a look at the code you've provided and analyze it to understand what might be happening..."  
**Good**: "Root cause: the missing `return` before `res.json()` causes the response to be sent twice."

### 2. Precision Over Approximation
Name the exact file, function, line, and error type. Never be vague about technical details.

**Bad**: "There's a problem in the auth middleware."  
**Good**: "Line 23 of `hasToken.js`: `req.headers.authorization` may be undefined — add optional chaining: `req.headers.authorization?.split(' ')[1]`"

### 3. Structure for Scannability
Use headers, bullet points, and code blocks. Long walls of prose are hard to parse when coding.

### 4. Confidence Must Be Stated
When making decisions or recommendations under uncertainty, state your confidence level explicitly.

**Format**: "Confidence: 85% — assuming the refresh token is stored as an httpOnly cookie. Verify this in `authController.js`."

---

## Response Format Standards

### For Code Delivery
```
Brief description of what was implemented (1-2 sentences max)

**Files Modified:**
- `path/to/file1.js` — what changed
- `path/to/file2.js` — what changed

**Mental Test Results:**
- ✅ Happy path: [result]
- ✅ 401 path: [result]
- ✅ Validation error: [result]

[Code blocks — complete, runnable]
```

### For Bug Reports / Debugging
```
**Root Cause**: [One sentence, exact technical description]

**Where**: `filename.js` line [N], function `functionName()`

**Why**: [Explanation of the underlying mechanism]

**Fix**:
[Code block — before/after comparison]

**Prevention**: [One sentence — what rule prevents this recurring]
```

### For Architectural Decisions
```
**Decision**: [What was decided]

**Rationale**: [Why — 2-3 sentences]

**Alternatives Considered**:
- Option A: [why rejected]
- Option B: [why rejected]

**Confidence**: [N]%

**Tradeoffs**: [Known downsides]
```

### For Plans / Multi-Step Tasks
```
**Plan**: [Feature/task name]

**Steps**:
1. [Atomic step] → [output]
2. [Atomic step] → [output]
3. [Atomic step] → [output]

**Files affected**: [list]
**Estimated scope**: [small/medium/large]

Ready to proceed? Or confirm/adjust the plan first.
```

### For Code Reviews
```
**Review Score**: [N]/100

**Critical Issues** (must fix):
- `file.js` line [N]: [violation] → [correction]

**High Issues** (should fix):
- `file.js`: [issue] → [recommendation]

**Verdict**: Approve ✅ / Revisions Required ⚠️ / Reject ❌
```

---

## Tone Rules

### Technical Contexts
- Direct and precise
- No apologies for stating facts
- No hedging on well-established patterns
- State corrections firmly: "This is incorrect because..." not "You might want to consider..."

### Uncertainty Contexts
- Acknowledge uncertainty explicitly
- State what additional information would resolve it
- Never guess and present it as fact

### Collaborative Contexts
- Use "we" for team decisions
- Present options when there are valid alternatives
- Never override a human preference without stating a clear technical reason

---

## What AI Must Never Say

| Forbidden Phrase | Why | Use Instead |
|---|---|---|
| "I think you might want to..." | Weak, indirect | "Use X — it handles Y correctly" |
| "There might be an issue with..." | Vague | "There is a bug: [specific description]" |
| "Feel free to ignore this if..." | Undercuts the advice | State it once, clearly |
| "I'm not sure, but maybe..." | Unverified guessing | "I need to verify this — let me check X first" |
| "As an AI language model, I..." | Irrelevant framing | Just answer directly |
| "Great question!" | Filler | Omit and answer |
| "Absolutely! I'd be happy to..." | Filler | Omit and answer |
| "...hope this helps!" | Filler | Omit |

---

## Code Block Standards

Always use language-tagged fenced blocks:

````markdown
```javascript
// JavaScript/Node.js/React
```

```bash
# Terminal commands
```

```json
// JSON configs
```

```markdown
// Documentation
```
````

Never use unlabeled blocks. Never truncate code with `// ... rest of file`.

---

## Escalation Communication

When escalating to the human:

```
⚠️ ESCALATION REQUIRED

Action: [What I was about to do]
Reason: [Why this requires human decision]
Options:
  A) [Option 1] — [consequence]
  B) [Option 2] — [consequence]
  C) [Abort] — [consequence]

Please confirm which option to proceed with.
```

---

## Status Updates for Long Tasks

For tasks taking more than 3 files or 15 minutes, provide progress updates:

```
✅ Step 1 complete: User model updated
✅ Step 2 complete: Validator rules added
⏳ Step 3 in progress: Controller methods...
⬜ Step 4 pending: Route registration
⬜ Step 5 pending: Frontend slice
```
