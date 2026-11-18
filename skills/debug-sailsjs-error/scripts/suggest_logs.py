#!/usr/bin/env python3
"""suggest_logs.py - propose where to add temporary debug logs in a Sails.js action/helper/model/policy file.

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
    ('action-fn', r"\bfn:\s*async\s+function\s*\(\s*(?:inputs|\{[^}]*\})?[^)]*\)", 'first line inside fn', "console.log('[DEBUG] fn inputs @L{L}', typeof inputs !== 'undefined' ? inputs : '(destructured: log the names)')"),
    ('controller-action', r"^\s*(\w+)\s*:\s*async\s+function\s*\(\s*req\s*,\s*res", 'first line inside the action', "console.log('[DEBUG] {name}', { params: req.allParams ? req.allParams() : req.params, user: req.me || req.user })"),
    ('waterline-query', r"\bawait\s+(\w+)\.(?:find|findOne|create|createEach|update|updateOne|destroy|destroyOne|count|sum)\b", 'line after the await (assign the result to inspect it)', "console.log('[DEBUG] {name} query done @L{L}')"),
    ('exit', r"\b(?:exits|res)\.(?:success|error|ok|badRequest|notFound|serverError|forbidden)\(", 'line before the exit', "console.log('[DEBUG] exiting @L{L}')"),
    ('lifecycle', r"\b((?:before|after)(?:Create|Update|Destroy|Validate))\s*:", 'first line inside the callback', "console.log('[DEBUG] {name}', arguments[0])"),
    ('policy', r"module\.exports\s*=\s*(?:async\s+)?function\s*\(\s*req\s*,\s*res\s*,\s*(proceed|next)", 'first line inside the policy', "console.log('[DEBUG] policy', req.method, req.path, 'user:', req.me && req.me.id)"),
    ('catch', r"\bcatch\s*\((\w+)\)", 'first line inside the catch', "console.log('[DEBUG] caught', {name}.name, {name}.message)"),
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
