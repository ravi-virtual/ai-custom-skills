#!/usr/bin/env python3
"""followup_schedule.py - decide which payment reminder each unpaid invoice needs today, and draft it.

Usage:
  python followup_schedule.py invoices.json [--today 2026-11-17] [--messages] [--json] [--sender "Alex Doe"]

invoices.json is a list of:
{"number": "2026-014", "client": "Jane Smith", "email": "jane@example.com", "amount": 941.25, "currency": "USD",
 "due_date": "2026-11-24", "status": "sent", "last_stage": "none"}
status: sent | paid | disputed | draft.   last_stage: the last reminder you sent (none, before, due, gentle, firm, final, escalate).

Stages by days relative to the due date:
  -3 before   friendly heads-up        0 due     due-today note       +3 gentle   polite reminder
  +7 firm     clear request + date     +14 final pause-work notice      +30 escalate formal demand / next steps
Only the highest stage reached and not yet sent is proposed. Paid and draft invoices are skipped; disputed
invoices get "resolve the dispute", never a reminder. Messages are drafts for you to review and send yourself.
"""
import argparse
import datetime
import json
import sys
from collections import defaultdict

STAGES = [("before", -3), ("due", 0), ("gentle", 3), ("firm", 7), ("final", 14), ("escalate", 30)]
ORDER = {"none": -1, **{name: i for i, (name, _) in enumerate(STAGES)}}

TEMPLATES = {
    "before": ("Invoice {number} is due on {due}", "Hi {client},\n\nA quick heads-up that invoice {number} for {currency} {amount} is due on {due}. Payment details are on the invoice; let me know if you need anything from my side to process it.\n\nThanks,\n{sender}"),
    "due": ("Invoice {number} is due today", "Hi {client},\n\nInvoice {number} ({currency} {amount}) is due today. If it is already on its way, thank you and please ignore this note.\n\nBest,\n{sender}"),
    "gentle": ("Reminder: invoice {number} ({days} days overdue)", "Hi {client},\n\nI don't have a payment recorded for invoice {number} ({currency} {amount}, due {due}). It may have crossed paths with your payment; if not, could you confirm when I can expect it? I'm happy to resend the invoice or payment details.\n\nThanks,\n{sender}"),
    "firm": ("Overdue invoice {number}: payment needed by {deadline}", "Hi {client},\n\nInvoice {number} ({currency} {amount}) is now {days} days past its due date of {due}. Please arrange payment by {deadline}, or tell me today if there is a problem with the invoice so we can sort it out.\n\nThank you,\n{sender}"),
    "final": ("Final notice: invoice {number} is {days} days overdue", "Hi {client},\n\nI haven't received payment or a reply regarding invoice {number} ({currency} {amount}, due {due}). If it is not settled by {deadline}, I will have to pause work on the project and apply any late-payment terms in our agreement. I would much prefer to resolve this directly. Can we speak this week?\n\nRegards,\n{sender}"),
    "escalate": ("Formal notice: invoice {number} remains unpaid", "Dear {client},\n\nInvoice {number} ({currency} {amount}) has been unpaid for {days} days despite earlier reminders. Please pay in full by {deadline}. Otherwise I will proceed with the next steps available under our agreement, which may include a formal demand, the platform's dispute process, or a collections or legal route.\n\nRegards,\n{sender}"),
}


def stage_for(days_from_due):
    reached = None
    for name, offset in STAGES:
        if days_from_due >= offset:
            reached = name
    return reached


def plan(invoices, today, sender):
    actions, skipped, totals = [], [], defaultdict(float)
    for inv in invoices:
        status = inv.get("status", "sent")
        label = f"{inv.get('number')} ({inv.get('client')})"
        if status in ("paid", "draft"):
            skipped.append(f"{label}: {status}")
            continue
        due = datetime.date.fromisoformat(inv["due_date"])
        days = (today - due).days
        totals[inv.get("currency", "")] += float(inv.get("amount", 0))
        if status == "disputed":
            actions.append({"invoice": inv["number"], "client": inv.get("client"), "stage": "dispute", "days_overdue": days,
                            "advice": "Disputed: do not send reminders. Ask for the specific objection in writing, offer a call, correct the invoice or agree a settlement."})
            continue
        stage = stage_for(days)
        last = ORDER.get(inv.get("last_stage", "none"), -1)
        if stage is None:
            skipped.append(f"{label}: not due until {due} (first reminder 3 days before)")
            continue
        if ORDER[stage] <= last:
            skipped.append(f"{label}: '{inv.get('last_stage')}' reminder already sent; next stage after day {STAGES[min(ORDER[stage] + 1, len(STAGES) - 1)][1]}")
            continue
        deadline = today + datetime.timedelta(days=5 if stage in ("firm", "final", "escalate") else 3)
        subject, body = TEMPLATES[stage]
        ctx = dict(number=inv["number"], client=inv.get("client", "there"), amount=f"{float(inv.get('amount', 0)):,.2f}", currency=inv.get("currency", ""),
                   due=due.isoformat(), days=max(days, 0), deadline=deadline.isoformat(), sender=sender)
        actions.append({"invoice": inv["number"], "client": inv.get("client"), "email": inv.get("email"), "stage": stage, "days_overdue": days,
                        "subject": subject.format(**ctx), "body": body.format(**ctx)})
    actions.sort(key=lambda a: -a["days_overdue"])
    return actions, skipped, dict(totals)


def main():
    ap = argparse.ArgumentParser(description="Plan payment reminders.")
    ap.add_argument("invoices")
    ap.add_argument("--today", help="ISO date to plan for (default: today)")
    ap.add_argument("--messages", action="store_true", help="include drafted subject and body")
    ap.add_argument("--sender", default="[Your name]")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        with open(args.invoices, encoding="utf-8") as fh:
            invoices = json.load(fh)
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
        actions, skipped, totals = plan(invoices, today, args.sender)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"Error: {exc!r}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"today": today.isoformat(), "actions": actions, "skipped": skipped, "outstanding": totals}, indent=2))
        return 0
    print(f"Payment follow-ups as of {today}\n")
    if not actions:
        print("Nothing to send today.")
    for a in actions:
        late = f"{a['days_overdue']} days overdue" if a["days_overdue"] > 0 else ("due today" if a["days_overdue"] == 0 else f"due in {-a['days_overdue']} days")
        print(f"- {a['invoice']} | {a['client']} | {late} | stage: {a['stage'].upper()}")
        if a["stage"] == "dispute":
            print(f"    {a['advice']}")
        elif args.messages:
            print(f"    To: {a.get('email') or '(no email on file)'}\n    Subject: {a['subject']}\n" + "\n".join("    " + line for line in a["body"].splitlines()) + "\n")
    if skipped:
        print("\nSkipped:")
        print("\n".join("  " + s for s in skipped))
    print("\nOutstanding: " + (", ".join(f"{cur} {v:,.2f}" for cur, v in totals.items()) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
