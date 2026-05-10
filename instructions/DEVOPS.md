# DEVOPS.md — DevOps Operations Reference

## Overview
This file covers operational procedures for running, maintaining, and scaling the MERN stack application infrastructure.

---

## Section 1: Local Development Operations

### Starting the Stack
```bash
# Terminal 1: MongoDB (if local)
mongod --dbpath /data/db

# Terminal 2: Backend
cd backend
npm run dev          # nodemon watches for changes, restarts on save

# Terminal 3: Frontend
cd frontend
npm run dev          # Vite dev server with HMR
```

### Stopping the Stack
```bash
# Stop nodemon/vite: Ctrl+C in each terminal

# Kill processes if stuck on port
npx kill-port 5000   # Backend
npx kill-port 5173   # Frontend
```

### Resetting Local State
```bash
# Clear MongoDB (development only — NEVER on production)
mongosh
> use appname_development
> db.dropDatabase()

# Reset node_modules (if dependency issues)
cd backend && rm -rf node_modules && npm install
cd frontend && rm -rf node_modules && npm install

# Clear Vite cache
cd frontend && rm -rf node_modules/.vite
```

---

## Section 2: Process Management (Production)

### PM2 Operations
```bash
# Install PM2 globally
npm install -g pm2

# Start the backend
pm2 start backend/src/server.js --name "app-backend" --watch

# Start with environment variables
pm2 start backend/src/server.js \
  --name "app-backend" \
  --env production

# View running processes
pm2 list

# View logs
pm2 logs app-backend
pm2 logs app-backend --lines 100  # Last 100 lines

# Restart on change
pm2 restart app-backend

# Stop
pm2 stop app-backend

# Delete from PM2 registry
pm2 delete app-backend

# Save PM2 configuration (persist across reboots)
pm2 save
pm2 startup  # Then run the command it outputs

# Monitor real-time
pm2 monit
```

### PM2 Ecosystem File
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'app-backend',
    script: 'src/server.js',
    cwd: './backend',
    instances: 'max',         // Or specific number: 2
    exec_mode: 'cluster',     // Load balancing across instances
    env: {
      NODE_ENV: 'production',
    },
    error_file: 'logs/err.log',
    out_file: 'logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    max_memory_restart: '256M',
    restart_delay: 1000,
  }]
};

// Start with ecosystem file
// pm2 start ecosystem.config.js
```

---

## Section 3: Database Operations

### MongoDB Backup
```bash
# Backup a database (point-in-time)
mongodump --uri "mongodb://localhost:27017/appname" --out ./backups/$(date +%Y%m%d)

# Backup a single collection
mongodump --uri "mongodb://localhost:27017/appname" \
  --collection users --out ./backups/users_$(date +%Y%m%d)
```

### MongoDB Restore
```bash
# Restore entire database (staging/dev only)
mongorestore --uri "mongodb://localhost:27017/appname" ./backups/20250115/

# Restore single collection
mongorestore --uri "mongodb://localhost:27017/appname" \
  --collection users ./backups/users_20250115/appname/users.bson
```

### Database Maintenance Queries
```javascript
// Via mongosh

// Check database stats
db.stats()

// Check collection stats
db.users.stats()

// Find large documents
db.profiles.aggregate([
  { $project: { _id: 1, size: { $bsonSize: "$$ROOT" } } },
  { $sort: { size: -1 } },
  { $limit: 10 }
])

// Count soft-deleted records
db.users.countDocuments({ isDeleted: true })

// Verify indexes are being used
db.users.find({ email: "test@test.com" }).explain("executionStats")

// Check slow queries (requires profiling enabled)
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(10)
```

---

## Section 4: Nginx Configuration

```nginx
# /etc/nginx/sites-available/app
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;  # Redirect HTTP to HTTPS
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend (React SPA)
    location / {
        root /var/www/app/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;  # SPA routing
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 30s;  # Adjust for AI endpoints
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

### SSL Setup with Certbot
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (cron)
sudo certbot renew --dry-run  # Test
# Certbot adds auto-renewal cron automatically
```

---

## Section 5: Environment Management

### Secret Rotation Procedure
When rotating JWT secrets:
1. Generate new secrets: `node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"`
2. Deploy new secrets to environment
3. Restart the backend server
4. **All existing tokens are immediately invalidated** — users must log in again
5. Monitor auth failure logs briefly to confirm normal operations
6. Document the rotation in SESSION.md

### Environment Variables Audit
```bash
# List all env vars in use (check for any undocumented ones)
grep -r "process.env" backend/src/

# Should ONLY appear in constants.js
# If appears elsewhere → VIOLATION → fix immediately
```

---

## Section 6: Emergency Procedures

### Service Down
```
1. Check PM2: pm2 list
2. Check logs: pm2 logs app-backend --lines 50
3. Check DB: mongosh --eval "db.adminCommand('ping')"
4. Restart if needed: pm2 restart app-backend
5. If still down: pm2 delete + pm2 start
6. If still down: check OS resources (disk space, memory)
```

### High Memory Usage
```bash
# Check memory
free -h
pm2 monit

# Restart the process (PM2 will restart it)
pm2 restart app-backend

# If recurring: investigate memory leak in DEBUGGING.md workflow
```

### Disk Space Full
```bash
# Check usage
df -h

# Find large files
du -sh /var/log/* | sort -rh | head -20

# Clear old logs
pm2 flush  # Clears PM2 logs
find /var/log -name "*.log" -mtime +30 -delete

# Clear old backups
find ./backups -mtime +30 -type d -exec rm -rf {} +
```
