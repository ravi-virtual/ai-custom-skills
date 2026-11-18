#!/usr/bin/env python3
"""check_proposal.py - lint a freelance proposal draft before a human sends it.

Usage:
  python check_proposal.py proposal.txt [--job job.txt] [--json]

Errors (exit code 1): unfilled placeholders, contact details that bypass the platform.
Warnings: length, generic opening, no client-specific hook, no question, no next step, self-focus,
no evidence, cliches/guarantees. Heuristics only: a human reads it last.
"""
import argparse
import json
import re
import sys

GENERIC_OPENERS = [r"^\s*(dear (sir|madam|hiring manager|client)|hello sir|hi sir|greetings)", r"i am writing to (apply|express)", r"i came across your (job|post|listing)",
                   r"i am (the )?(perfect|ideal|best) (fit|candidate|choice)", r"as per your (job )?description", r"i have read your (job )?(post|description|requirements)"]
CLICHES = [r"\bperfect fit\b", r"\bbest in (the )?(class|world)\b", r"100% (satisfaction|guarantee)", r"\bguarantee[sd]?\b", r"\bunbeatable\b", r"\b(top|best) rated freelancer\b", r"\bi can do (it|this) (very )?(cheap|cheaply|fast)\b"]
STOP = set("""the and for with that this from your you are will have has been our their about into more than then them they what when where which who how can could would should need needs looking want wants work working project job please using use make made also must very just such like some any all new""".split())


def tokens(text):
    return [w for w in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{3,}", text.lower()) if w not in STOP]


def check(text, job=None):
    errors, warnings, notes = [], [], []
    wc = len(re.findall(r"\w+", text))
    if wc < 80:
        warnings.append(f"Only {wc} words: too thin to show you understood the problem (aim for roughly 120 to 250).")
    elif wc > 300:
        warnings.append(f"{wc} words: long. Clients skim; cut to what proves fit and next steps (roughly 120 to 250).")

    first = " ".join(text.strip().split()[:45])
    for pat in GENERIC_OPENERS:
        if re.search(pat, text.strip()[:200], re.I):
            warnings.append("Generic opening. Start with the client's problem in their words; the first two lines are what they see in the list.")
            break

    if job:
        job_terms = {t for t in tokens(job)}
        overlap = sorted(job_terms & set(tokens(first)))
        if len(overlap) < 2:
            warnings.append("The opening shares fewer than 2 distinctive terms with the job post; mirror the client's specific problem up front.")
        else:
            notes.append("Opening echoes the job: " + ", ".join(overlap[:6]))

    if "?" not in text:
        warnings.append("No question. One or two sharp clarifying questions show expertise and invite a reply.")
    if not re.search(r"\b(call|chat|meet|discuss|available|next step|let me know|happy to|walk (you )?through|schedule)\b", text, re.I):
        warnings.append("No clear next step. End with one easy action (a short call, a question to answer).")

    me = len(re.findall(r"\b(i|i'm|i've|my|me|mine)\b", text, re.I))
    you = len(re.findall(r"\b(you|your|you're|yours|you've)\b", text, re.I))
    if me > 2 * max(you, 1) and me > 8:
        warnings.append(f"Self-focused ({me} I/my vs {you} you/your). Rewrite around the client's outcome.")

    if not (re.search(r"\d+\s?%|\$\s?\d|\b\d{2,}\b|https?://", text)):
        warnings.append("No evidence (number, result, link). Add one measurable outcome or a relevant sample.")

    for pat in CLICHES:
        if re.search(pat, text, re.I):
            warnings.append("Cliche or guarantee detected (" + re.search(pat, text, re.I).group(0) + "). Replace with a specific, provable claim.")
            break

    ph = re.findall(r"\[[^\]]{1,60}\]|\{\{[^}]+\}\}|<[A-Za-z ]{2,30}>|\bTODO\b|\bXXX+\b", text)
    if ph:
        errors.append("Unfilled placeholder(s): " + ", ".join(sorted(set(ph))[:6]))
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d\s().-]{8,}\d|whatsapp|telegram|skype", text, re.I):
        errors.append("Contact details or off-platform channel found; most platforms forbid this before a contract. Remove it.")
    return {"words": wc, "errors": errors, "warnings": warnings, "notes": notes}


def main():
    ap = argparse.ArgumentParser(description="Lint a freelance proposal.")
    ap.add_argument("proposal")
    ap.add_argument("--job", help="job post text, to check the opening mirrors it")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        text = open(args.proposal, encoding="utf-8").read()
        job = open(args.job, encoding="utf-8").read() if args.job else None
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    r = check(text, job)
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['words']} words")
        for e in r["errors"]:
            print("ERROR  ", e)
        for w in r["warnings"]:
            print("WARNING", w)
        for n in r["notes"]:
            print("NOTE   ", n)
        if not (r["errors"] or r["warnings"]):
            print("No issues found. Read it aloud once, then send it yourself.")
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
