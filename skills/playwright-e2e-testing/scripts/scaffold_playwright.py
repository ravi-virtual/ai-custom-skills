#!/usr/bin/env python3
"""scaffold_playwright.py - add a Playwright Test (TypeScript) e2e setup to a project.

Usage:
  python scaffold_playwright.py [--out DIR] [--base-url http://localhost:3000]
                                [--with-auth] [--force]

Writes (never overwrites existing files unless --force):
  playwright.config.ts      parallel, CI-aware retries, trace/screenshot/video on failure, HTML report
  e2e/fixtures.ts           extended `test` with page objects
  e2e/pages/HomePage.ts     example page object (role-based locators)
  e2e/smoke.spec.ts         example tests tagged @smoke
  e2e/auth.setup.ts         (--with-auth) log in once, reuse storageState
  .github/workflows/playwright.yml
  .gitignore additions, tsconfig.e2e.json
Then prints the npm commands to run. Standard library only.
"""
import argparse
import os
import sys
import textwrap

dedent = lambda t: textwrap.dedent(t).lstrip("\n")  # noqa: E731


def config(base_url, with_auth):
    setup_project = '''    { name: 'setup', testMatch: /.*\\.setup\\.ts/ },
''' if with_auth else ""
    chromium_extra = '''
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],''' if with_auth else '''
      use: { ...devices['Desktop Chrome'] },'''
    return dedent(f'''
        import {{ defineConfig, devices }} from '@playwright/test';

        const baseURL = process.env.BASE_URL ?? '{base_url}';

        export default defineConfig({{
          testDir: './e2e',
          fullyParallel: true,
          forbidOnly: !!process.env.CI,                 // fail the build if test.only is committed
          retries: process.env.CI ? 2 : 0,              // retries expose flakiness; do not rely on them locally
          workers: process.env.CI ? 2 : undefined,
          reporter: [['list'], ['html', {{ open: 'never' }}]],
          use: {{
            baseURL,
            trace: 'on-first-retry',                    // open with: npx playwright show-trace <trace.zip>
            screenshot: 'only-on-failure',
            video: 'retain-on-failure',
          }},
          projects: [
        {setup_project}    {{
              name: 'chromium',{chromium_extra}
            }},
            // {{ name: 'firefox', use: {{ ...devices['Desktop Firefox'] }} }},
            // {{ name: 'webkit', use: {{ ...devices['Desktop Safari'] }} }},
            // {{ name: 'mobile', use: {{ ...devices['Pixel 7'] }} }},
          ],
          // Start the app for the tests (uncomment and adapt):
          // webServer: {{
          //   command: 'npm run dev',
          //   url: baseURL,
          //   reuseExistingServer: !process.env.CI,
          // }},
        }});
    ''')


FIXTURES = dedent('''
    import { test as base, expect } from '@playwright/test';
    import { HomePage } from './pages/HomePage';

    type Fixtures = { homePage: HomePage };

    // Fixtures give every test fresh, isolated page objects and keep setup out of test bodies.
    export const test = base.extend<Fixtures>({
      homePage: async ({ page }, use) => {
        await use(new HomePage(page));
      },
    });

    export { expect };
''')

HOME_PAGE = dedent('''
    import type { Locator, Page } from '@playwright/test';

    // Page objects hold locators and user-level actions, never assertions.
    export class HomePage {
      readonly page: Page;
      readonly mainHeading: Locator;

      constructor(page: Page) {
        this.page = page;
        this.mainHeading = page.getByRole('heading', { level: 1 });
      }

      async goto() {
        await this.page.goto('/');
      }
    }
''')

SMOKE = dedent('''
    import { test, expect } from './fixtures';

    // Replace these examples with your critical user journeys.
    test.describe('smoke', { tag: '@smoke' }, () => {
      test('home page loads without errors', async ({ page, homePage }) => {
        const errors: string[] = [];
        page.on('pageerror', (e) => errors.push(e.message));

        await homePage.goto();

        await expect(homePage.mainHeading).toBeVisible();   // web-first assertion: auto-waits and retries
        expect(errors).toEqual([]);
      });

      test('unknown route is handled', async ({ page }) => {
        const response = await page.goto('/this-route-does-not-exist');
        expect(response?.status()).toBeGreaterThanOrEqual(400);
      });
    });
''')

AUTH_SETUP = dedent('''
    import { test as setup, expect } from '@playwright/test';

    const authFile = 'playwright/.auth/user.json';

    // Runs once before the dependent projects; every test then starts already logged in.
    setup('authenticate', async ({ page }) => {
      const email = process.env.E2E_USER_EMAIL;
      const password = process.env.E2E_USER_PASSWORD;
      if (!email || !password) throw new Error('Set E2E_USER_EMAIL and E2E_USER_PASSWORD (a dedicated test account).');

      await page.goto('/login');
      await page.getByLabel('Email').fill(email);
      await page.getByLabel('Password').fill(password);
      await page.getByRole('button', { name: 'Sign in' }).click();
      await expect(page).not.toHaveURL(/login/);          // adapt to a post-login signal in your app

      await page.context().storageState({ path: authFile });
    });
''')

WORKFLOW = dedent('''
    name: Playwright
    on:
      push:
        branches: [main]
      pull_request:
    jobs:
      e2e:
        runs-on: ubuntu-latest
        timeout-minutes: 30
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with:
              node-version: lts/*
              cache: npm
          - run: npm ci
          - run: npx playwright install --with-deps chromium
          - run: npx playwright test
            env:
              BASE_URL: ${{ vars.E2E_BASE_URL }}
              E2E_USER_EMAIL: ${{ secrets.E2E_USER_EMAIL }}
              E2E_USER_PASSWORD: ${{ secrets.E2E_USER_PASSWORD }}
          - uses: actions/upload-artifact@v4
            if: ${{ !cancelled() }}
            with:
              name: playwright-report
              path: |
                playwright-report/
                test-results/
              retention-days: 14
''')

TSCONFIG = dedent('''
    {
      "compilerOptions": {
        "target": "ES2022",
        "module": "ESNext",
        "moduleResolution": "Bundler",
        "strict": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "noEmit": true,
        "types": ["node"]
      },
      "include": ["e2e", "playwright.config.ts"]
    }
''')

GITIGNORE = "\n# Playwright\nnode_modules/\ntest-results/\nplaywright-report/\nblob-report/\nplaywright/.auth/\nplaywright/.cache/\n"


def main():
    ap = argparse.ArgumentParser(description="Scaffold a Playwright Test setup.")
    ap.add_argument("--out", default=".", help="project root (default: current directory)")
    ap.add_argument("--base-url", default="http://localhost:3000")
    ap.add_argument("--with-auth", action="store_true", help="add a login setup project using storageState")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    plan = {
        "playwright.config.ts": config(args.base_url, args.with_auth),
        "e2e/fixtures.ts": FIXTURES,
        "e2e/pages/HomePage.ts": HOME_PAGE,
        "e2e/smoke.spec.ts": SMOKE,
        ".github/workflows/playwright.yml": WORKFLOW,
        "tsconfig.e2e.json": TSCONFIG,
    }
    if args.with_auth:
        plan["e2e/auth.setup.ts"] = AUTH_SETUP

    written, skipped = [], []
    for rel, content in plan.items():
        path = os.path.join(args.out, rel)
        if os.path.exists(path) and not args.force:
            skipped.append(rel)
            continue
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        written.append(rel)

    gi = os.path.join(args.out, ".gitignore")
    existing = open(gi, encoding="utf-8").read() if os.path.exists(gi) else ""
    if "playwright-report/" not in existing:
        with open(gi, "a", encoding="utf-8") as fh:
            fh.write(GITIGNORE)
        written.append(".gitignore (appended)")

    print("Written: " + ", ".join(written))
    if skipped:
        print("Skipped (exist, use --force): " + ", ".join(skipped))
    print("Next:\n  npm install -D @playwright/test @types/node\n  npx playwright install --with-deps chromium\n  npx playwright test")
    if args.with_auth:
        print("  (set E2E_USER_EMAIL / E2E_USER_PASSWORD for the auth setup project)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
