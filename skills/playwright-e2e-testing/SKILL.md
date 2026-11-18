---
name: playwright-e2e-testing
description: Sets up, writes, debugs and stabilises Playwright end-to-end tests in TypeScript - config, role-based locators, web-first assertions, fixtures and page objects, login reuse with storageState, API seeding, network mocking, CI with traces and reports, and flaky-test triage. Use when the user wants browser or e2e tests for a web app, asks to add Playwright, fix a failing or flaky Playwright test, speed up a suite, test a login or checkout flow, or run browser tests in CI. For test planning and case design use qa-test-strategy first.
---

# Playwright E2E Testing

Write few, stable, user-focused tests for the critical journeys; push everything else down to unit and API tests (see `qa-test-strategy`).

## Workflow

1. **Pick the journeys.** Ask for the 3 to 7 flows whose failure would hurt most (sign-up/login, core task, checkout/payment, key admin action). Each becomes one or two tests, not dozens.
2. **Set up** (new project): `python scripts/scaffold_playwright.py --base-url http://localhost:3000 [--with-auth]`, then `npm install -D @playwright/test @types/node` and `npx playwright install --with-deps chromium`. Existing config is never overwritten without `--force`. The scaffold type-checks and its example tests pass against a running page.
3. **Explore the UI** with `npx playwright codegen <url>` to find locators, then rewrite the output into the style below. Never commit raw codegen.
4. **Write tests** following the rules below, one user outcome per test, independent of every other test.
5. **Run:** `npx playwright test` (all), `--grep @smoke` (tagged), `--ui` (watch mode with time travel), `--debug` (step through), `--headed`. Report: `npx playwright show-report`.
6. **Fix failures from evidence:** open the trace (`npx playwright show-trace test-results/<test>/trace.zip`), read the error, the DOM snapshot and the network tab before changing anything.
7. **Wire CI** (the scaffold writes `.github/workflows/playwright.yml`): install browsers, run, upload `playwright-report/` and `test-results/` as artifacts.

## Rules that keep suites stable

**Locators, in order of preference:** `getByRole('button', { name: 'Save' })`, `getByLabel`, `getByPlaceholder`, `getByText`, `getByTestId` (configure `testIdAttribute` if the app uses another attribute), and only then CSS/XPath. Role and label locators match how users and assistive technology see the page and survive markup changes. Scope with `locator.filter({ hasText })` or by chaining from a region, not by position (`nth`) unless order is the point.

**Assertions:** use web-first assertions that auto-wait and retry: `await expect(locator).toBeVisible()`, `toHaveText`, `toHaveValue`, `toHaveCount`, `toHaveURL`. Do not assert on a snapshot value such as `expect(await locator.isVisible()).toBe(true)`. Use `expect.poll` or `expect(...).toPass()` for non-DOM conditions.

**Waiting:** never `waitForTimeout` or fixed sleeps. Wait for the thing you need: an assertion, `page.waitForResponse`, or a locator state. Actions (`click`, `fill`) already wait for actionability.

**Isolation:** each test creates the data it needs and does not rely on another test's leftovers. Seed and clean up through the API or a database helper (`request` fixture), not by clicking through the UI. Use unique values (`Date.now()` or a random suffix) so parallel workers do not collide.

**Login once:** do it in a `setup` project and reuse `storageState` (scaffold `--with-auth`); keep test credentials in environment variables for a dedicated test account, never in the repo. For tests that must start logged out, override with `test.use({ storageState: { cookies: [], origins: [] } })`.

**Page objects and fixtures:** use a page object for pages touched by many tests (locators plus user-level actions, no assertions); for small suites plain helper functions are enough. Share setup through fixtures (`test.extend`), not `beforeAll` mutations of shared state.

**Third parties and flakiness sources:** mock payment, email, maps and analytics with `page.route` or use the vendor's test mode; fix time-dependent logic with `page.clock`; avoid depending on the public internet.

**Structure:** `test.step('...')` for readable reports; tag with `{ tag: '@smoke' }` and run subsets with `--grep`; `test.describe.configure({ mode: 'serial' })` only for genuinely ordered flows.

## Debugging and flaky-test triage

| Symptom | Likely cause | Fix |
|---|---|---|
| Passes alone, fails in the full run | Shared data/state between tests | Isolate data; unique values; own account per worker if needed |
| Element not found / not visible | Wrong locator, wrong frame, element behind overlay, not rendered yet | Check the trace snapshot; use `frameLocator`; assert the precondition |
| Click lands on wrong thing or "intercepts pointer events" | Overlay, animation, sticky header | Wait for the overlay to disappear; disable animations in test config |
| Passes locally, fails in CI | Slower machine, different data or viewport, missing env vars | Review CI trace; keep retries at 2 and fix the root cause; match viewport |
| Intermittent assertion failure | Asserting before data settles, race with network | Web-first assertion or `waitForResponse`; never a sleep |
| Suite is slow | Logging in through the UI, serial tests, UI-driven setup | `storageState`, API seeding, `fullyParallel`, shard in CI (`--shard=1/4`) |

A test that fails intermittently is a defect in the test or the app. Quarantine it with an issue and an owner (`test.fixme` plus a link), do not leave it retrying forever. CI `retries` are a safety net, and `trace: 'on-first-retry'` gives the evidence.

## Also supported

API tests with the `request` fixture, visual comparisons with `toHaveScreenshot` (pin OS and browser in CI; expect maintenance), accessibility checks with `@axe-core/playwright` (adds a dependency), file upload/download, multiple tabs, iframes, and dialogs. Snippets: `references/playwright-cheatsheet.md`.

## Files

- `scripts/scaffold_playwright.py` - config, fixtures, page object, smoke tests, auth setup, CI workflow
- `references/playwright-cheatsheet.md` - copy-ready snippets for common situations
