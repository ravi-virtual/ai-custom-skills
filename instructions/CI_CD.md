# CI_CD.md — CI/CD Pipeline Reference

## Overview
Continuous Integration and Continuous Deployment ensures every code change is automatically tested and verified before it can reach production.

---

## CI/CD Philosophy
- Every push triggers the pipeline — no exceptions
- The pipeline is the gatekeeper — broken builds do not proceed
- Automated checks eliminate human error in pre-deployment verification

---

## Pipeline Stages

### Stage 1: Code Quality
```yaml
name: Code Quality
steps:
  - name: Lint Backend
    command: cd backend && npm run lint
    fail_on_error: true
    
  - name: Lint Frontend
    command: cd frontend && npm run lint
    fail_on_error: true
    
  - name: Check for Debug Logs
    command: grep -r "// \[DEBUG\]" backend/src frontend/src
    fail_if_output: true  # Fail if any debug logs found
    
  - name: Check for Hardcoded Secrets
    command: npm run secrets-check  # Custom script
    fail_on_error: true
```

### Stage 2: Testing
```yaml
name: Testing
steps:
  - name: Backend Unit Tests
    command: cd backend && npm run test:unit
    fail_on_error: true
    
  - name: Backend Integration Tests
    command: cd backend && npm run test:integration
    environment:
      MONGO_URI: mongodb://localhost:27017/test
      NODE_ENV: test
    fail_on_error: true
    
  - name: Frontend Unit Tests
    command: cd frontend && npm test -- --watchAll=false
    fail_on_error: true
    
  - name: Coverage Check
    command: cd backend && npm run test:coverage
    fail_on_threshold: 80  # Fail if coverage drops below 80%
```

### Stage 3: Build
```yaml
name: Build
steps:
  - name: Build Frontend
    command: cd frontend && npm run build
    fail_on_error: true
    
  - name: Verify Build Output
    command: ls frontend/dist/index.html
    fail_if_missing: true
```

### Stage 4: Deploy (Staging)
```yaml
name: Deploy Staging
trigger: push to main branch
steps:
  - name: Deploy Backend
    command: [platform-specific deploy command]
    environment: staging
    
  - name: Deploy Frontend
    command: [platform-specific deploy command]
    environment: staging
    
  - name: Health Check
    command: curl -f https://staging-api.yourdomain.com/api/health
    retry: 3
    wait_between: 10s
```

### Stage 5: Deploy (Production)
```yaml
name: Deploy Production
trigger: manual approval required
steps:
  - name: Production Deploy Approval
    type: manual_gate
    approvers: [human-reviewer]
    
  - name: Deploy Backend
    command: [production deploy command]
    
  - name: Deploy Frontend
    command: [production deploy command]
    
  - name: Production Health Check
    command: curl -f https://api.yourdomain.com/api/health
    retry: 5
    wait_between: 15s
```

---

## GitHub Actions Template

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - name: Install backend deps
        run: cd backend && npm ci
      - name: Install frontend deps
        run: cd frontend && npm ci
      - name: Lint backend
        run: cd backend && npm run lint
      - name: Lint frontend
        run: cd frontend && npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    
    services:
      mongodb:
        image: mongo:7
        ports:
          - 27017:27017
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - name: Install deps
        run: cd backend && npm ci
      - name: Run tests
        run: cd backend && npm test
        env:
          MONGO_URI: mongodb://localhost:27017/test
          NODE_ENV: test
          JWT_SECRET: test-secret-32-chars-minimum-length
          JWT_REFRESH_SECRET: test-refresh-32-chars-minimum

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - name: Install frontend deps
        run: cd frontend && npm ci
      - name: Build frontend
        run: cd frontend && npm run build
        env:
          VITE_API_BASE_URL: https://api.yourdomain.com
```

---

## npm Scripts Reference

### Backend package.json scripts
```json
{
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js",
    "lint": "eslint src/ --ext .js",
    "lint:fix": "eslint src/ --ext .js --fix",
    "test": "jest",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "test:coverage": "jest --coverage"
  }
}
```

### Frontend package.json scripts
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src/ --ext .js,.jsx",
    "lint:fix": "eslint src/ --ext .js,.jsx --fix",
    "test": "jest"
  }
}
```

---

## Rollback Strategy

### Immediate Rollback (< 5 minutes post-deploy)
```bash
# If deploy just happened and there's a critical issue:
git revert HEAD
git push origin main  # Triggers CI → auto-deploys previous version
```

### Planned Rollback
```bash
# Find the last stable commit
git log --oneline -10

# Revert to specific commit
git revert --no-commit <bad-commit>..<HEAD>
git commit -m "Revert: [description of what was reverted]"
git push origin main
```

---

## Branch Strategy

```
main        → production (protected, requires PR + CI pass)
develop     → staging (auto-deploys on push)
feature/*   → feature branches (merge to develop via PR)
fix/*       → bug fix branches (merge to develop via PR)
hotfix/*    → critical production fixes (merge to main directly after review)
```

## Pre-Merge Checklist (PR Template)
```markdown
## PR Checklist
- [ ] All CI stages passing
- [ ] Code follows CODING_STANDARDS.md
- [ ] Security reviewed (SECURITY.md)
- [ ] All new endpoints have validators
- [ ] No debug logs (`grep -r "// \[DEBUG\]" src/`)
- [ ] DECISIONS.md updated for architectural changes
- [ ] TASKS.md updated (mark task complete)
```
