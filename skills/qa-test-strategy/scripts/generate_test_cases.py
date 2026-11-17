#!/usr/bin/env python3
"""generate_test_cases.py - derive field-level test cases from a spec (boundary values + equivalence classes).

Usage:
  python generate_test_cases.py spec.json [--format md|csv|json] [--out FILE]

spec.json:
{
  "feature": "Sign-up form",
  "fields": [
    {"name": "age", "type": "integer", "min": 18, "max": 65, "required": true},
    {"name": "email", "type": "email", "required": true},
    {"name": "username", "type": "string", "min_length": 3, "max_length": 20, "pattern": "^[a-z0-9_]+$"},
    {"name": "plan", "type": "enum", "values": ["free", "pro"]},
    {"name": "newsletter", "type": "boolean"}
  ]
}
Types: integer, number, string, email, enum, boolean, date (ISO yyyy-mm-dd; optional min/max dates).
Every case has: id, field, technique, input, expected (valid | invalid), priority (P1 boundaries and
required-ness, P2 classes, P3 hostile/odd input). Expected results describe field validity only; add
the business outcome (message, state change) when you turn these into executable tests.
"""
import argparse
import csv
import datetime as dt
import io
import json
import re
import sys

HOSTILE = [
    ("script injection", "<script>alert(1)</script>"),
    ("SQL metacharacters", "' OR '1'='1' --"),
    ("unicode / emoji", "Zoë 😀 日本語"),
    ("leading/trailing spaces", "  padded  "),
]


def case(field, technique, value, expected, priority):
    return {"field": field, "technique": technique, "input": value, "expected": expected, "priority": priority}


def numeric_cases(f, name, integer):
    lo, hi = f.get("min"), f.get("max")
    step = 1 if integer else 0.01
    out = []
    if lo is not None:
        out += [case(name, "boundary: min-1", lo - step, "invalid", "P1"), case(name, "boundary: min", lo, "valid", "P1"),
                case(name, "boundary: min+1", lo + step, "valid", "P1")]
    if hi is not None:
        out += [case(name, "boundary: max-1", hi - step, "valid", "P1"), case(name, "boundary: max", hi, "valid", "P1"),
                case(name, "boundary: max+1", hi + step, "invalid", "P1")]
    if lo is not None and hi is not None:
        out.append(case(name, "equivalence: typical value", (lo + hi) // 2 if integer else (lo + hi) / 2, "valid", "P2"))
    elif not out:
        out.append(case(name, "equivalence: typical value", 1, "valid", "P2"))
    out += [case(name, "equivalence: zero", 0, "valid" if (lo is None or lo <= 0) and (hi is None or hi >= 0) else "invalid", "P2"),
            case(name, "equivalence: negative", -1, "valid" if lo is None or lo <= -1 else "invalid", "P2"),
            case(name, "equivalence: non-numeric text", "abc", "invalid", "P2")]
    if integer:
        out.append(case(name, "equivalence: decimal for integer field", 1.5, "invalid", "P2"))
    out.append(case(name, "error guessing: very large number", 10 ** 15, "invalid" if hi is not None else "valid", "P3"))
    return out


def string_cases(f, name):
    lo, hi = f.get("min_length"), f.get("max_length")
    out = []
    if lo is not None:
        out += [case(name, "boundary: length min-1", "a" * max(lo - 1, 0), "invalid" if lo > 0 else "valid", "P1"),
                case(name, "boundary: length min", "a" * lo, "valid", "P1")]
    if hi is not None:
        out += [case(name, "boundary: length max", "a" * hi, "valid", "P1"), case(name, "boundary: length max+1", "a" * (hi + 1), "invalid", "P1")]
    out.append(case(name, "equivalence: typical value", "valid_value", "valid", "P2"))
    if f.get("pattern"):
        out.append(case(name, "equivalence: violates pattern " + f["pattern"], "INVALID value!", "invalid" if not re.fullmatch(f["pattern"], "INVALID value!") else "valid", "P2"))
    for label, value in HOSTILE:
        out.append(case(name, "error guessing: " + label, value, "invalid" if f.get("pattern") and not re.fullmatch(f["pattern"], value) else "valid (must be stored/escaped safely)", "P3"))
    return out


def email_cases(name):
    return [case(name, "equivalence: valid address", "user@example.com", "valid", "P2"),
            case(name, "equivalence: plus addressing", "user+tag@example.com", "valid", "P2"),
            case(name, "equivalence: missing @", "userexample.com", "invalid", "P1"),
            case(name, "equivalence: missing domain", "user@", "invalid", "P1"),
            case(name, "equivalence: missing local part", "@example.com", "invalid", "P1"),
            case(name, "equivalence: contains space", "us er@example.com", "invalid", "P2"),
            case(name, "boundary: very long address (>254 chars)", "a" * 250 + "@example.com", "invalid", "P3"),
            case(name, "error guessing: mixed case", "User@Example.COM", "valid (decide if case-insensitive)", "P3")]


def enum_cases(f, name):
    out = [case(name, "equivalence: each allowed value", v, "valid", "P1") for v in f.get("values", [])]
    out += [case(name, "equivalence: value not in list", "__not_allowed__", "invalid", "P1")]
    if f.get("values") and isinstance(f["values"][0], str):
        out.append(case(name, "error guessing: wrong case", f["values"][0].upper() if f["values"][0] != f["values"][0].upper() else f["values"][0].lower(), "invalid (unless case-insensitive)", "P3"))
    return out


def date_cases(f, name):
    lo, hi = f.get("min"), f.get("max")
    out = [case(name, "equivalence: valid date", "2024-06-15", "valid", "P2"),
           case(name, "equivalence: impossible date", "2024-02-30", "invalid", "P1"),
           case(name, "equivalence: wrong format", "15/06/2024", "invalid", "P2"),
           case(name, "boundary: leap day", "2024-02-29", "valid", "P2"),
           case(name, "boundary: non-leap Feb 29", "2023-02-29", "invalid", "P2")]
    for key, label in (("min", "min"), ("max", "max")):
        v = f.get(key)
        if v:
            d = dt.date.fromisoformat(v)
            below, above = d - dt.timedelta(days=1), d + dt.timedelta(days=1)
            if key == "min":
                out += [case(name, "boundary: day before min", below.isoformat(), "invalid", "P1"), case(name, "boundary: min", v, "valid", "P1")]
            else:
                out += [case(name, "boundary: max", v, "valid", "P1"), case(name, "boundary: day after max", above.isoformat(), "invalid", "P1")]
    return out


def generate(spec):
    cases = []
    for f in spec["fields"]:
        name, typ = f["name"], f.get("type", "string")
        if typ == "integer":
            cs = numeric_cases(f, name, True)
        elif typ == "number":
            cs = numeric_cases(f, name, False)
        elif typ == "email":
            cs = email_cases(name)
        elif typ == "enum":
            cs = enum_cases(f, name)
        elif typ == "boolean":
            cs = [case(name, "equivalence: true", True, "valid", "P2"), case(name, "equivalence: false", False, "valid", "P2"),
                  case(name, "equivalence: non-boolean text", "maybe", "invalid", "P2")]
        elif typ == "date":
            cs = date_cases(f, name)
        elif typ == "string":
            cs = string_cases(f, name)
        else:
            raise SystemExit(f"Unknown field type '{typ}' for field '{name}'.")
        if f.get("required"):
            cs += [case(name, "required: empty string", "", "invalid", "P1"), case(name, "required: missing/null", None, "invalid", "P1")]
            if typ in ("string", "email"):
                cs.append(case(name, "required: whitespace only", "   ", "invalid", "P1"))
        else:
            cs.append(case(name, "optional: omitted", None, "valid", "P2"))
        cases += cs
    for i, c in enumerate(cases, 1):
        c["id"] = f"TC-{i:03d}"
    return cases


def render(cases, fmt, feature):
    cols = ["id", "field", "technique", "input", "expected", "priority"]
    if fmt == "json":
        return json.dumps(cases, indent=2, ensure_ascii=False)
    if fmt == "csv":
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=cols)
        w.writeheader()
        for c in cases:
            w.writerow({**c, "input": json.dumps(c["input"], ensure_ascii=False)})
        return buf.getvalue()
    esc = lambda v: json.dumps(v, ensure_ascii=False).replace("|", "\\|")  # noqa: E731
    lines = [f"# Field test cases: {feature}", "", f"{len(cases)} cases", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for c in cases:
        lines.append(f"| {c['id']} | {c['field']} | {c['technique']} | `{esc(c['input'])}` | {c['expected']} | {c['priority']} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Generate boundary/equivalence test cases from a field spec.")
    ap.add_argument("spec")
    ap.add_argument("--format", choices=["md", "csv", "json"], default="md")
    ap.add_argument("--out")
    args = ap.parse_args()
    try:
        with open(args.spec, encoding="utf-8") as fh:
            spec = json.load(fh)
        cases = generate(spec)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"Error: cannot use {args.spec}: {exc!r}", file=sys.stderr)
        return 1
    text = render(cases, args.format, spec.get("feature", "feature"))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {len(cases)} cases to {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
