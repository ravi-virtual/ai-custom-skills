#!/usr/bin/env python3
"""generate_invoice.py - build a printable invoice (HTML + Markdown) from a JSON file, with exact money math.

Usage:
  python generate_invoice.py invoice.json [--out DIR]

Writes invoice-<number>.html (open in a browser, Print > Save as PDF) and invoice-<number>.md, and prints the totals.
Math uses Decimal with round-half-up to the cent: line = quantity * rate; discount and tax are percentages of
the subtotal / taxable amount; amount due = total - deposit_paid. All text is HTML-escaped.
See references/invoice.example.json. Tax rules differ by country: confirm required invoice fields, tax rates
and numbering with your accountant. Standard library only.
"""
import argparse
import datetime
import html
import json
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal("0.01")


def d(value, label):
    try:
        return Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"{label} is not a number: {value!r}")


def q(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def fmt(x, cur):
    return f"{cur} {x:,.2f}"


def compute(inv):
    cur = inv.get("currency", "USD")
    lines, subtotal = [], Decimal("0")
    if not inv.get("items"):
        raise ValueError("items must contain at least one line")
    for i, it in enumerate(inv["items"], 1):
        qty, rate = d(it.get("quantity", 1), f"items[{i}].quantity"), d(it.get("rate"), f"items[{i}].rate")
        if qty < 0 or rate < 0:
            raise ValueError(f"items[{i}]: quantity and rate must not be negative (use discount_percent or a credit note)")
        amount = q(qty * rate)
        subtotal += amount
        lines.append({"description": it.get("description", ""), "quantity": qty, "unit": it.get("unit", ""), "rate": q(rate), "amount": amount})
    disc_pct, tax_pct = d(inv.get("discount_percent", 0), "discount_percent"), d(inv.get("tax_percent", 0), "tax_percent")
    if not (0 <= disc_pct <= 100 and 0 <= tax_pct <= 100):
        raise ValueError("discount_percent and tax_percent must be between 0 and 100")
    discount = q(subtotal * disc_pct / 100)
    taxable = subtotal - discount
    tax = q(taxable * tax_pct / 100)
    total = taxable + tax
    paid = q(d(inv.get("deposit_paid", 0), "deposit_paid"))
    if paid > total:
        raise ValueError("deposit_paid exceeds the invoice total")
    return {"cur": cur, "lines": lines, "subtotal": subtotal, "discount": discount, "disc_pct": disc_pct, "tax": tax, "tax_pct": tax_pct,
            "total": total, "paid": paid, "due": total - paid}


def due_date(inv):
    issue = datetime.date.fromisoformat(inv.get("issue_date") or datetime.date.today().isoformat())
    if inv.get("due_date"):
        return issue, datetime.date.fromisoformat(inv["due_date"])
    return issue, issue + datetime.timedelta(days=int(inv.get("due_days", 14)))


def party(p):
    keys = ("name", "business", "company", "address", "email", "tax_id")
    return [str(p[k]) for k in keys if p.get(k)]


def to_markdown(inv, c, issue, due):
    cur = c["cur"]
    out = [f"# Invoice {inv['invoice_number']}", "", f"Issue date: {issue}  \nDue date: {due}", "",
           "**From**  \n" + "  \n".join(party(inv.get("freelancer", {}))), "",
           "**Bill to**  \n" + "  \n".join(party(inv.get("client", {}))), "",
           "| Description | Qty | Rate | Amount |", "|---|---:|---:|---:|"]
    for ln in c["lines"]:
        out.append(f"| {ln['description']} | {ln['quantity']:g} {ln['unit']} | {fmt(ln['rate'], cur)} | {fmt(ln['amount'], cur)} |")
    out += ["", f"Subtotal: {fmt(c['subtotal'], cur)}  "]
    if c["discount"]:
        out.append(f"Discount ({c['disc_pct']:g}%): -{fmt(c['discount'], cur)}  ")
    if c["tax_pct"]:
        out.append(f"{inv.get('tax_label', 'Tax')} ({c['tax_pct']:g}%): {fmt(c['tax'], cur)}  ")
    out.append(f"**Total: {fmt(c['total'], cur)}**  ")
    if c["paid"]:
        out.append(f"Already paid: -{fmt(c['paid'], cur)}  ")
    out += [f"**Amount due: {fmt(c['due'], cur)}**", ""]
    pay = inv.get("payment", {})
    if pay.get("methods"):
        out += ["## Payment", *[f"- {m}" for m in pay["methods"]], f"Reference: {pay.get('reference', 'Invoice ' + str(inv['invoice_number']))}", ""]
    for key in ("late_fee_note", "notes"):
        if inv.get(key):
            out += [str(inv[key]), ""]
    return "\n".join(out)


def to_html(inv, c, issue, due):
    e = lambda s: html.escape(str(s))  # noqa: E731
    cur = c["cur"]
    rows = "".join(f"<tr><td>{e(l['description'])}</td><td class=n>{l['quantity']:g} {e(l['unit'])}</td><td class=n>{e(fmt(l['rate'], cur))}</td><td class=n>{e(fmt(l['amount'], cur))}</td></tr>" for l in c["lines"])
    totals = [("Subtotal", fmt(c["subtotal"], cur))]
    if c["discount"]:
        totals.append((f"Discount ({c['disc_pct']:g}%)", "-" + fmt(c["discount"], cur)))
    if c["tax_pct"]:
        totals.append((f"{inv.get('tax_label', 'Tax')} ({c['tax_pct']:g}%)", fmt(c["tax"], cur)))
    totals.append(("Total", fmt(c["total"], cur)))
    if c["paid"]:
        totals.append(("Already paid", "-" + fmt(c["paid"], cur)))
    trows = "".join(f"<tr><td>{e(k)}</td><td class=n>{e(v)}</td></tr>" for k, v in totals)
    block = lambda title, p: f"<div><h3>{title}</h3>" + "<br>".join(e(x) for x in party(p)) + "</div>"  # noqa: E731
    pay = inv.get("payment", {})
    pay_html = ""
    if pay.get("methods"):
        pay_html = "<h3>Payment</h3><ul>" + "".join(f"<li>{e(m)}</li>" for m in pay["methods"]) + f"</ul><p>Reference: {e(pay.get('reference', 'Invoice ' + str(inv['invoice_number'])))}</p>"
    notes = "".join(f"<p class=small>{e(inv[k])}</p>" for k in ("late_fee_note", "notes") if inv.get(k))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Invoice {e(inv['invoice_number'])}</title>
<style>
body{{font:14px/1.5 system-ui,Segoe UI,Arial,sans-serif;color:#111;max-width:780px;margin:32px auto;padding:0 24px}}
h1{{font-size:28px;margin:0 0 4px}} h3{{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#555;margin:0 0 6px}}
.grid{{display:flex;justify-content:space-between;gap:24px;margin:24px 0}} table{{width:100%;border-collapse:collapse}}
th,td{{padding:8px 6px;border-bottom:1px solid #ddd;text-align:left}} th.n,td.n{{text-align:right;white-space:nowrap}}
.totals{{width:50%;margin-left:auto;margin-top:16px}} .due td{{font-weight:700;font-size:16px;border-top:2px solid #111}}
.small{{color:#555;font-size:12px}} @media print{{body{{margin:0}}}}
</style></head><body>
<h1>Invoice {e(inv['invoice_number'])}</h1>
<p class=small>Issue date: {issue} &nbsp;|&nbsp; Due date: {due}</p>
<div class=grid>{block('From', inv.get('freelancer', {}))}{block('Bill to', inv.get('client', {}))}</div>
<table><thead><tr><th>Description</th><th class=n>Qty</th><th class=n>Rate</th><th class=n>Amount</th></tr></thead><tbody>{rows}</tbody></table>
<table class=totals>{trows}<tr class=due><td>Amount due</td><td class=n>{e(fmt(c['due'], cur))}</td></tr></table>
{pay_html}{notes}
</body></html>
"""


def main():
    ap = argparse.ArgumentParser(description="Generate an invoice from JSON.")
    ap.add_argument("invoice")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    try:
        with open(args.invoice, encoding="utf-8") as fh:
            inv = json.load(fh)
        if not inv.get("invoice_number"):
            raise ValueError("invoice_number is required")
        if not re.fullmatch(r"[\w.-]+", str(inv["invoice_number"])):
            raise ValueError("invoice_number may only contain letters, digits, dot, dash and underscore")
        c = compute(inv)
        issue, due = due_date(inv)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, f"invoice-{inv['invoice_number']}")
    with open(base + ".html", "w", encoding="utf-8") as fh:
        fh.write(to_html(inv, c, issue, due))
    with open(base + ".md", "w", encoding="utf-8") as fh:
        fh.write(to_markdown(inv, c, issue, due))
    print(f"Wrote {base}.html and {base}.md")
    print(f"Subtotal {fmt(c['subtotal'], c['cur'])} | discount {fmt(c['discount'], c['cur'])} | tax {fmt(c['tax'], c['cur'])} | total {fmt(c['total'], c['cur'])} | due {fmt(c['due'], c['cur'])} by {due}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
