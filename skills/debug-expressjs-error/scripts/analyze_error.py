#!/usr/bin/env python3
"""analyze_error.py - match an error message against known Express/Node failure patterns.

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
    r"EADDRINUSE": "Port is already in use. Another instance of the server might be running elsewhere, or another application is using this port. Use `lsof -i :<port>` to find and kill the process.",
    r"ValidationError: .*": "Mongoose validation failed. Check if the input data matches your schema requirements (required fields, types, etc.). Ensure all required fields are present in the request body.",
    r"CastError: Cast to ObjectId failed": "Invalid ID format passed to a database query. Check if the ID string matches the MongoDB ObjectId format. This often happens in route parameters like `/api/users/:id`.",
    r"MongoNetworkError": "Database connection failed. Ensure your MongoDB URI is correct, the database is accessible, and your IP is whitelisted (if using Atlas).",
    r"Route.get\(\) requires a callback function but got a \[object Undefined\]": "Check your route definitions. You're likely trying to use a controller function that wasn't exported correctly or is misspelled in the import.",
    r"PayloadTooLargeError": "The request body is too large. Consider increasing the limit in your body-parser middleware: `app.use(express.json({ limit: '10mb' }))`.",
    r"JsonWebTokenError": "Invalid JWT. Check if the token was signed correctly or if the secret key matches on both sides. Verify the 'Authorization' header format.",
    r"ERR_HTTP_HEADERS_SENT": "Multiple responses sent for a single request. Ensure you are using `return res.status(...).json(...)` to exit early and avoid continuing execution after sending a response.",
    r"req.body is undefined": "Missing body-parsing middleware. Add `app.use(express.json())` and `app.use(express.urlencoded({ extended: true }))` before your routes.",
    r"MongooseServerSelectionError": "The server failed to connect to MongoDB. Check your connection string and ensure the database server is running.",
    r"RangeError: Maximum call stack size exceeded": "Infinite recursion in your middleware or logic. Check your `next()` calls and ensure you aren't calling the same middleware recursively.",
    r"TokenExpiredError": "The JWT has expired. The client needs to re-authenticate or use a refresh token.",
    r"ReferenceError: next is not defined": "You are trying to call `next()` in a middleware or route handler, but it wasn't included in the parameter list: `(req, res, next) => { ... }`.",
    r"SyntaxError: Unexpected token": "Likely a JSON parsing error. The client sent malformed JSON, or you are trying to parse something that isn't JSON.",
    r"UnhandledPromiseRejection|ERR_UNHANDLED_REJECTION|UnhandledPromiseRejectionWarning": "A rejected promise had no handler (Node 15+ crashes the process on this). In Express 4, async handlers do not forward rejections: wrap them (`asyncHandler`) or `try/catch` and call `next(err)`. Express 5 forwards them automatically.",
    r"E11000 duplicate key": "MongoDB unique index violated. Catch `err.code === 11000`, return 409, and read `err.keyValue` to tell the user which field collided.",
    r"jwt (?:malformed|must be provided)": "Token missing or not a JWT. Check the `Authorization: Bearer <token>` header is sent and parsed (no `Bearer ` prefix left in the value, no quotes around it).",
    r"Cannot GET /|Cannot POST /": "No route matched. Check the HTTP method, the mount prefix (`app.use('/api', router)`), trailing slashes, and that the route file is actually required before the 404 handler.",
    r"ECONNREFUSED": "Nothing is listening at the target host:port (database, Redis, or another service). Confirm the service is up and that the URL/port come from the right environment variable.",
    r"listen EACCES": "No permission to bind that port (ports below 1024 need elevated rights). Use a higher port or a reverse proxy.",
    r"Cannot find module": "Missing dependency or wrong import path. Run the install command, check the file name casing and the `main`/`exports` field; for ESM check the file extension is included.",
    r"MongoParseError|bad auth|Authentication failed": "Invalid Mongo connection string or credentials. URL-encode special characters in the password and check the auth database / Atlas user.",
    r"is not a function": "Something that is not a function is called. Typical: wrong `require` shape (`module.exports` vs named export), or a middleware factory used without calling it (`cors` vs `cors()`).",
}

GENERIC = "General Express debugging: read the first line of the stack trace, confirm middleware order, check that every code path sends exactly one response or calls next(), and verify DB connectivity."


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
