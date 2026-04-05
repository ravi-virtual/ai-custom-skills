---
name: sailsjs-helper
description: >
  Use this skill whenever the user wants to create a Sails.js helper only — without building a full
  API endpoint. Triggers include: "create a helper", "add a helper", "write a sails helper",
  "new helper function", or when a user asks to extract logic into a reusable helper. Also trigger
  when the user mentions a sails helper name and wants to implement it. This skill covers helper
  structure, constants destructuring, Redis-first patterns, exit conventions, SQS error logging,
  and file/calling-name conventions. Use sailsjs-api instead when a full controller action, route,
  and validation is also needed.
---

# Sails.js Helper Creator

Creates a single, production-ready Sails.js helper file at `api/helpers/your-helper-name.js`.

---

## Workflow

### Step 1 — Understand the helper

Ask the user (or extract from conversation):

- **What does this helper do?** (one sentence)
- **What inputs does it need?** (names, types, required/optional)
- **What does it return on success?** (`true/false`, a record, a token, structured data?)
- **Does it call any external APIs?** (Zoom, Twilio, AWS, etc.)
- **Does it read/write to the DB or Redis cache?**
- **What service/queue is used for error logging?** (needed for the catch block)

Then ask the user to share their `sails.config.constants` file (or the relevant section), so you can:
- Reuse existing constant keys (URLs, status codes, queue names, etc.)
- Never hardcode values that already exist in constants

---

### Step 2 — Write the Helper

Follow the structure below precisely. Read `references/helper-guide.md` for deep detail and edge-case patterns.

#### File skeleton

```javascript
const {
  // Only destructure what this helper actually uses
  SQSTypes,
  SQSEvents,
  Queues,
  // e.g. AXIOS, ZoomUrls, OnlineMeetingUserStatus, etc.
} = sails.config.constants;

module.exports = {
  friendlyName: 'Human Readable Name',
  description: 'One sentence description.',

  inputs: {
    inputName: {
      type: 'string',    // string | number | boolean | json | ref
      required: true,
    },
  },

  exits: {
    success: {
      description: 'What success means.',
    },
  },

  fn: async function (inputs, exits) {
    try {
      let { inputName } = inputs;

      // ... logic here ...

      return exits.success(result);
    } catch (err) {
      let catchData = {
        serviceName: 'ServiceName',
        api: 'Helper.helperName',
        errorDetail: err,
      };
      await sails.helpers.sendMessage(
        SQSTypes.Error,
        SQSEvents.CatchError,
        catchData,
        Queues.NotificationQueue
      );
      return exits.success(false);
    }
  },
};
```

---

### Step 3 — Apply Patterns

Based on what the helper does, apply the relevant patterns from the table below.
Read `references/helper-guide.md` for full code for each pattern.

| Helper does | Pattern to apply |
|---|---|
| Fetches cached data (Redis) | Redis-first |
| Generates / refreshes a token | Token with refresh loop |
| Calls an external HTTP API | AXIOS call with status check |
| Reads from the database | DB query with isDeleted guard |
| Writes / updates the database | DB update + cache invalidation |
| Sends a message to SQS | SQS send pattern |
| Has retryable steps | Retry loop with attempt counter |

---

### Step 4 — Output Checklist

Before presenting the final file, verify:

- [ ] Constants destructured at top (nothing from `sails.config.constants` used inline)
- [ ] `friendlyName` and `description` filled in
- [ ] All inputs have `type` and `required` declared
- [ ] No hardcoded queue names, URLs, status codes, or error strings
- [ ] Redis checked before DB (if applicable)
- [ ] External API uses `AXIOS` from constants (not a fresh `require`)
- [ ] Every code path ends in `exits.success(...)` — no bare `return` without `exits`
- [ ] Catch block: SQS log then `exits.success(false)`
- [ ] File name is kebab-case; calling name is the camelCase equivalent

---

### Step 5 — Present Output

Output the helper in a single labeled code block:

```
// --- Helper (api/helpers/helper-name.js) ---
```

Then add a **"Calling convention"** note showing exactly how to invoke it from a controller or another helper:

```javascript
// Boolean result
let success = await sails.helpers.helperName.with({ inputKey: value });

// Data result
let tokenData = await sails.helpers.helperName.with({ inputKey: value });
if (!tokenData) { /* handle failure */ }
```

And a **"Constants to add"** note if any new keys need to be added to `sails.config.constants`.

---

## Reference Files

- `references/helper-guide.md` — All patterns in full detail (Redis, token refresh, AXIOS, DB, SQS, retry loops)
