# Controller Action Template

Full annotated template for a Sails.js controller action.

```javascript
/**
 * @name <actionName>
 * @file <ControllerName>.js
 * @param {Request} req
 * @param {Response} res
 * @description <One-line description of what this action does>
 * @for <Panel/App names, e.g. "Agent Panel, Agent App">
 * @author <Author Name> (<Company>)
 */
<actionName>: async (req, res) => {
  try {
    // ── 1. Assemble input data ────────────────────────────────────────────────
    let data = {
      <field1>: req.body.<field1>,
      <field2>: req.headers.<HeaderName>?.<prop>,
      eventCode: Events.<EVENT_CODE>,
      lang: req.headers.lang || Language.English,
    };

    req.setLocale(data.lang);

    // ── 2. Validate inputs ────────────────────────────────────────────────────
    let result = await <ModelName>.validateData(data);
    if (result.hasError) {
      return res.badRequest({
        status: ResponseCodes.BAD_REQUEST,
        data: {},
        message: Object.keys(result.errors).length + ' error(s) found.',
        errorCode: '',
        error: result.errors,
      });
    }

    // ── 3. Redis-first data fetch ─────────────────────────────────────────────
    let <record> = await sails.helpers.getCache(<cacheKey>);

    // Fall back to DB if not cached
    if (!<record>) {
      <record> = await <ModelName>.findOne({
        id: data.<id>,
        isDeleted: false,
      });

      if (!<record>) {
        return res.badRequest({
          status: ResponseCodes.BAD_REQUEST,
          message: req.i18n.__('<I18N_KEY_NOT_FOUND>'),
          data: {},
        });
      }
    }

    // ── 4. Authorization check (if needed) ────────────────────────────────────
    let isValidAgent = await sails.helpers.isValidAgent.with({
      userDataId: data.agentId,
      paramsId: <record>.<ownerField>,
    });

    if (!isValidAgent) {
      return res.status(ResponseCodes.UNAUTHORIZED).json({
        status: ResponseCodes.UNAUTHORIZED,
        message: req.i18n.__('ACCESS_DENIED'),
        data: {},
      });
    }

    // ── 5. Core business logic via helper ─────────────────────────────────────
    let <helperResult> = await sails.helpers.<helperName>.with({
      <input1>: data.<field1>,
    });

    if (!<helperResult>) {
      return res.badRequest({
        status: ResponseCodes.BAD_REQUEST,
        message: req.i18n.__('<I18N_KEY_FAILURE>'),
        data: {},
      });
    }

    // ── 6. Success response ───────────────────────────────────────────────────
    return res.ok({
      status: ResponseCodes.OK,
      message: '',
      data: {},  // or { <record> } if returning data
    });

  } catch (err) {
    // ── 7. Catch block — log to SQS, return 500 ───────────────────────────────
    let catchData = {
      serviceName: '<ServiceName>',
      api: 'v1/<ControllerName>.<actionName>',
      errorDetail: err,
    };
    await sails.helpers.sendMessage(
      SQSTypes.Error,
      SQSEvents.CatchError,
      catchData,
      Queues.NotificationQueue
    );
    return res.serverError({
      status: ResponseCodes.SERVER_ERROR,
      data: {},
      message: '',
      errorCode: '',
      error: err,
    });
  }
},
```

## Constant destructuring at the top of the controller file

Add these at the top of the controller file (outside the `module.exports`):

```javascript
const {
  ResponseCodes,
  Language,
  Events,
  TicketType,
  TicketStatus,
  SQSTypes,
  SQSEvents,
  Queues,
  // ...any others used in this controller
} = sails.config.constants;
```

## Notes

- `req.headers.<HeaderName>` — Sails middlewares often parse JWT/session data and inject structured objects into headers. Use `?.` for safety.
- `req.i18n.__('KEY')` — all user-facing strings go through i18n. Never hardcode message strings.
- Always include `isDeleted: false` in any `findOne` / `find` query unless explicitly querying soft-deleted records.
- The `data` object pattern ensures all inputs are validated before use and makes the code easier to read and test.
