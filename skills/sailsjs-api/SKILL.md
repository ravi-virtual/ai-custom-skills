---
name: sailsjs-api
description: >
  Use this skill whenever the user wants to create a new API endpoint in Sails.js. Triggers include:
  any mention of "create API", "new endpoint", "add route", "controller action", "sails API", or
  requests to add new functionality to a Sails.js backend. This skill covers the FULL flow:
  controller action, sails helper, model validation, route registration, and policy setup.
  Always use this skill when the user wants a complete Sails.js API with all its supporting pieces,
  even if they only mention "add an API" or "create an endpoint". Do NOT use for helper-only tasks
  (use sailsjs-helper instead).
---

# Sails.js API Creator

Creates a **complete, production-ready** Sails.js API endpoint covering all five layers:

1. **Controller Action** — the request handler
2. **Sails Helper** — reusable business logic
3. **Model Validation** — event-driven input validation
4. **Route** — `config/routes.js` entry
5. **Policy** — `config/policies.js` entry

---

## Workflow

### Step 1 — Gather Context

Before writing anything, ask the user (or extract from conversation):

- What does the API do? (e.g., "terminate a meeting", "create a ticket")
- Which **controller file** does it belong to?
- Which **model** is the primary data model?
- What **request inputs** are needed? (`req.body`, `req.headers`, `req.params`)
- Does it need an accompanying **helper**? (almost always yes for non-trivial logic)
- Which **policies** should protect it? (e.g., `isAuthenticated`, `isAgent`)
- What **HTTP method** and **path**? (e.g., `POST /api/v1/meeting/terminate`)

Then check: does `sails.config.constants` already define relevant keys?  
→ Read the constants file (ask the user for its path if not provided) and **reuse any existing constant keys** — never hardcode strings that already live in constants.

---

### Step 2 — Controller Action

Follow this exact structure. Read `references/controller-template.md` for the full annotated template.

**Key rules:**
- JSDoc header with `@name`, `@file`, `@param`, `@description`, `@for`, `@author`
- Extract inputs into a `data` object at the top (never inline `req.body.x` deeper in the function)
- Set locale early: `req.setLocale(data.lang)`
- Always call `Model.validateData(data)` before any DB/cache work
- Use `sails.helpers.getCache()` before DB queries (Redis-first pattern)
- All `res.*` responses use the standardized shape: `{ status, data, message, errorCode?, error? }`
- Catch block: send to SQS error queue via `sails.helpers.sendMessage`, then `res.serverError`
- Pull `ResponseCodes`, `Language`, `Events`, `TicketType`, `TicketStatus`, `SQSTypes`, `SQSEvents`, `Queues`, etc. from `sails.config.constants` — never hardcode values

**Response codes** (always from constants):
```
ResponseCodes.OK          → 200
ResponseCodes.BAD_REQUEST → 400
ResponseCodes.UNAUTHORIZED→ 401
ResponseCodes.SERVER_ERROR→ 500
```

**Standard error shapes:**
```js
// 400
res.badRequest({ status: ResponseCodes.BAD_REQUEST, data: {}, message: '...', errorCode: '', error: result.errors })

// 401
res.status(ResponseCodes.UNAUTHORIZED).json({ status: ResponseCodes.UNAUTHORIZED, message: req.i18n.__('ACCESS_DENIED'), data: {} })

// 500 (catch block only)
res.serverError({ status: ResponseCodes.SERVER_ERROR, data: {}, message: '', errorCode: '', error: err })
```

---

### Step 3 — Sails Helper

Read `references/helper-template.md` for the full annotated template.

**Key rules:**
- Destructure all needed constants at the top: `const { AXIOS, SQSTypes, ... } = sails.config.constants;`
- Define `friendlyName`, `description`, `inputs` (with `type` + `required`), `exits.success`
- Business logic inside `fn: async function(inputs, exits)`
- Redis-first pattern for any cached data
- On any internal error, log to SQS then `return exits.success(false)` — **never throw out of a helper**
- Happy path ends with `return exits.success(<result>)`
- The helper filename (camelCase) must match the way it's called: `sails.helpers.myHelperName`

---

### Step 4 — Model Validation

Add a `validateData` static method to the primary model (or its companion `Events` file).

Read `references/validation-template.md` for the full annotated template.

**Key rules:**
- Destructure `{ Events, Validator, SanitizeHtml }` from `sails.config.constants`
- Use a `switch` on `eventData.eventCode`
- Each case defines `data` (the fields to validate) and `rules` (validatorjs-style rules)
- Add the new event code constant to the `Events` constant object if it doesn't exist
- `default` case sets `result.hasError = true` with `'Invalid Event Code'`
- Return `{ hasError: false }` on pass, `{ hasError: true, errors: validation.errors.all() }` on fail

**Common validatorjs rules:**
```
required|string
required|integer
required|email
required|boolean
string          (optional string)
integer|min:1
```

---

### Step 5 — Route

Add to `config/routes.js`:

```js
'POST /api/v1/<resource>/<action>': {
  controller: '<ControllerName>',
  action: '<actionName>',
  policy: ['<PolicyName>'],   // if policies are separate from policies.js mapping
},
```

Or the shorthand used in many Sails apps:

```js
'POST /api/v1/<resource>/<action>': '<ControllerName>.<actionName>',
```

---

### Step 6 — Policy

Add to `config/policies.js` under the correct controller key:

```js
ControllerName: {
  actionName: ['isAuthenticated', 'isAgent'],  // use whatever policies apply
},
```

---

### Step 7 — Output Checklist

Before presenting the final output, verify:

- [ ] JSDoc header on the controller action
- [ ] All constants imported from `sails.config.constants` (no hardcoded strings/numbers)
- [ ] `data` object assembled at top of controller
- [ ] `validateData` called with correct `eventCode`
- [ ] Redis cache checked before DB query
- [ ] All `res.*` calls use standard shape
- [ ] Catch block sends to SQS and returns `serverError`
- [ ] Helper destructures constants at top
- [ ] Helper never throws — always `exits.success(false)` on error
- [ ] New event code added to Events constants (note this to the user)
- [ ] `validateData` case added to the model
- [ ] Route added to `config/routes.js`
- [ ] Policy added to `config/policies.js`

---

## Output Format

Present output in this order, each in its own labeled code block:

1. `// --- Controller Action (ControllerName.js) ---`
2. `// --- Helper (api/helpers/helperName.js) ---`
3. `// --- Model Validation (api/models/ModelName.js or ModelNameEvents.js) ---`
4. `// --- Route (config/routes.js) ---`
5. `// --- Policy (config/policies.js) ---`
6. A short **"What to add to constants"** note listing any new keys the user must add to `sails.config.constants`

---

## Reference Files

- `references/controller-template.md` — Full annotated controller action template
- `references/helper-template.md` — Full annotated helper template
- `references/validation-template.md` — Full annotated model validation template
