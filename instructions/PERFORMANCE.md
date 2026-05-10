# PERFORMANCE.md — Performance Standards & Benchmarks

## Performance Philosophy
Performance is a feature. Slow APIs and sluggish UIs degrade user experience and signal poor engineering. Every component of this system must meet defined performance budgets.

---

## Section 1: API Performance Standards

### Response Time Budgets
| Endpoint Type | Target (p50) | Acceptable (p95) | Alert Threshold |
|---|---|---|---|
| Simple CRUD (read) | < 100ms | < 300ms | > 500ms |
| Simple CRUD (write) | < 150ms | < 400ms | > 700ms |
| Authenticated read | < 120ms | < 350ms | > 600ms |
| AI generation endpoint | < 5s | < 15s | > 30s |
| Paginated list (50 items) | < 200ms | < 500ms | > 1s |

### Database Query Performance
```javascript
// ✅ Optimized query patterns

// 1. Always .lean() for reads
const users = await User.find({ isDeleted: false }).lean();

// 2. Only select needed fields
const users = await User.find({ isDeleted: false })
  .select('name email role createdAt')
  .lean();

// 3. Use .limit() for all list queries
const users = await User.find({ isDeleted: false })
  .limit(50)
  .skip(page * 50)
  .lean();

// 4. Use indexed fields in queries (define indexes on schema)
userSchema.index({ email: 1 }, { unique: true });
userSchema.index({ createdAt: -1 }); // For time-sorted queries
userSchema.index({ isDeleted: 1, role: 1 }); // Compound for common query
```

### Indexing Strategy
| Index | Purpose | Type |
|---|---|---|
| `email: 1` | Unique email lookup | Unique |
| `createdAt: -1` | Time-sorted queries | Regular |
| `isDeleted: 1, role: 1` | Role-based filtered queries | Compound |
| `isDeleted: 1, createdAt: -1` | Soft-deleted list queries | Compound |

---

## Section 2: Frontend Performance Standards

### Page Load Budgets
| Metric | Target | Alert Threshold |
|---|---|---|
| First Contentful Paint (FCP) | < 1.5s | > 3s |
| Largest Contentful Paint (LCP) | < 2.5s | > 4s |
| Total Blocking Time (TBT) | < 200ms | > 600ms |
| Cumulative Layout Shift (CLS) | < 0.1 | > 0.25 |
| Bundle Size (gzipped) | < 300KB | > 500KB |

### React Performance Rules
```jsx
// 1. Memoize expensive computations
const sortedUsers = useMemo(() => {
  return users.slice().sort((a, b) => a.name.localeCompare(b.name));
}, [users]); // Only recalculates when users changes

// 2. Memoize callbacks to prevent child re-renders
const handleDelete = useCallback((id) => {
  dispatch(deleteUser(id));
}, [dispatch]);

// 3. Avoid creating new objects/arrays in JSX
// ❌ Creates new array on every render
<Component styles={['class1', 'class2']} />

// ✅ Stable reference
const styles = ['class1', 'class2']; // Outside component
<Component styles={styles} />

// 4. Use React.memo for pure components
const UserCard = React.memo(({ user }) => (
  <div>{user.name}</div>
));
```

### Bundle Optimization
```javascript
// Vite config for code splitting
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          redux: ['@reduxjs/toolkit', 'react-redux'],
          router: ['react-router-dom'],
        }
      }
    }
  }
}
```

---

## Section 3: Memory & Resource Standards

### Backend Memory
- Node.js process memory should remain < 256MB under normal load
- No memory leaks: memory should not grow continuously over time
- Database connection pool: use Mongoose's built-in connection pooling (default: 5)

### Frontend Memory
- No memory leaks from missing useEffect cleanup
- Event listeners must be removed in cleanup functions
- Large data sets should use virtual scrolling, not render-all

---

## Section 4: AI Generation Performance

### Timeout Configuration
```javascript
// Per-model timeout in the fallback chain
const AI_TIMEOUTS = {
  gemini: 10000,   // 10 seconds
  grok: 8000,      // 8 seconds
  openai: 6000,    // 6 seconds (most reliable, shorter timeout)
};
```

### Response Streaming
- For AI generation endpoints, consider streaming responses to the frontend
- Streaming reduces perceived latency even when total generation time is unchanged
- Use Server-Sent Events (SSE) or WebSocket for streaming

---

## Section 5: Performance Monitoring

### Metrics to Track
```javascript
// Backend: Add timing middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (duration > 500) {
      console.warn(`SLOW REQUEST: ${req.method} ${req.path} ${duration}ms`);
    }
  });
  next();
});
```

### Performance Regression Detection
- Track API response times per endpoint
- Alert when any endpoint exceeds its p95 threshold consistently
- Profile database queries when API times exceed budget
- Use `EXPLAIN` on MongoDB queries that are slow

---

## Section 6: Performance Testing

### Load Testing Approach
```bash
# Use artillery or k6 for load testing
artillery quick --count 100 --num 10 http://localhost:5000/api/users

# Target: 100 requests, 10 concurrent users
# Pass criteria: 0 errors, < 300ms average response time
```

### Performance Checklist
Before deploying any new endpoint:
- [ ] Query uses indexed fields
- [ ] Query uses `.lean()` and `.select()`
- [ ] Pagination is implemented for list endpoints
- [ ] Response time tested with 100+ document collection
- [ ] Memory usage unchanged after 1000 request test run
