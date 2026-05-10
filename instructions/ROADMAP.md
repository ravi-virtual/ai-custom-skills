# ROADMAP.md — Product & Technical Roadmap

## Purpose
Tracks planned features, technical improvements, and system evolution over time. Provides directional clarity for both human developers and AI agents.

---

## Current Status: Phase 2 — Feature Enhancement

```
Phase 1: Foundation    ✅ Complete
Phase 2: Enhancement   🔄 In Progress  ← We are here
Phase 3: Scale         ⬜ Planned
Phase 4: Intelligence  ⬜ Planned
```

---

## Phase 1: Foundation ✅ (Complete)

### Completed Features
- [x] User authentication (register, login, logout)
- [x] JWT access token (15m) + refresh token (15m, httpOnly cookie)
- [x] Profile creation (multi-step form)
- [x] Profile persistence across sessions
- [x] AI-powered content generation (Gemini → Grok → OpenAI fallback)
- [x] User feedback on generated content
- [x] Responsive navigation with hamburger menu
- [x] Profile list, switching, and deletion
- [x] Form validation on all steps
- [x] Frontend token refresh interceptor

### Completed Infrastructure
- [x] AI Operating System (60 markdown files)
- [x] MERN stack project structure
- [x] Full middleware chain (hasToken → isAuthenticated → role → validator → controller)
- [x] ApiResponse + sendError utilities
- [x] constants.js centralized config
- [x] axiosInstance with interceptors

---

## Phase 2: Enhancement 🔄 (In Progress)

### High Priority (Next Up)
- [ ] Admin panel — user management dashboard
  - List all users with pagination
  - Soft-delete user accounts
  - View user profiles
  - Promote/demote user roles

- [ ] Email verification on registration
  - Send verification email with token
  - Verify email endpoint
  - Block unverified users from AI generation

- [ ] Password reset flow
  - "Forgot password" request → email with reset token
  - Reset password endpoint (validate token, update password)

### Medium Priority
- [ ] Profile export (download as PDF or text)
- [ ] Multiple profile templates (LinkedIn, resume, bio)
- [ ] AI generation history (view past generations per profile)
- [ ] User preferences (theme, language, notification settings)

### Low Priority
- [ ] Social login (Google OAuth)
- [ ] Profile sharing (public URL for a profile)
- [ ] AI generation refinement (re-generate with feedback context)

---

## Phase 3: Scale ⬜ (Planned — Q3 2026)

### Performance
- [ ] Redis caching layer for frequently accessed profiles
- [ ] Database query optimization audit
- [ ] CDN for frontend static assets
- [ ] API response compression (gzip)

### Reliability
- [ ] Circuit breaker for AI service calls
- [ ] Database connection pooling optimization
- [ ] Automated backup verification (monthly restore test)
- [ ] Zero-downtime deployments (blue-green or rolling)

### Observability
- [ ] Centralized log aggregation (Better Stack)
- [ ] Error tracking with Sentry integration
- [ ] Performance dashboards (response time, error rate per endpoint)
- [ ] Automated alerts for P0/P1 thresholds

---

## Phase 4: Intelligence ⬜ (Planned — Q4 2026)

### AI Enhancements
- [ ] Fine-tuned model for domain-specific profile generation
- [ ] Context-aware generation (uses existing profile content as context)
- [ ] A/B testing for generation quality (compare model outputs)
- [ ] Batch generation (generate all profile sections in one click)

### Automation
- [ ] Scheduled profile refresh suggestions ("Your profile is 30 days old — update?")
- [ ] Automated quality scoring for generated content
- [ ] Smart suggestions based on feedback patterns across users

---

## Technical Debt Register

| Item | Priority | Effort | Impact |
|---|---|---|---|
| Add ESLint rule for missing `return` before response | High | Low | High |
| Add test coverage to auth middleware chain | High | Medium | High |
| Extract AI service into dedicated microservice | Low | High | Medium |
| Migrate from CommonJS to ESM | Low | High | Low |
| Add TypeScript types to API response shapes | Low | High | Low |
| Add API versioning (`/api/v1/`) | Medium | Medium | Medium |

---

## Deprecated / Cancelled Features

| Feature | Status | Reason |
|---|---|---|
| Real-time notifications (WebSockets) | Cancelled | Out of scope for MVP phase |
| Mobile app (React Native) | Deferred | Web-first strategy |
| Multi-tenant support | Deferred | Single-tenant until scale demands it |
| Stripe billing integration | Deferred | No monetization in current phase |

---

## Version History

| Version | Date | Major Changes |
|---|---|---|
| 0.1.0 | 2026-04-10 | Initial project scaffold |
| 0.2.0 | 2026-04-12 | Auth + profile CRUD + AI generation |
| 0.3.0 | 2026-04-12 | Token refresh, feedback, validation |
| 0.4.0 | 2026-05-10 | AI-OS 60-file framework complete |
| 0.5.0 | TBD | Admin panel + email verification |

---

## Roadmap Decision Log

| Decision | Date | Rationale |
|---|---|---|
| Web-only (no mobile) | Project start | Faster iteration, lower complexity |
| MERN stack | Project start | Full-stack JS consistency |
| Gemini as primary AI | 2026-04-12 | Best free tier, strong performance |
| Soft delete everywhere | Project start | Data recovery + audit trail |
| Phase over ship-all-at-once | Project start | Learn from users early |
