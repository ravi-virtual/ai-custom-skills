# Sails Helper Template

Full annotated template for a Sails.js helper (`api/helpers/<helperName>.js`).

```javascript
const {
  // Destructure ONLY the constants actually used in this helper
  AXIOS,
  SQSTypes,
  SQSEvents,
  Queues,
  // e.g. ZoomUrls, ZoomStatusCodes, OnlineMeetingUserStatus, etc.
} = sails.config.constants;

module.exports = {
  friendlyName: '<Human Readable Name>',

  description: '<One sentence: what this helper does and for what context.>',

  inputs: {
    <inputName>: {
      type: 'string',   // string | number | boolean | json | ref
      required: true,
    },
    <optionalInput>: {
      type: 'string',
      required: false,
      defaultsTo: '',
    },
  },

  exits: {
    success: {
      description: '<What a successful exit means.>',
    },
  },

  fn: async function (inputs, exits) {
    try {
      let { <inputName> } = inputs;

      // ── 1. Redis-first pattern (for cached resources) ──────────────────────
      let cachedData = await sails.helpers.getCache('<cache_key>');
      let <token> = cachedData?.<field>;

      if (!<token>) {
        <token> = await sails.helpers.<generateSomething>();
      }

      if (!<token>) {
        return exits.success(false);
      }

      // ── 2. Core logic ──────────────────────────────────────────────────────
      // ... your business logic here ...

      // ── 3. DB operations (if needed) ───────────────────────────────────────
      let record = await <ModelName>.findOne({
        <field>: <value>,
        isDeleted: false,
      });

      if (!record) {
        return exits.success(false);  // or true depending on semantics
      }

      // ── 4. External API call (if needed) ───────────────────────────────────
      // Use AXIOS from constants, not direct import
      let response = await AXIOS({
        method: 'POST',
        url: `${<UrlConstant>}/<path>`,
        headers: {
          Authorization: `Bearer ${<token>}`,
          'Content-Type': 'application/json',
        },
        data: { /* ... */ },
      });

      // ── 5. Success ─────────────────────────────────────────────────────────
      return exits.success(true);   // or return exits.success(<data>)

    } catch (err) {
      // ── 6. Catch block — log to SQS, return false (never throw) ───────────
      let catchData = {
        serviceName: '<ServiceName>',
        api: 'Helper.<helperName>',
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

## File naming & calling convention

| File path | How it's called in Sails |
|---|---|
| `api/helpers/terminate-meeting.js` | `sails.helpers.terminateMeeting` |
| `api/helpers/generate-zoom-account-token.js` | `sails.helpers.generateZoomAccountToken` |
| `api/helpers/is-valid-agent.js` | `sails.helpers.isValidAgent.with({ ... })` |

Sails auto-converts kebab-case filenames to camelCase for the helper name.

## Passing inputs

```javascript
// Simple (positional, single input)
let result = await sails.helpers.myHelper(value);

// Named inputs (use .with() for multiple inputs)
let result = await sails.helpers.myHelper.with({
  ticketId: data.ticketId,
  agentId: data.agentId,
});
```

## Return value conventions

| Scenario | Return |
|---|---|
| Boolean success/failure | `exits.success(true)` / `exits.success(false)` |
| Returning data on success | `exits.success({ token, expiresAt })` |
| Record not found (not an error) | `exits.success(null)` or `exits.success(false)` |
| Any caught error | `exits.success(false)` after SQS logging |

## Notes

- **Never** use `return exits.error()` unless you specifically want to propagate an exception to the caller. Prefer `exits.success(false)`.
- **Always** destructure constants at the top of the file — never use `sails.config.constants.<X>` inline.
- **Redis-first**: check cache before any DB query. Use `sails.helpers.getCache` and `sails.helpers.setCache`.
- For token refresh loops (e.g. OAuth tokens), track attempt count and cap retries (e.g. `tokenRefreshAttempts < 2`).
