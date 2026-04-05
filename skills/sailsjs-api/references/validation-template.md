# Model Validation Template

Full annotated template for the `validateData` static method on a Sails model or its companion events file.

## Location options

| Approach | File |
|---|---|
| Inline in model | `api/models/<ModelName>.js` — add to `module.exports` |
| Companion events file | `api/models/<ModelName>Events.js` — separate file, same shape |

Use a companion events file when the model already has many static methods and readability would suffer.

---

## Template

```javascript
const { Events, Validator, SanitizeHtml } = sails.config.constants;

// Inside module.exports = { ... } or as a standalone export object:

/**
 * @name validateData
 * @file <ModelName>Events.js (or <ModelName>.js)
 * @param eventData
 * @description Validates input data for <ModelName> operations
 * @author <Author Name>
 */
validateData: (eventData) => {
  let data;
  let rules;
  let result = {};

  switch (eventData.eventCode) {

    // ── Existing cases ────────────────────────────────────────────────────────
    case Events.<EXISTING_EVENT_CODE>: {
      data = {
        <field>: eventData.<field>,
      };
      rules = {
        <field>: 'required|string',
      };
      break;
    }

    // ── NEW case added for this API ───────────────────────────────────────────
    case Events.<NEW_EVENT_CODE>: {
      data = {
        <field1>: eventData.<field1>,
        <field2>: eventData.<field2>,
      };
      rules = {
        <field1>: 'required|string',
        <field2>: 'required|integer',
      };
      break;
    }

    default: {
      result['hasError'] = true;
      result['errors'] = 'Invalid Event Code';
      return result;
    }
  }

  // ── Run validation ────────────────────────────────────────────────────────
  let validation = new Validator(data, rules);

  if (validation.passes()) {
    result['hasError'] = false;
  }
  if (validation.fails()) {
    result['hasError'] = true;
    result['errors'] = validation.errors.all();
  }
  return result;
},
```

---

## Validatorjs rule reference

| Rule | Example |
|---|---|
| Required string | `'required\|string'` |
| Required integer | `'required\|integer'` |
| Required email | `'required\|email'` |
| Required boolean | `'required\|boolean'` |
| Optional string | `'string'` |
| Integer with min | `'required\|integer\|min:1'` |
| Max length | `'required\|string\|max:255'` |
| Array | `'required\|array'` |
| In set of values | `'required\|in:active,inactive,pending'` |

---

## Adding a new Events constant

When you add a new `case Events.<NEW_EVENT_CODE>`, you **must** also add the constant to `sails.config.constants`. Tell the user to add this to their constants file:

```javascript
// In config/constants.js (or wherever Events is defined)
Events: {
  // ... existing events ...
  <NEW_EVENT_CODE>: '<NEW_EVENT_CODE>',  // e.g. VALIDATE_DATA_FOR_<ACTION>
},
```

**Naming convention:** `VALIDATE_DATA_FOR_<ACTION>` — e.g. `VALIDATE_DATA_FOR_TERMINATE_MEETING`

---

## SanitizeHtml usage (when applicable)

Use `SanitizeHtml` for any string fields that may contain user-generated HTML or rich text:

```javascript
case Events.VALIDATE_DATA_WITH_HTML: {
  data = {
    content: SanitizeHtml(eventData.content, { allowedTags: [] }),
    title: eventData.title,
  };
  rules = {
    content: 'required|string',
    title: 'required|string|max:200',
  };
  break;
}
```
