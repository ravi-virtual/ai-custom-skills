# Sails.js Helper — Pattern Guide

All common helper patterns with full annotated code examples.

---

## 1. File & Calling-Name Convention

| File path | Called as |
|---|---|
| `api/helpers/terminate-meeting.js` | `sails.helpers.terminateMeeting` |
| `api/helpers/generate-zoom-account-token.js` | `sails.helpers.generateZoomAccountToken` |
| `api/helpers/is-valid-agent.js` | `sails.helpers.isValidAgent.with({ ... })` |
| `api/helpers/get-cache.js` | `sails.helpers.getCache(key)` |
| `api/helpers/send-message.js` | `sails.helpers.sendMessage(type, event, data, queue)` |

Sails automatically converts kebab-case filenames → camelCase helper names.

---

## 2. Redis-First Pattern

Use when the helper needs data that might be cached.

```javascript
// Try cache first
let cachedData = await sails.helpers.getCache('<cache_key>');
let value = cachedData?.<field>;

// Fall back to DB or external source
if (!value) {
  value = await <generateOrFetch>();
}

// Still nothing? Bail out.
if (!value) {
  return exits.success(false);
}
```

Cache a new value after generating it:
```javascript
await sails.helpers.setCache('<cache_key>', { <field>: value, expiresAt: Date.now() + 3600000 });
```

---

## 3. Token with Refresh Loop

Use when calling an external API that may return a 401 and need a fresh token.

```javascript
let tokenRefreshAttempts = 0;

while (tokenRefreshAttempts < 2) {
  let apiResponse = await AXIOS({
    method: 'POST',
    url: `${ZoomUrls.BASE}/${ZoomUrls.END_MEETING}/${meetingId}`,
    headers: { Authorization: `Bearer ${zoomAccountToken}` },
    validateStatus: () => true,   // don't throw on non-2xx
  });

  // Token expired — refresh once and retry
  if (apiResponse.status === ZoomStatusCodes.TOKEN_EXPIRED) {
    zoomAccountToken = await sails.helpers.generateZoomAccountToken();
    tokenRefreshAttempts++;
    continue;
  }

  // Success
  if (apiResponse.status === ZoomStatusCodes.SUCCESS || apiResponse.status === ZoomStatusCodes.NO_CONTENT) {
    break;
  }

  // Unrecoverable error
  return exits.success(false);
}
```

---

## 4. AXIOS External API Call

Always use `AXIOS` from `sails.config.constants`, not a raw `require('axios')`.

```javascript
const { AXIOS, SomeUrls, SomeStatusCodes } = sails.config.constants;

let response = await AXIOS({
  method: 'GET',                              // GET | POST | PUT | PATCH | DELETE
  url: `${SomeUrls.BASE}/${SomeUrls.ENDPOINT}`,
  headers: {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  data: { key: value },                       // for POST/PUT/PATCH body
  params: { queryParam: value },              // for GET query string
  validateStatus: () => true,                 // handle non-2xx manually
});

if (response.status !== SomeStatusCodes.OK) {
  return exits.success(false);
}

let responseData = response.data;
```

---

## 5. DB Query with isDeleted Guard

Always include `isDeleted: false` unless explicitly querying deleted records.

```javascript
// Single record
let record = await ModelName.findOne({
  id: recordId,
  isDeleted: false,
});
if (!record) {
  return exits.success(false);  // or true if "not found" is an acceptable outcome
}

// Multiple records
let records = await ModelName.find({
  status: StatusConstant.Active,
  isDeleted: false,
}).sort('createdAt DESC');

// With populate
let record = await ModelName.findOne({ id: recordId, isDeleted: false })
  .populate('<associationName>');
```

---

## 6. DB Update + Cache Invalidation

After updating a record, invalidate or refresh the cache.

```javascript
// Update
await ModelName.updateOne({ id: recordId }).set({
  <field>: newValue,
  updatedAt: new Date(),
});

// Invalidate cache so next read gets fresh data
await sails.helpers.deleteCache(<cacheKey>);
// Or refresh it immediately:
// await sails.helpers.setCache(<cacheKey>, updatedData);
```

---

## 7. SQS Send Pattern

Send a message to an SQS queue (for notifications, events, errors, etc.).

```javascript
const { SQSTypes, SQSEvents, Queues } = sails.config.constants;

// Notification / domain event
await sails.helpers.sendMessage(
  SQSTypes.Notification,
  SQSEvents.MeetingTerminated,
  { ticketId, agentId },
  Queues.NotificationQueue
);

// Error event (catch block)
await sails.helpers.sendMessage(
  SQSTypes.Error,
  SQSEvents.CatchError,
  { serviceName: 'Queue', api: 'Helper.<helperName>', errorDetail: err },
  Queues.NotificationQueue
);
```

---

## 8. Retry Loop with Attempt Counter

Use for any operation that may transiently fail and is safe to retry.

```javascript
const MAX_ATTEMPTS = 3;
let attempts = 0;
let success = false;

while (attempts < MAX_ATTEMPTS) {
  try {
    let result = await someOperation();
    if (result) {
      success = true;
      break;
    }
  } catch (retryErr) {
    // Log individual retry failures silently or at debug level
  }
  attempts++;
  await new Promise(r => setTimeout(r, 500 * attempts));  // backoff
}

if (!success) {
  return exits.success(false);
}
```

---

## 9. Input Types Reference

| Sails type | JS equivalent | Notes |
|---|---|---|
| `'string'` | String | Use for IDs, names, tokens |
| `'number'` | Number | Integers and floats |
| `'boolean'` | Boolean | true/false flags |
| `'json'` | Any JSON-serializable | Objects, arrays |
| `'ref'` | Any JS value | Dates, Buffers, class instances |

---

## 10. Exits Reference

```javascript
exits: {
  success: {
    description: 'Returns result data or true/false.',
  },
  // Custom exits (use sparingly — prefer exits.success(false) for errors)
  notFound: {
    description: 'The record was not found.',
    responseType: 'notFound',
  },
  invalid: {
    description: 'Input was invalid.',
    responseType: 'badRequest',
  },
},

// Usage:
return exits.notFound();
return exits.invalid({ field: 'error message' });
```

> ⚠️ Custom exits propagate exceptions to the caller. For most helpers, `exits.success(false)` is safer and keeps error handling localized.

---

## 11. Full Working Example — generateZoomAccountToken

```javascript
const {
  AXIOS,
  SQSTypes,
  SQSEvents,
  Queues,
  ZoomUrls,
  ZoomCreateMeetingData,
} = sails.config.constants;

module.exports = {
  friendlyName: 'Generate Zoom Account Token',
  description: 'Fetch a new Zoom server-to-server OAuth token and cache it.',

  inputs: {},

  exits: {
    success: {
      description: 'Returns the token string, or false on failure.',
    },
  },

  fn: async function (inputs, exits) {
    try {
      let response = await AXIOS({
        method: 'POST',
        url: ZoomUrls.ACCOUNT_TOKEN,
        headers: {
          Authorization: `Basic ${ZoomCreateMeetingData.ENCODED_KEY}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        data: 'grant_type=account_credentials&account_id=' + ZoomCreateMeetingData.ACCOUNT_ID,
        validateStatus: () => true,
      });

      if (!response?.data?.access_token) {
        return exits.success(false);
      }

      let token = response.data.access_token;

      // Cache for slightly less than the expiry window
      await sails.helpers.setCache('zoom_account_token', {
        token,
        cachedAt: Date.now(),
      });

      return exits.success(token);
    } catch (err) {
      let catchData = {
        serviceName: 'Queue',
        api: 'Helper.generateZoomAccountToken',
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
