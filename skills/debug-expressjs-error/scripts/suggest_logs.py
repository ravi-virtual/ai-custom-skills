#!/usr/bin/env python3
"""suggest_logs.py - propose where to add temporary debug logs in a Express route/controller/middleware file.

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
    ('handler', r"(?:(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?\(?\s*req\s*,\s*res|function\s+(\w+)\s*\(\s*req\s*,\s*res)", 'first line inside the handler', "console.log('[DEBUG] {name}', { params: req.params, query: req.query, body: req.body })"),
    ('route', r"\b(?:router|app)\.(?:get|post|put|patch|delete|use)\(\s*['\"`]([^'\"`]+)", 'inside the first middleware/handler of this route', "console.log('[DEBUG] hit {name}', req.method, req.originalUrl)"),
    ('db-call', r"\bawait\s+(\w+)\.(?:find|findOne|findById|findByIdAndUpdate|findOneAndUpdate|create|insertMany|updateOne|updateMany|deleteOne|deleteMany|save|aggregate)\b", 'line after the await', "console.log('[DEBUG] {name} query done @L{L}')"),
    ('response', r"\bres\.(?:status\(\d+\)\.)?(?:json|send)\(", 'line before the response', "console.log('[DEBUG] sending response @L{L}', res.statusCode)"),
    ('next', r"\bnext\((?!\s*err)", 'line before next()', "console.log('[DEBUG] next() @L{L}')"),
    ('catch', r"\bcatch\s*\((\w+)\)", 'first line inside the catch', "console.log('[DEBUG] caught', {name}.message, {name}.stack)"),
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
