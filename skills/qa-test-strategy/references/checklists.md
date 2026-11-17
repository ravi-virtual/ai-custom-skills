# QA Checklists

## Contents
- [Web UI](#web-ui)
- [API](#api)
- [Accessibility smoke](#accessibility-smoke)
- [Security smoke](#security-smoke)
- [Performance smoke](#performance-smoke)
- [Compatibility](#compatibility)
- [Localisation](#localisation)
- [Regression / release](#regression--release)

## Web UI
- [ ] Every primary journey completes end to end (signup, login, core task, logout)
- [ ] Form validation: required, format, limits, inline messages that say how to fix it, no data lost on error
- [ ] Empty, loading and error states exist and are understandable
- [ ] Back, forward, refresh and deep links behave; unsaved-changes warning where data could be lost
- [ ] Double-click and repeated submit do not duplicate actions
- [ ] Session expiry and re-login return the user sensibly
- [ ] Links, buttons, menus work; no console errors on main pages
- [ ] Responsive at common widths (320, 768, 1280+); touch targets usable

## API
- [ ] Status codes match the contract (200/201/204, 400, 401, 403, 404, 409, 422, 429, 5xx never for client mistakes)
- [ ] Response schema and types match the docs; error bodies are consistent and contain no stack traces
- [ ] Authentication required where expected; token expiry handled
- [ ] Authorisation: user A cannot read or change user B's resources (change IDs in the URL and body)
- [ ] Validation: missing, wrong-typed, oversize, and unexpected extra fields
- [ ] Idempotency: repeating PUT/DELETE is safe; POST duplicates are prevented where required
- [ ] Pagination, filtering, sorting: edges and invalid parameters
- [ ] Rate limiting and large payload behaviour
- [ ] Backwards compatibility when the contract changes

## Accessibility smoke
- [ ] Everything operable by keyboard; visible focus; logical tab order; no keyboard traps
- [ ] Images have meaningful alt text (or empty alt if decorative); form fields have labels
- [ ] Colour contrast meets WCAG 2.x AA (4.5:1 normal text, 3:1 large text); information is not conveyed by colour alone
- [ ] Headings form a sensible outline; landmarks present; page has a title; language set
- [ ] Errors are announced and associated with fields; dynamic updates are exposed to assistive tech
- [ ] Works at 200% zoom without losing content; respects reduced-motion
- [ ] Run an automated checker (axe, Lighthouse) and a manual screen-reader pass of the main journey

## Security smoke
Only on systems you are authorised to test, in a non-production environment unless agreed.
- [ ] Authentication: lockout/rate limit on repeated failures, secure password reset, session invalidated on logout
- [ ] Authorisation: direct object references (IDs), forced browsing to admin pages, role escalation
- [ ] Input handling: stored and reflected script injection, SQL/NoSQL injection attempts, file upload type/size checks
- [ ] Transport and headers: HTTPS only, secure and HttpOnly cookies, sensible CORS, security headers present
- [ ] Data exposure: no secrets, tokens or personal data in URLs, logs, error messages or client-side code
- [ ] Dependencies: known-vulnerability scan (npm audit, pip-audit, or equivalent)

## Performance smoke
- [ ] Key pages and endpoints respond within the agreed budget under normal load (define it: for example p95 < 500 ms)
- [ ] Behaviour with a realistic data volume (large lists, big files)
- [ ] No obvious N+1 queries or unbounded result sets
- [ ] A short load test of the critical journey at expected peak, watching errors, latency and resource use
- [ ] Graceful degradation: timeouts and retries do not pile up

## Compatibility
- [ ] Latest two versions of Chrome, Firefox, Safari, Edge (adapt to your analytics)
- [ ] iOS Safari and Android Chrome on at least one small and one large device
- [ ] Supported OS and app versions for mobile/desktop clients; upgrade from the previous version keeps data

## Localisation
- [ ] Text expansion does not break layouts; no hard-coded strings; right-to-left layout if supported
- [ ] Dates, numbers, currency, time zones and pluralisation follow the locale
- [ ] Non-ASCII input is stored and displayed correctly, including in search and sort

## Regression / release
- [ ] Smoke suite passes on the release candidate in a production-like environment
- [ ] Regression suite green; flaky tests triaged, none ignored silently
- [ ] Migration and rollback tested on a copy of production-like data
- [ ] Feature flags, configuration and secrets verified for the target environment
- [ ] Monitoring, alerts and logging confirmed for the new functionality
- [ ] Release notes and known issues documented; support team informed
