#!/usr/bin/env python3
"""generate_onboarding_kit.py - fill the client onboarding templates from one project file.

Usage:
  python generate_onboarding_kit.py project.json --out ./onboarding/acme [--only scope-of-work,welcome-email]

project.json (see references/project.example.json):
{
  "freelancer": {"name": "..."}, "client": {"name": "...", "company": "..."},
  "project": {"name": "...", "summary": "...", "start_date": "2026-12-01", "target_date": "2026-12-20"},
  "deliverables": ["..."], "out_of_scope": ["..."], "assumptions": ["..."], "access_needed": ["..."],
  "milestones": [{"name": "Discovery", "due": "2026-12-05", "amount": 500}],
  "currency": "USD",
  "payment_terms": {"deposit_percent": 30, "net_days": 7},
  "revisions_included": 2, "review_days": 3,
  "communication": {"channel": "Slack", "update_day": "Friday", "response_time": "1 business day"}
}
Templates live in ../assets/*.md and use {{dotted.keys}} plus computed fields (lists, milestone table,
totals). Anything that cannot be filled is written as [[MISSING: key]] and reported, so nothing is
silently invented. Standard library only.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
CENT = Decimal("0.01")


def money(x):
    return f"{Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP):,.2f}"


def bullets(items):
    return "\n".join(f"- {i}" for i in items) if items else "- (none listed)"


def computed(p):
    ms = p.get("milestones", [])
    total = sum((Decimal(str(m.get("amount", 0))) for m in ms), Decimal("0"))
    dep = Decimal(str(p.get("payment_terms", {}).get("deposit_percent", 0)))
    deposit = (total * dep / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    cur = p.get("currency", "USD")
    rows = ["| # | Milestone | Due | Amount |", "|---|---|---|---|"]
    rows += [f"| {i} | {m.get('name', '')} | {m.get('due', 'TBD')} | {cur} {money(m.get('amount', 0))} |" for i, m in enumerate(ms, 1)]
    if ms:
        rows.append(f"| | **Total** | | **{cur} {money(total)}** |")
    access = p.get("access_needed", [])
    company = p.get("client", {}).get("company")
    out = {
        "today": datetime.date.today().isoformat(),
        "client_company_suffix": f" ({company})" if company else "",
        "deliverables_list": bullets([f"{d}" for d in p.get("deliverables", [])]),
        "out_of_scope_list": bullets(p.get("out_of_scope", [])),
        "assumptions_list": bullets(p.get("assumptions", [])),
        "access_list": bullets(access),
        "access_inline": ", ".join(access) if access else "the tools and accounts we discussed",
        "milestones_table": "\n".join(rows) if ms else "[[MISSING: milestones]]",
        "total_amount": money(total) if ms else "[[MISSING: milestones]]",
        "deposit_sentence": (f"A deposit of {cur} {money(deposit)} ({dep:g}%) is due before work starts." if dep else "No deposit is required; each milestone is invoiced on completion."),
        "deposit_clause": (f" and the {dep:g}% deposit is received" if dep else ""),
        "intake_due": p.get("intake_due", "[[MISSING: intake_due]]"),
        "kickoff_length": p.get("kickoff_length", 30),
        "review_days": p.get("review_days", 3),
    }
    return out


def lookup(key, p, extra):
    if key in extra:
        return extra[key]
    cur = p
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def fill(text, p, extra):
    missing = []

    def sub(m):
        v = lookup(m.group(1), p, extra)
        if v is None or v == "":
            missing.append(m.group(1))
            return f"[[MISSING: {m.group(1)}]]"
        return str(v)
    result = re.sub(r"\{\{\s*([\w.]+)\s*\}\}", sub, text)
    missing += re.findall(r"\[\[MISSING: ([^\]]+)\]\]", result)   # markers coming from computed fields
    return result, missing


def main():
    ap = argparse.ArgumentParser(description="Fill onboarding templates from a project file.")
    ap.add_argument("project")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--only", help="comma-separated template names without .md")
    args = ap.parse_args()
    try:
        with open(args.project, encoding="utf-8") as fh:
            project = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: cannot read {args.project}: {exc}", file=sys.stderr)
        return 2
    extra = computed(project)
    wanted = set(args.only.split(",")) if args.only else None
    os.makedirs(args.out, exist_ok=True)
    all_missing = {}
    for path in sorted(glob.glob(os.path.join(ASSETS, "*.md"))):
        name = os.path.basename(path)[:-3]
        if wanted and name not in wanted:
            continue
        with open(path, encoding="utf-8") as fh:
            text, missing = fill(fh.read(), project, extra)
        with open(os.path.join(args.out, name + ".md"), "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {os.path.join(args.out, name + '.md')}")
        if missing:
            all_missing[name] = sorted(set(missing))
    if all_missing:
        print("\nFill these in (marked [[MISSING: ...]]):")
        for name, keys in all_missing.items():
            print(f"  {name}: {', '.join(keys)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
