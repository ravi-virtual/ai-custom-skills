# DEPLOYMENT.md — Deployment Guide

## Overview
This guide covers deploying the MERN stack application from local development through staging to production.

---

## Environment Overview

| Environment | Purpose | Deployment Trigger |
|---|---|---|
| Development | Local development | `npm run dev` |
| Staging | Testing before production | Manual trigger |
| Production | Live user-facing | Manual approval |

---

## Local Development Setup

### Prerequisites
```bash
Node.js 20.x LTS
MongoDB 7.x (local or Atlas)
npm 10.x
```

### First-Time Setup
```bash
# 1. Clone the repository
git clone <repo-url>

# 2. Setup backend
cd backend
npm install
cp .env.example .env
# Fill in .env values

# 3. Setup frontend
cd ../frontend
npm install
cp .env.example .env
# Fill in .env values

# 4. Start MongoDB (if local)
mongod --dbpath /data/db

# 5. Start backend
cd ../backend
npm run dev    # Starts on port 5000

# 6. Start frontend (new terminal)
cd ../frontend
npm run dev    # Starts on port 5173
```

### Environment Variables (Backend `.env`)
```bash
PORT=5000
NODE_ENV=development
MONGO_URI=mongodb://localhost:27017/appname
JWT_SECRET=minimum-32-character-random-secret
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=another-minimum-32-char-secret
JWT_REFRESH_EXPIRES_IN=15m
CORS_ORIGIN=http://localhost:5173

# AI Services
GEMINI_API_KEY=your-gemini-api-key
GROK_API_KEY=your-grok-api-key
OPENAI_API_KEY=your-openai-api-key
```

### Environment Variables (Frontend `.env`)
```bash
VITE_API_BASE_URL=http://localhost:5000
```

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing: `npm test`
- [ ] No ESLint errors: `npm run lint`
- [ ] No debug logs in codebase: `grep -r "// \[DEBUG\]" src/`
- [ ] No hardcoded credentials in any file
- [ ] CODING_STANDARDS.md checklist complete

### Security
- [ ] All SECURITY.md checklist items verified
- [ ] Helmet middleware active
- [ ] CORS restricted to production domain only
- [ ] Rate limiting configured for production
- [ ] JWT secrets are 32+ characters of random data
- [ ] No sensitive data in API responses (tested with Postman)

### Performance
- [ ] Database indexes created (verify with `db.collection.getIndexes()`)
- [ ] Bundle size within budget: `npm run build` → check dist size
- [ ] API response times within budget (PERFORMANCE.md)

---

## Production Environment Variables

```bash
# backend/.env.production
PORT=5000
NODE_ENV=production
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/appname?retryWrites=true&w=majority
JWT_SECRET=<64-char random string>
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=<another 64-char random string>
JWT_REFRESH_EXPIRES_IN=15m
CORS_ORIGIN=https://yourdomain.com

GEMINI_API_KEY=<production key>
GROK_API_KEY=<production key>
OPENAI_API_KEY=<production key>
```

```bash
# frontend/.env.production
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## Build Process

### Backend (Production)
```bash
cd backend
# Backend runs directly with Node — no build step
# Use PM2 for process management:
npm install -g pm2
pm2 start src/server.js --name "app-backend"
pm2 save
pm2 startup
```

### Frontend (Production Build)
```bash
cd frontend
npm run build    # Outputs to dist/ folder

# Serve with static hosting or Nginx:
# dist/ folder contains index.html + assets/
```

---

## Deployment Targets

### Option A: Render.com (Recommended for Solo/Small Teams)
```yaml
# Backend Web Service:
Runtime: Node
Build Command: npm install
Start Command: node src/server.js
Environment: Set all env vars in dashboard

# Frontend Static Site:
Build Command: npm run build
Publish Directory: dist
```

### Option B: Railway
```yaml
# Backend:
Start Command: npm start
Root Directory: backend/

# Frontend:
Root Directory: frontend/
Build Command: npm run build
Output Directory: dist/
```

### Option C: VPS (Ubuntu + Nginx + PM2)
```nginx
# /etc/nginx/sites-available/app
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /var/www/app/frontend/dist;
        try_files $uri /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Database Deployment

### MongoDB Atlas Setup
1. Create cluster on MongoDB Atlas (free tier: M0)
2. Create database user with password
3. Add IP whitelist (0.0.0.0/0 for cloud deployment, or specific server IPs)
4. Get connection string and update `MONGO_URI` env var

### Initial Data Migration
```javascript
// If needed: create admin user script
// scripts/createAdmin.js
require('dotenv').config();
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const User = require('./src/models/User');
const { config } = require('./src/config/constants');

mongoose.connect(config.MONGO_URI).then(async () => {
  const hash = await bcrypt.hash('adminPassword123!', 10);
  await User.create({
    _id: uuidv4(),
    name: 'Admin',
    email: 'admin@yourdomain.com',
    password: hash,
    role: 'admin'
  });
  console.log('Admin created');
  process.exit(0);
});
```

---

## Rollback Procedure
If a deployment fails:
1. Identify the last known good commit: `git log --oneline -10`
2. Revert: `git revert HEAD` or `git checkout <commit-hash>`
3. Redeploy the reverted version
4. Document the failure in FAILURES.md

---

## Post-Deployment Verification
After every deployment:
- [ ] Health check endpoint responds: `GET /api/health` → 200
- [ ] Login flow works end-to-end
- [ ] Core feature (profile creation/generation) works
- [ ] No error logs in production monitoring
- [ ] Response times within PERFORMANCE.md budgets
