#!/usr/bin/env python3
"""analyze_error.py - match an error message against known MERN full-stack failure patterns.

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
    r"Access-Control-Allow-Origin": "CORS issue. The backend is not allowing requests from the frontend origin. Check your `cors` configuration in Express and ensure `origin` matches your React dev server (usually localhost:5173 or 3000).",
    r"Network Error": "React cannot reach the Express server. Verify the server is running and the URL in your Axios/Fetch call is correct. Check if the server port is correct.",
    r"401 \(Unauthorized\)": "Authentication failure. The JWT is either missing, invalid, or expired. Check if the 'Authorization' header is being sent correctly in Axios interceptors.",
    r"404 \(Not Found\)": "The API endpoint does not exist. Verify the route definition in Express and ensure any prefixes like `/api` are included in the React request URL.",
    r"400 \(Bad Request\)": "Validation failed on the backend. The frontend is likely sending data that doesn't match the Mongoose schema or Yup/Zod validator. Compare the React request body with the Express schema.",
    r"500 \(Internal Server Error\)": "The backend server crashed while processing the request. Check the Express terminal for the stack trace to identify the bug in the controller or middleware.",
    r"Proxy error: Could not proxy request": "Vite/CRA proxy failure. The backend server is likely not running on the port specified in `vite.config.ts` or `package.json` proxy field.",
    r"AxiosError: Request failed with status code 403": "Forbidden. This often means CORS allows the origin but the specific request fails (e.g., missing 'withCredentials: true' for cookies or a mismatch in allowed methods).",
    r"Failed to fetch": "The browser blocked the request or the server is down. Check for CORS errors in the console or verify the server status.",
    r"ERR_CONNECTION_REFUSED": "The backend server is not listening on the expected port. Confirm the Express server is successfully started and listening.",
    r"Preflight response is not successful": "CORS preflight (OPTIONS) request failed. Ensure the backend handles OPTIONS requests (automatically done by the `cors` middleware) and allows the required headers.",
    r"ECONNRESET": "The connection was abruptly closed by the server. Check if the Express server crashed or if there's a timeout/limit being hit.",
    r"Error: No 'Access-Control-Allow-Origin' header is present": "CORS block. You MUST add the `cors()` middleware in your Express `app.js` or `server.js` before any routes.",
    r"withCredentials": "If you are using cookies for sessions/JWT, ensure `withCredentials: true` is set in the React Axios config AND `credentials: true` is set in the backend `cors` config.",
    r"Unexpected token '?<|is not valid JSON": "The frontend received HTML instead of JSON (a 404 page, `index.html` fallback, or a proxy error page). Open the Network tab, check the real response and URL, then fix the base URL / proxy / missing route.",
    r"blocked by CORS policy": "Browser CORS block. Fix on the server: `cors({ origin: <exact frontend origin>, credentials: true })` registered before the routes. Wildcard `*` cannot be combined with credentials.",
    r"ERR_NETWORK|net::ERR_FAILED": "The request never completed (server down, wrong port, mixed content, or a CORS failure that hides the status). Check the server log first, then the Network tab.",
    r"E11000 duplicate key": "MongoDB unique index violated by the request. Have the API return a 409 with the offending field so the UI can show a precise message.",
    r"Mixed Content": "An HTTPS page is calling an HTTP API. Serve the API over HTTPS or use a same-origin proxy.",
    r"Request failed with status code 4\d\d": "The API answered with a 4xx. Read `error.response.data` (not just `error.message`) to see the server's validation/auth message.",
    r"SameSite|Set-Cookie": "Cookie not being stored/sent. For cross-site cookies you need `SameSite=None; Secure` over HTTPS, `credentials: true` in CORS, and `withCredentials: true` on the client.",
    r"Cannot read propert(?:y|ies) of (?:undefined|null)": "Usually the UI reads a field before the response arrives, or the API response shape differs from what the component expects. Log the raw response once and compare with the component's access path.",
}

GENERIC = "General MERN debugging: trace one request end to end - React handler -> Axios call (URL, headers) -> Express route -> controller -> Mongoose -> response -> React state."


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
