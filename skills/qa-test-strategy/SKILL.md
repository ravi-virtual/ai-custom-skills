---
name: qa-test-strategy
description: Plans and performs manual and automated QA - risk-based test strategy and test plans, test case design (boundary values, equivalence classes, decision tables, state transitions), exploratory test charters, regression and release checklists, defect reports with severity and priority, and test summary reports. Use when the user asks how to test a feature or product, to write a test plan or test cases, to review requirements for testability, to triage or write a bug report, to decide what to automate, or to sign off a release. For Playwright browser automation specifically use playwright-e2e-testing.
---

# QA Test Strategy

Goal: find the defects that matter most, cheaply, and give the team an honest picture of quality. Test where the risk is, not evenly everywhere.

## Workflow

1. **Understand what is being tested.** Ask for (or infer) the feature, users, platforms, requirements or acceptance criteria, release date, and what has broken before. List assumptions and open questions; ambiguous requirements are the first defects to report.
2. **Assess risk.** Score each area: likelihood of failure (new code, complexity, many integrations, past bugs) times impact (money, data loss, security, number of users, regulatory). Test depth follows the score.

   | Impact \ Likelihood | Low | Medium | High |
   |---|---|---|---|
   | High | Medium | High | Critical |
   | Medium | Low | Medium | High |
   | Low | Low | Low | Medium |

3. **Choose levels and automation.** Many fast unit tests, fewer integration/API tests, a small set of end-to-end tests on critical journeys, plus exploratory testing for what scripts miss. Automate what is stable, repeated, high-value and deterministic (smoke, regression, data-driven checks); keep usability, look and feel, and new unstable features manual until they settle.
4. **Design cases** with the technique that fits the input (table below). For field validation run `python scripts/generate_test_cases.py spec.json` to get boundary and equivalence cases, then add business outcomes by hand.
5. **Write the plan** from `assets/test-plan.md` (scope, out of scope, approach, environments, data, schedule, entry/exit criteria, risks). Keep it to a page or two for a feature.
6. **Execute and explore.** Run the P1 cases first. Add timeboxed exploratory sessions (60 to 90 minutes) with a charter; record notes and bugs as you go.
7. **Report defects** with `assets/bug-report.md` (below). **Report status** with `assets/test-summary.md`: what was tested, what was not, open defects by severity, risks, and a go/no-go recommendation with reasons.

## Which technique for which problem

| Situation | Technique |
|---|---|
| Ranges, lengths, limits | Boundary value analysis (min-1, min, min+1, max-1, max, max+1) |
| Many equivalent inputs | Equivalence partitioning: one value per class, valid and invalid |
| Several conditions combine into outcomes | Decision table |
| Behaviour depends on current state or history (order status, login, checkout) | State transition (cover every transition, plus invalid ones) |
| Many parameters with several values each | Pairwise (all pairs) instead of every combination |
| Unknown unknowns | Exploratory testing with charters, error guessing |
| Everything else | Requirement- and user-journey-based cases with traceability |

Details and worked examples: `references/techniques.md`.

## Writing a good test case

ID, title (behaviour under test), preconditions, steps (imperative, one action each), test data, expected result (observable and specific), priority, and the requirement it covers. One case checks one thing. A different person must be able to run it with no extra explanation. Write the unhappy path as carefully as the happy path: invalid input, missing permissions, network failure, double submit, concurrent edits, large data, timeouts.

## Writing a good bug report

Title states the symptom and place ("Checkout total ignores discount when cart has 2+ items"). Include: environment (build, browser/device, OS, account type), minimal steps to reproduce, expected vs actual result, frequency, evidence (screenshot, video, HAR, console/server log excerpt), and the impact. Search for duplicates first and verify on the latest build. One defect per report; no opinions about the cause unless confirmed.

**Severity** is impact on the product; **priority** is how soon to fix it. They differ.

| Severity | Meaning | Example |
|---|---|---|
| Critical | Data loss, security breach, system down, no workaround | Payment charged twice |
| Major | Core feature broken, workaround is hard | Cannot reset password |
| Minor | Feature works with a flaw or a simple workaround | Wrong sort order on a list |
| Trivial | Cosmetic | Misaligned icon |

## Release readiness

Typical exit criteria (adapt per project): all P1 cases executed and passing; no open Critical or Major defects; known Minor defects accepted by the product owner and documented; regression suite green on the release candidate; smoke test passed in the production-like environment; rollback plan verified. Use the checklists in `references/checklists.md` (web UI, API, accessibility, security smoke, performance smoke, compatibility, localisation).

## Principles

- Testing shows the presence of defects, not their absence; say what was **not** covered.
- Test early: review requirements and designs, ask "how would we test this?" before code exists.
- Keep tests independent, deterministic and data-isolated; a flaky test is a bug in the test and must be fixed or removed, not rerun until green.
- Only test systems you are authorised to test; security checks beyond a smoke level need written permission and a safe environment.

## Files

- `scripts/generate_test_cases.py` - boundary and equivalence cases from a JSON field spec (md, csv, json output)
- `assets/test-plan.md`, `assets/bug-report.md`, `assets/test-summary.md` - copy and fill in
- `references/techniques.md` - technique details and exploratory charters
- `references/checklists.md` - reusable checklists
