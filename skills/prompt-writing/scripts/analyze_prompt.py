#!/usr/bin/env python3
"""analyze_prompt.py - structural lint for an LLM prompt.

Usage:
  python analyze_prompt.py prompt.txt [--json] [--strict]
  cat prompt.txt | python analyze_prompt.py - [--json]

Checks (heuristics, not a quality judgment):
  context/role, explicit task verb, output format, delimiters/XML tags, examples,
  vague wording, unresolved placeholders, prompt length, prohibition-only rules.
Exit code: 0 normally; with --strict, 1 if any warning was found.
"""
import argparse
import json
import re
import sys

VAGUE = ["good", "nice", "briefly", "short", "long", "etc", "and so on", "appropriate",
         "as needed", "relevant", "stuff", "things", "some", "better", "high quality"]
TASK_VERBS = ["write", "create", "classify", "extract", "summarize", "summarise", "analyze", "analyse",
              "translate", "generate", "answer", "explain", "review", "list", "compare", "rewrite",
              "identify", "convert", "draft", "evaluate", "rate", "decide", "return", "respond"]


def has(text, words):
    return any(re.search(r"\b" + re.escape(w) + r"\b", text, re.IGNORECASE) for w in words)


def analyze(text):
    findings = []  # (severity, code, message)
    words = re.findall(r"\w+", text)

    if len(words) < 15:
        findings.append(("warn", "too-short", "Very short prompt (<15 words). Add context, constraints and the expected output."))
    if len(words) > 1500:
        findings.append(("info", "very-long", "Prompt exceeds ~1500 words. Consider splitting it into chained prompts or moving reference text into the input."))

    if not (re.search(r"\byou are\b|\bact as\b|\byour (?:role|job|task|goal)\b", text, re.I)
            or has(text, ["context", "background", "audience"])):
        findings.append(("warn", "no-context", "No role or context found. State who/what this is for and why; purpose improves judgment calls."))

    if not has(text, TASK_VERBS):
        findings.append(("warn", "no-task", "No clear task verb (write, classify, extract...). State the job as an instruction."))

    if not (has(text, ["format", "json", "markdown", "table", "bullet", "bullets", "schema", "yaml", "csv", "sentences", "words", "paragraph", "paragraphs", "headings"])):
        findings.append(("warn", "no-format", "No output format specified. Say exactly what the answer should look like (shape, length, language)."))

    if not (re.search(r"</?[A-Za-z_][\w-]*>", text) or '"""' in text or re.search(r"^#{1,3} \w", text, re.M) or "```" in text):
        findings.append(("warn", "no-delimiters", "No delimiters or XML tags. Fence variable input (e.g. <document>...</document>) so it cannot be confused with instructions."))

    if not re.search(r"<example|\bexample\b|\be\.g\.|\bfor instance\b|^input:", text, re.I | re.M):
        findings.append(("info", "no-examples", "No examples. For hard-to-describe formats or tone, add 2-5 varied examples."))

    placeholders = re.findall(r"\{\{[^}]*\}\}|\[(?:TODO|TBD|INSERT[^\]]*|YOUR[^\]]*)\]", text, re.I)
    if placeholders:
        findings.append(("info", "placeholders", f"Unresolved placeholders present ({', '.join(sorted(set(placeholders))[:5])}). Fine for a template; fill them before sending."))

    vague = [w for w in VAGUE if re.search(r"\b" + re.escape(w) + r"\b", text, re.I)]
    if vague:
        findings.append(("warn", "vague", f"Vague wording: {', '.join(vague)}. Replace with measurable terms (e.g. 'max 80 words')."))

    negatives = len(re.findall(r"\b(?:do not|don't|never|avoid|must not)\b", text, re.I))
    positives = len(re.findall(r"\b(?:always|must|should|use|include|answer|return|respond)\b", text, re.I))
    if negatives >= 3 and negatives > positives:
        findings.append(("warn", "prohibitions", "Mostly prohibitions. Rephrase as what to do instead; add the reason behind important rules."))

    shouting = re.findall(r"\b[A-Z]{5,}\b", text)
    if len(shouting) >= 3:
        findings.append(("info", "shouting", "Several ALL-CAPS words. Prefer explaining why a rule matters over emphasis."))
    return findings


def main():
    ap = argparse.ArgumentParser(description="Structural lint for an LLM prompt.")
    ap.add_argument("file", help="prompt file, or - for stdin")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any warning is found")
    args = ap.parse_args()

    try:
        text = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    except OSError as exc:
        print(f"Error reading {args.file}: {exc}", file=sys.stderr)
        return 2

    findings = analyze(text)
    if args.json:
        print(json.dumps([{"severity": s, "code": c, "message": m} for s, c, m in findings], indent=2))
    else:
        n_words = len(re.findall(r"\w+", text))
        print(f"--- Prompt analysis: {args.file} ({n_words} words) ---")
        if not findings:
            print("No structural issues found. Now test it on real inputs.")
        for sev, code, msg in findings:
            print(f"[{sev.upper():4}] {code}: {msg}")
    return 1 if args.strict and any(s == "warn" for s, _, _ in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
