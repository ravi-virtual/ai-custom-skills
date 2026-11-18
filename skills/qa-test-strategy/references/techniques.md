# Test Design Techniques

## Contents
- [Equivalence partitioning and boundary values](#equivalence-partitioning-and-boundary-values)
- [Decision tables](#decision-tables)
- [State transition testing](#state-transition-testing)
- [Pairwise testing](#pairwise-testing)
- [Exploratory testing](#exploratory-testing)
- [Error guessing prompts](#error-guessing-prompts)
- [Traceability](#traceability)

## Equivalence partitioning and boundary values

Split inputs into classes the system should treat identically, then test one value per class. Defects cluster at the edges, so add boundary values.

Example: discount for order total, 0 to 99.99 gets 0%, 100 to 499.99 gets 5%, 500 and above gets 10%.
- Classes: negative (invalid), 0 to 99.99, 100 to 499.99, 500+, non-numeric (invalid).
- Boundaries: -0.01, 0, 0.01, 99.99, 100, 100.01, 499.99, 500, 500.01.
- Do not forget precision and rounding (2 decimals, currency), and maximum sizes.

## Decision tables

Use when combinations of conditions produce different results. List conditions as rows and rules as columns, then check every column is reachable and that no combination is missing.

| Conditions | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Logged in | Y | Y | N | N |
| Has coupon | Y | N | Y | N |
| **Actions** | | | | |
| Apply discount | X | | | |
| Show login prompt | | | X | X |

N conditions give 2^N rules; collapse rules whose outcome does not depend on a condition ("don't care"). Each remaining rule is a test.

## State transition testing

Model states, events and transitions (for example order: Created, Paid, Shipped, Delivered, Cancelled, Refunded). Derive tests for: every valid transition; every invalid transition (event not allowed in that state, expect a clear refusal and no state change); sequences (Created, Paid, Cancelled, Refunded); repeated events (double click on Pay, duplicate webhook); and timeouts or expirations. Check side effects too (emails, stock, ledger entries).

## Pairwise testing

When parameters have several values each (browser x OS x language x plan), full combinations explode. Cover every pair of values at least once with far fewer cases (tools: PICT, AllPairs, or any pairwise generator). Add the known-risky full combinations by hand. Use it for configuration matrices, not for logic with dependencies (use a decision table there).

## Exploratory testing

Simultaneous learning, test design and execution, guided by a **charter** and a timebox (60 to 90 minutes).

Charter template: *Explore* <area/feature> *with* <resources, data, tools, personas> *to discover* <risk, information>.
Examples: "Explore the checkout with an expired card, coupon stacking and back-button use to discover payment-state errors." "Explore CSV import with malformed, huge and non-UTF-8 files to discover crashes and data corruption."

Notes during a session: what was covered, bugs found (with IDs), questions raised, ideas for next sessions, and the time split between setup, testing and bug investigation.

Product-element heuristic **SFDIPOT**: Structure, Function, Data, Interfaces, Platform, Operations, Time. Ask what each means for the feature to generate ideas.

## Error guessing prompts

- Empty, null, whitespace, very long, special characters, emoji, right-to-left text
- Zero, negative, huge numbers, decimals, rounding, currency and units
- Dates: leap days, month ends, daylight-saving changes, time zones, past and future, epoch limits
- Double submit, rapid clicks, back/forward/refresh mid-flow, two tabs, two users editing the same record
- Slow or lost network, timeouts, server errors, partial failures, retries creating duplicates
- Permissions: other user's data via URL/ID change, logged-out access, role changes mid-session
- Large lists, pagination edges (empty, one, exact page size, last page), sorting stability
- File upload: wrong type, empty file, huge file, duplicate name, interrupted upload

## Traceability

Map each requirement or acceptance criterion to at least one test case and each case back to a requirement. Gaps in either direction are findings: untested requirements, or tests with no purpose.
