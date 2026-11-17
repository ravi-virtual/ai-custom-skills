# Mongoose & PostgreSQL Models

Part of the `backend-expressjs` skill. Read this when the task touches the topics below.

## Contents
- [Mongoose Model (UUID `_id`)](#mongoose-model-uuid-id)
- [PostgreSQL Schema (if used)](#postgresql-schema-if-used)

## Mongoose Model (UUID `_id`)

```js
// src/models/User.js
const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { Roles } = require('../config/constants');

const userSchema = new mongoose.Schema(
  {
    _id:             { type: String, default: uuidv4 },
    name:            { type: String, required: [true, 'Name is required'], trim: true },
    email:           { type: String, required: [true, 'Email is required'], unique: true, lowercase: true, trim: true, index: true },
    password:        { type: String, required: true, select: false },
    role:            { type: String, enum: Object.values(Roles), default: Roles.USER },
    isAuthenticated: { type: Boolean, default: false },
    isDeleted:       { type: Boolean, default: false },
  },
  {
    timestamps: true,
    _id: false,
    toJSON: {
      transform(doc, ret) {
        delete ret.__v;
        delete ret.password;
      },
    },
  }
);

module.exports = mongoose.model('User', userSchema);
```

### Mongoose Query Rules
- `.lean()` on all read-only queries
- Always include `{ isDeleted: false }` in every find query
- Soft delete only — never `.deleteOne()` on user-facing records
- Indexes defined inline on schema fields
- `password` has `select: false` — add `.select('+password')` only when explicitly needed (e.g. login)

## PostgreSQL Schema (if used)

When PostgreSQL is used, maintain `database/schema.sql` with UUID primary keys.

```sql
-- database/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(100) NOT NULL,
  email             VARCHAR(255) NOT NULL UNIQUE,
  password          VARCHAR(255) NOT NULL,
  role              VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  is_authenticated  BOOLEAN NOT NULL DEFAULT FALSE,
  is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
  created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users(role);
```

> Add a `CREATE TABLE` block per model following the same UUID + `is_deleted` + timestamps pattern. Every table gets its own trigger.
