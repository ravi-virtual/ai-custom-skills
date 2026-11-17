# Playwright Cheatsheet (TypeScript)

## Contents
- [Locators](#locators)
- [Assertions](#assertions)
- [Auth with storageState](#auth-with-storagestate)
- [API seeding and API tests](#api-seeding-and-api-tests)
- [Network mocking and waiting](#network-mocking-and-waiting)
- [Forms, uploads, downloads, dialogs](#forms-uploads-downloads-dialogs)
- [Frames and multiple pages](#frames-and-multiple-pages)
- [Data-driven tests and tags](#data-driven-tests-and-tags)
- [Config options worth knowing](#config-options-worth-knowing)
- [CLI](#cli)

## Locators

```ts
page.getByRole('button', { name: 'Sign in' });
page.getByRole('link', { name: /pricing/i });
page.getByLabel('Email');
page.getByPlaceholder('Search');
page.getByText('Order confirmed');
page.getByTestId('cart-count');                  // data-testid by default
page.getByRole('row', { name: /Ada/ }).getByRole('button', { name: 'Delete' });
page.locator('li').filter({ hasText: 'Pro plan' }).getByRole('button');
```

## Assertions

```ts
await expect(page).toHaveURL(/\/dashboard/);
await expect(page).toHaveTitle('Dashboard');
await expect(locator).toBeVisible();
await expect(locator).toBeEnabled();
await expect(locator).toHaveText('Saved');       // exact; use a RegExp for partial
await expect(locator).toContainText('Saved');
await expect(locator).toHaveValue('ada@example.com');
await expect(locator).toHaveCount(3);
await expect(locator).toHaveAttribute('aria-expanded', 'true');
await expect.poll(async () => (await request.get('/api/status')).status()).toBe(200);
await expect(async () => { /* any retried block */ }).toPass({ timeout: 10_000 });
await expect(page).toHaveScreenshot('home.png', { maxDiffPixelRatio: 0.01 });
```

Soft assertions (`expect.soft`) record a failure and keep going; use them for independent checks on one page.

## Auth with storageState

```ts
// e2e/auth.setup.ts  (project "setup", other projects depend on it)
setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.E2E_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.E2E_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/dashboard/);
  await page.context().storageState({ path: 'playwright/.auth/user.json' });
});
```

Different roles: one setup per role writing its own file, then `test.use({ storageState: 'playwright/.auth/admin.json' })` in the relevant describe block. Faster alternative: log in with `request.post('/api/login')` and save `request.storageState()`.

## API seeding and API tests

```ts
test('shows a seeded order', async ({ page, request }) => {
  const res = await request.post('/api/orders', { data: { sku: 'A1', qty: 2 } });
  expect(res.ok()).toBeTruthy();
  const { id } = await res.json();

  await page.goto(`/orders/${id}`);
  await expect(page.getByRole('heading', { name: `Order ${id}` })).toBeVisible();

  await request.delete(`/api/orders/${id}`);      // clean up
});
```

## Network mocking and waiting

```ts
// Mock a backend response
await page.route('**/api/products', (route) =>
  route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([{ id: 1, name: 'Mock' }]) }));

// Simulate failure
await page.route('**/api/checkout', (route) => route.abort('failed'));

// Wait for the response triggered by an action (start waiting BEFORE the action)
const responsePromise = page.waitForResponse((r) => r.url().includes('/api/save') && r.ok());
await page.getByRole('button', { name: 'Save' }).click();
await responsePromise;
```

## Forms, uploads, downloads, dialogs

```ts
await page.getByLabel('Country').selectOption('IN');
await page.getByRole('checkbox', { name: 'I agree' }).check();
await page.getByLabel('Upload').setInputFiles('e2e/files/invoice.pdf');

const downloadPromise = page.waitForEvent('download');
await page.getByRole('button', { name: 'Export CSV' }).click();
const download = await downloadPromise;
expect(download.suggestedFilename()).toMatch(/\.csv$/);

page.once('dialog', (d) => d.accept());          // register before the click that opens it
await page.getByRole('button', { name: 'Delete' }).click();
```

## Frames and multiple pages

```ts
const frame = page.frameLocator('iframe[title="Payment"]');
await frame.getByLabel('Card number').fill('4242 4242 4242 4242');   // vendor test card, test mode only

const popupPromise = page.waitForEvent('popup');
await page.getByRole('link', { name: 'Terms' }).click();
const popup = await popupPromise;
await expect(popup).toHaveURL(/terms/);
```

## Data-driven tests and tags

```ts
for (const [role, canDelete] of [['admin', true], ['viewer', false]] as const) {
  test(`${role} delete button visibility`, { tag: '@permissions' }, async ({ page }) => {
    // ...
  });
}
// run: npx playwright test --grep @permissions   |   --grep-invert @slow
```

## Config options worth knowing

| Option | Purpose |
|---|---|
| `fullyParallel`, `workers` | Parallelism within and across files |
| `retries`, `forbidOnly` | CI safety net; block committed `test.only` |
| `use.trace`, `screenshot`, `video` | Evidence on failure |
| `use.baseURL`, `use.locale`, `use.timezoneId`, `use.viewport` | Deterministic environment |
| `expect.timeout`, `timeout` | Assertion and test time limits (raise sparingly) |
| `webServer` | Start the app before tests, reuse locally |
| `projects` with `dependencies` | Setup projects, browser/device matrix |
| `globalSetup` | One-time work like seeding a database |

## CLI

```bash
npx playwright test                         # everything
npx playwright test e2e/smoke.spec.ts:15    # one test by line
npx playwright test -g "checkout"           # by title
npx playwright test --project=chromium --headed
npx playwright test --ui                    # interactive runner
npx playwright test --debug                 # inspector
npx playwright test --shard=2/4             # split across CI machines
npx playwright test --last-failed
npx playwright codegen http://localhost:3000
npx playwright show-report
npx playwright show-trace path/to/trace.zip
```
