---
name: freelance-invoicing-followups
description: Creates correct freelance invoices and manages getting paid - invoices from time or milestones with exact rounding, discounts, tax and deposits as printable HTML or Markdown, payment terms, a reminder cadence with ready-to-send messages for early, due, overdue, final and escalation stages, handling disputes, and record keeping. Use when the user needs to bill a client, turn hours or milestones into an invoice, check invoice math, chase an unpaid invoice, write a polite or firm payment reminder, set late-fee or deposit terms, or review which invoices are outstanding. Not tax or legal advice.
---

# Freelance Invoicing and Follow-ups

Bill promptly, make paying easy, and follow up on a schedule instead of on a mood.

## Workflow: invoice

1. **Gather** (ask for what is missing, never guess numbers): invoice number, issue date, payment terms (days or due date), currency, both parties' details, line items (description, quantity, rate), discount, tax rate and label, deposit already paid, payment methods and reference.
2. **Write `invoice.json`** from `references/invoice.example.json`.
3. **Generate:** `python scripts/generate_invoice.py invoice.json --out ./invoices`. Writes `invoice-<number>.html` (open in a browser and print to PDF) and `.md`, and prints subtotal, discount, tax, total and amount due. Math is exact decimal with round-half-up to the cent; all text is escaped.
4. **Sanity-check** the printed totals against the source (hours, milestone amounts, deposit) before sending, and confirm the details your country requires on an invoice (legal names and addresses, tax ID, sequential numbering, tax breakdown) with an accountant.
5. **Send** with a short message: what the invoice covers, amount, due date, how to pay. Send milestone invoices when the milestone is accepted, not weeks later. On a platform with built-in billing and escrow, use that instead.

## Workflow: getting paid

1. Keep a simple register (JSON or spreadsheet) of invoices: number, client, email, amount, currency, due date, status, last reminder stage.
2. **Plan reminders:** `python scripts/followup_schedule.py invoices.json --messages --sender "Your Name"`. It picks the stage each unpaid invoice has reached and drafts the message; add `--today YYYY-MM-DD` to preview a date and `--json` for automation.

   | Day vs due date | Stage | Tone and purpose |
   |---|---|---|
   | -3 | before | friendly heads-up |
   | 0 | due | due-today note |
   | +3 | gentle | assume it crossed in the post; offer to resend |
   | +7 | firm | clear request with a deadline |
   | +14 | final | pause work and apply agreed late terms, offer a call |
   | +30 | escalate | formal notice of next steps under the agreement |

3. **Review each draft and send it yourself.** Reminders are drafts: check the facts, the tone for this client, and whether anything changed (partial payment, dispute). Update `last_stage` after sending.
4. **Disputes:** stop reminders. Ask for the specific objection in writing, offer a call, fix errors fast, and agree a documented resolution (corrected invoice, credit, payment plan). Keep calm, factual records.
5. **Reconcile** payments against invoices each week; mark paid, send a short thank-you receipt.

## Terms that reduce late payment

- Net 7 to 14 days for small projects (adapt to the client and norms); due date written on the invoice.
- Deposit and milestone billing for new clients; work on the next milestone starts when the previous invoice is settled.
- Late-payment clause in the scope of work or contract (interest or fee, within what the law in your jurisdiction allows) and the right to pause work.
- Easy payment: bank details or a payment link on the invoice, a clear reference, and the currency stated.
- Invoice on time and to the right person (accounts payable, with a purchase order number if the client uses them).

## Principles

- Accuracy first: show every line, rate and total so the client can approve without questions.
- Same cadence for everyone; adjust tone, not the rules.
- Never threaten something you will not do; escalate only through channels the agreement or platform provides.
- Keep invoices, agreements and payment records for the period your tax authority requires.

## Boundaries

This skill produces billing documents and drafts. Tax treatment, invoice legal requirements, interest and debt collection rules vary by country and client type: confirm with an accountant or lawyer for anything beyond routine invoicing.

## Files

- `scripts/generate_invoice.py` - invoice HTML and Markdown with exact totals
- `scripts/followup_schedule.py` - reminder planner and message drafts
- `references/invoice.example.json` - complete example input
- `references/reminder-templates.md` - editable message wording for each stage, plus dispute and thank-you notes
