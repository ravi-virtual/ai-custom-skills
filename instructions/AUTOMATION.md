# AUTOMATION.md — Automation Framework

## Purpose
Defines all automation scripts, scheduled tasks, background jobs, and automated workflows used in the system.

---

## Automation Categories

| Category | Type | Trigger |
|---|---|---|
| Data Cleanup | Scheduled job | Daily/Weekly cron |
| Email Notifications | Event-driven | User action |
| Token Management | Event-driven | Expiry events |
| Health Checks | Scheduled | Every 5 minutes |
| Backup | Scheduled | Daily |
| Report Generation | Scheduled | Weekly |
| AI Content Queue | Queue-based | On demand + retry |

---

## Section 1: Scheduled Jobs

### Job 1: Soft-Deleted Record Cleanup

Permanently remove records soft-deleted more than 90 days ago (after data retention policy allows).

```javascript
// scripts/jobs/cleanupDeleted.js
'use strict';

const mongoose = require('mongoose');
const User = require('../src/models/User');
const Profile = require('../src/models/Profile');
const { config } = require('../src/config/constants');

const RETENTION_DAYS = 90;

const cleanupDeleted = async () => {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - RETENTION_DAYS);

  console.log(JSON.stringify({
    level: 'info',
    message: 'Starting deleted record cleanup',
    cutoffDate: cutoffDate.toISOString(),
  }));

  try {
    await mongoose.connect(config.MONGO_URI);

    const [userResult, profileResult] = await Promise.all([
      User.deleteMany({ isDeleted: true, updatedAt: { $lt: cutoffDate } }),
      Profile.deleteMany({ isDeleted: true, updatedAt: { $lt: cutoffDate } }),
    ]);

    console.log(JSON.stringify({
      level: 'info',
      message: 'Cleanup complete',
      usersDeleted: userResult.deletedCount,
      profilesDeleted: profileResult.deletedCount,
    }));
  } finally {
    await mongoose.disconnect();
  }
};

cleanupDeleted().catch((err) => {
  console.error(JSON.stringify({ level: 'error', message: err.message }));
  process.exit(1);
});
```

### Job 2: Expired Token Cleanup

```javascript
// scripts/jobs/cleanupExpiredTokens.js
// If storing refresh tokens in DB (optional pattern):
await RefreshToken.deleteMany({
  expiresAt: { $lt: new Date() }
});
```

### Cron Schedule Configuration

```javascript
// Using node-cron (npm install node-cron)
const cron = require('node-cron');

// Daily at 2:00 AM
cron.schedule('0 2 * * *', () => {
  require('./jobs/cleanupDeleted');
});

// Every 5 minutes: health check ping
cron.schedule('*/5 * * * *', () => {
  // Ping internal health endpoint
});
```

---

## Section 2: Event-Driven Automation

### Email Automation (Nodemailer)

```javascript
// src/services/emailService.js
'use strict';

const nodemailer = require('nodemailer');
const { config } = require('../config/constants');

const transporter = nodemailer.createTransport({
  service: 'gmail',  // Or use SMTP config
  auth: {
    user: config.EMAIL_USER,
    pass: config.EMAIL_PASS,
  },
});

/**
 * @name sendEmail
 * @file emailService.js
 * @param {Object} options - { to, subject, html }
 * @description Sends a transactional email
 */
const sendEmail = async ({ to, subject, html }) => {
  try {
    await transporter.sendMail({
      from: `"${config.APP_NAME}" <${config.EMAIL_FROM}>`,
      to,
      subject,
      html,
    });
    console.log(JSON.stringify({ level: 'info', message: 'Email sent', to, subject }));
  } catch (err) {
    console.error(JSON.stringify({ level: 'error', message: 'Email failed', to, error: err.message }));
    throw err; // Let caller handle
  }
};

module.exports = { sendEmail };
```

### Email Templates

```javascript
// src/services/emailTemplates.js
const welcomeEmail = (name) => ({
  subject: 'Welcome to ProfilePro!',
  html: `
    <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
      <h1>Welcome, ${name}!</h1>
      <p>Your account is ready. Start creating your AI-powered profile today.</p>
      <a href="${process.env.FRONTEND_URL}/dashboard" 
         style="background: #6366f1; color: white; padding: 12px 24px; 
                border-radius: 8px; text-decoration: none;">
        Get Started
      </a>
    </div>
  `
});

const passwordResetEmail = (name, resetUrl) => ({
  subject: 'Reset Your Password',
  html: `
    <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
      <h1>Password Reset Request</h1>
      <p>Hi ${name}, click below to reset your password. This link expires in 1 hour.</p>
      <a href="${resetUrl}" style="background: #6366f1; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none;">
        Reset Password
      </a>
      <p style="color: #94a3b8; font-size: 12px;">If you didn't request this, ignore this email.</p>
    </div>
  `
});

module.exports = { welcomeEmail, passwordResetEmail };
```

---

## Section 3: AI Generation Queue

### Queue Pattern (Without Redis)

For the current scale, use in-memory promise-based queuing:

```javascript
// src/services/generationQueue.js
'use strict';

class GenerationQueue {
  constructor(concurrency = 3) {
    this.queue = [];
    this.running = 0;
    this.concurrency = concurrency;
  }

  add(task) {
    return new Promise((resolve, reject) => {
      this.queue.push({ task, resolve, reject });
      this.run();
    });
  }

  async run() {
    while (this.running < this.concurrency && this.queue.length > 0) {
      const { task, resolve, reject } = this.queue.shift();
      this.running++;
      try {
        const result = await task();
        resolve(result);
      } catch (err) {
        reject(err);
      } finally {
        this.running--;
        this.run();
      }
    }
  }
}

module.exports = new GenerationQueue(3); // Max 3 concurrent AI calls
```

### Usage in Controller
```javascript
const generationQueue = require('../services/generationQueue');

const generateContent = async (req, res) => {
  try {
    const result = await generationQueue.add(() =>
      aiService.generate(req.body.prompt)
    );
    return new ApiResponse(ResponseCodes.OK, 'Generated', { content: result }).send(res);
  } catch (err) {
    return sendError(res, { statusCode: ResponseCodes.SERVER_ERROR, message: err.message, code: ErrorCodes.SERVER_ERROR });
  }
};
```

---

## Section 4: Automation Scripts

### Script: Create Admin User
```bash
# Run once after deployment to create initial admin
node scripts/createAdmin.js
```

### Script: Database Seed (Development)
```bash
# Seed development database with test data
node scripts/seed.js
```

### Script: Audit Debug Logs
```powershell
# Find any remaining debug logs before deployment (Windows)
Select-String -Path "backend\src\**\*.js" -Pattern "// \[DEBUG\]" -Recurse
Select-String -Path "frontend\src\**\*.jsx" -Pattern "// \[DEBUG\]" -Recurse
```

### Script: Count Soft-Deleted Records
```javascript
// scripts/auditDeleted.js
const counts = await Promise.all([
  User.countDocuments({ isDeleted: true }),
  Profile.countDocuments({ isDeleted: true }),
]);
console.log({ deletedUsers: counts[0], deletedProfiles: counts[1] });
```

---

## Automation Rules

| Rule | Rationale |
|---|---|
| All scripts use try/catch + process.exit(1) on failure | Scripts must fail loudly, not silently |
| Scripts connect and disconnect their own DB session | Never share a DB connection with the main app |
| Scheduled jobs log start, end, and counts | Enables audit trail and anomaly detection |
| Email failures throw (not swallow) | Caller decides whether to retry |
| Queue concurrency is capped | Prevents overwhelming the AI rate limits |
