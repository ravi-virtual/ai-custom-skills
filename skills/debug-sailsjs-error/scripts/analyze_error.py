#!/usr/bin/env python3
"""analyze_error.py - match an error message against known Sails.js/Waterline failure patterns.

Usage:
  python analyze_error.py "<error text>"
  python analyze_error.py --file path/to/error.log     # for long stack traces
  some-command 2>&1 | python analyze_error.py           # read from stdin

Prints a JSON list of {"pattern", "advice"}. The advice is a lead to verify, not a verdict.
"""
import argparse
import json
import re
import sys

PATTERNS = {
    r"E_UNIQUE": "A uniqueness constraint was violated. Another record with the same value already exists. Check the model attribute marked `unique: true` and handle the error gracefully in the action (e.g., catch the error and return a user-friendly message).",
    r"E_MISSING_OR_INVALID_PARAMS": "The action or helper received inputs that don't match its defined `inputs` block. Check that all required inputs are being passed correctly from the client or calling code, and verify their types match the schema.",
    r"E_INVALID_CRITERIA": "A Waterline query was called with invalid or undefined criteria. Check for `undefined` values being passed to `.findOne()`, `.find()`, `.update()`, or `.destroy()`. A common cause is an unresolved route parameter.",
    r"E_UNAUTHENTICATED": "A policy blocked the request because the user is not authenticated. Ensure the session is active, the JWT token is valid and being sent in the `Authorization` header, or that the policy logic correctly calls `proceed()` for valid users.",
    r"E_FORBIDDEN": "A policy rejected the request because the user lacks the necessary permissions. Review the policy logic to confirm the authorization checks are correct.",
    r"UsageError": "A Sails helper or method was called incorrectly. Check the inputs/options passed to the helper and compare against its defined `inputs` contract. Ensure all required inputs are present.",
    r"AdapterError": "A low-level database adapter error occurred. Check your database connection configuration in `config/datastores.js` and ensure the database server is reachable.",
    r"exits\.error is not a function": "The action was called with an incomplete `exits` object. Ensure the action is being called via Sails.js routing or `sails.helpers.*()` and not invoked directly without the exits context.",
    r"Cannot call an exit after the machine has already exited": "An exit (e.g., `exits.success()`) was called more than once in the same action. Ensure only one exit is called per request, and use `return exits.success()` to prevent further execution.",
    r"Error: Timeout": "The action or helper timed out. A long-running asynchronous operation (DB query, external API call) may not be completing. Check your async logic and await all promises.",
    r"response.send: Cannot set headers after they are sent to the client": "A response was sent more than once for the same request. Ensure you use `return exits.success()` or `return res.ok()` to exit the action immediately after sending a response.",
    r"ECONNREFUSED": "The Sails.js server failed to connect to the database or an external service. Verify your `config/datastores.js` connection string and ensure the target service (e.g., MongoDB, MySQL) is running and accessible.",
    r"ER_ACCESS_DENIED_ERROR": "Database access was denied. Check your database username, password, and host configuration in `config/datastores.js`.",
    r"blueprint": "A blueprint route may be conflicting with a custom route or action. Review your `config/routes.js` and ensure custom routes don't shadow or conflict with auto-generated blueprint routes.",
    r"E_NOT_FOUND|notFound": "A lookup returned nothing. Check the `findOne` criteria, then call `exits.notFound()` (or the project's equivalent) explicitly instead of continuing with `undefined`.",
    r"Unrecognized exit|exit .* is not defined": "The action/helper called an exit that is not declared in `exits`. Add it to the `exits` block or use `exits.success`/`exits.error`.",
    r"sails\.helpers\.\w+ is not a function|Cannot read propert(?:y|ies) of undefined \(reading '\w+'\) .*helpers": "Helper not found. The file name (kebab-case) must match the camelCase call (`send-email.js` -> `sails.helpers.sendEmail`), and `sails.config.hooks.helpers` must be enabled.",
    r"ER_DUP_ENTRY|E11000": "Duplicate key at the database level. Treat it like E_UNIQUE: catch it, return a 409/400 and name the field.",
    r"Could not find a (?:helper|model)|Unknown model": "Model/helper identity mismatch. Check the file name, `globals.models` setting, and the `identity` used in the call.",
    r"Cannot read propert(?:y|ies) of undefined \(reading 'session'\)": "Session hook disabled or the code runs outside a request. Check `config/session.js` and that `req` is passed down.",
}

GENERIC = "General Sails.js debugging: read the full stack in the `sails lift` output, verify every code path in `fn` reaches an exit, and check that policies call `proceed()` on success."


def analyze(error_log):
    """Return every matching suggestion (order = order of PATTERNS)."""
    hits = []
    for pattern, advice in PATTERNS.items():
        if re.search(pattern, error_log, re.IGNORECASE):
            hits.append({"pattern": pattern, "advice": advice})
    return hits or [{"pattern": "Unknown", "advice": GENERIC}]


def main():
    ap = argparse.ArgumentParser(description="Match an error against known patterns.")
    ap.add_argument("error", nargs="*", help="error text (quote it); omit to read stdin")
    ap.add_argument("--file", help="read the error text from a file")
    args = ap.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print(json.dumps({"error": f"cannot read {args.file}: {exc}"}))
            return 1
    elif args.error:
        text = " ".join(args.error)
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        ap.print_usage(sys.stderr)
        return 1

    print(json.dumps(analyze(text), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
