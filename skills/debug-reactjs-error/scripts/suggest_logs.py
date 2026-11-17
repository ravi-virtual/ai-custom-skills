#!/usr/bin/env python3
"""suggest_logs.py - propose where to add temporary debug logs in a React component/hook file.

Usage:
  python suggest_logs.py <file>

Prints JSON: a list of {"line", "type", "insert", "snippet"} sorted by line. Every snippet ends with
the cleanup marker `// [DEBUG]` so `cleanup_logs.py` can remove it afterwards.
Never log secrets: log whether a token/password exists (`!!token`), not its value.
"""
import json
import os
import re
import sys

MARKER = "// [DEBUG]"

# (type, regex matched per line, where to insert, snippet).
# Snippet placeholders: {name} = first captured group, {L} = line number.
RULES = [
    ('effect', r"\buseEffect\(", 'first line inside the effect', "console.log('[DEBUG] effect run @L{L}')"),
    ('async-fn', r"(?:const|let)\s+(\w+)\s*=\s*async\b|async\s+function\s+(\w+)", 'first line of the function (and log the result before returning)', "console.log('[DEBUG] {name} start')"),
    ('http-call', r"\bawait\s+(?:axios|api|fetch|\w+Api)\b[^;]*", 'line after the await', "console.log('[DEBUG] response @L{L}', typeof res !== 'undefined' ? res : '(assign the awaited value to inspect it)')"),
    ('dispatch', r"\bdispatch\((\w+)", 'line before the dispatch', "console.log('[DEBUG] dispatch {name}')"),
    ('catch', r"\bcatch\s*\((\w+)\)", 'first line inside the catch', "console.log('[DEBUG] caught', {name})"),
]


def suggest(path):
    if not os.path.isfile(path):
        return {"error": f"File not found: {path}"}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()

    found = []
    for idx, line in enumerate(lines, start=1):
        if MARKER in line:
            continue  # already instrumented
        for kind, regex, insert, snippet in RULES:
            m = re.search(regex, line)
            if not m:
                continue
            name = next((g for g in m.groups() if g), kind)
            found.append({
                "line": idx,
                "type": kind,
                "insert": insert,
                "snippet": snippet.replace("{name}", name).replace("{L}", str(idx)) + "; " + MARKER,
            })

    # One render snapshot listing every useState variable (placed before the first JSX return).
    state_vars = [m.group(1) for m in (re.search(r"const\s+\[(\w+)\s*,\s*\w+\]\s*=\s*useState", l) for l in lines) if m]
    if state_vars:
        for idx, line in enumerate(lines, start=1):
            if re.match(r"\s*return\s*(\(|<)", line) and MARKER not in line:
                found.append({
                    "line": idx,
                    "type": "render-snapshot",
                    "insert": "line before this return",
                    "snippet": "console.log('[DEBUG] render', { " + ", ".join(state_vars) + " }); " + MARKER,
                })
                break
    found.sort(key=lambda s: s["line"])
    if not found:
        return [{
            "line": 1,
            "type": "general",
            "insert": "top of file",
            "snippet": "console.log('[DEBUG] reached', __filename); " + MARKER,
        }]
    return found


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python suggest_logs.py <file>"}))
        sys.exit(1)
    result = suggest(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(1 if isinstance(result, dict) else 0)
