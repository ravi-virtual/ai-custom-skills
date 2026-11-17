#!/usr/bin/env python3
"""suggest_logs.py - propose where to add temporary debug logs in a MERN (React client or Express server) file.

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
    ('react-http-call', r"\bawait\s+(?:axios|api|\w+Api)\.(?:get|post|put|patch|delete)\(", 'line before the call', "console.log('[DEBUG][client] request @L{L}')"),
    ('react-http-response', r"\bconst\s+(?:\{[^}]*\}|\w+)\s*=\s*await\s+(?:axios|api|\w+Api)\b", 'line after the await', "console.log('[DEBUG][client] response @L{L}')"),
    ('react-effect', r"\buseEffect\(", 'first line inside the effect', "console.log('[DEBUG][client] effect run @L{L}')"),
    ('express-handler', r"(?:(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?\(?\s*req\s*,\s*res|function\s+(\w+)\s*\(\s*req\s*,\s*res)", 'first line inside the handler', "console.log('[DEBUG][server] {name}', { params: req.params, query: req.query, body: req.body })"),
    ('express-route', r"\b(?:router|app)\.(?:get|post|put|patch|delete)\(\s*['\"`]([^'\"`]+)", 'inside the first handler of this route', "console.log('[DEBUG][server] hit {name}', req.method, req.originalUrl)"),
    ('mongoose-call', r"\bawait\s+(\w+)\.(?:find|findOne|findById|findByIdAndUpdate|create|updateOne|deleteOne|save|aggregate)\b", 'line after the await', "console.log('[DEBUG][server] {name} query done @L{L}')"),
    ('auth-token', r"(?:localStorage\.(?:set|get)Item\(['\"`]\w*token|Authorization|jwt\.verify|jwt\.sign)", 'next line (log presence only, never the token value)', "console.log('[DEBUG][auth] token present?', !!(typeof token !== 'undefined' && token))"),
    ('cors', r"\bcors\(", 'above the app.use(cors(...)) line', "console.log('[DEBUG][server] CORS origin from env', process.env.CLIENT_URL)"),
    ('catch', r"\bcatch\s*\((\w+)\)", 'first line inside the catch', "console.log('[DEBUG] caught', {name}?.response?.data ?? {name}?.message)"),
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
