#!/usr/bin/env python3
"""analyze_error.py - match an error message against known React failure patterns.

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
    r"Too many re-renders": "Infinite loop detected. This usually happens when you call a state update function in the main body of the component or inside a `useEffect` without proper dependencies.",
    r"Cannot update a component while rendering a different component": "State update triggered during render phase. Move the state update to a `useEffect` or an event handler to avoid this warning.",
    r"Invalid hook call": "Hooks can only be called inside the body of a functional component. You might be calling a hook inside a loop, condition, or a regular JavaScript function.",
    r"rendered more hooks than during the previous render": "Hooks must be called in the same order every time. Do not place hooks inside `if` statements or loops.",
    r"Objects are not valid as a React child": "You are rendering a plain object (or Date/Promise). Render a field of it, or `JSON.stringify` while debugging. If it is a Promise, you forgot `await` or are rendering an `async` component in a client tree.",
    r"ReferenceError: .* is not defined": "A variable or function is being used before it's defined or is out of scope. Check your imports, especially for components used in JSX.",
    r"Warning: Each child in a list should have a unique \"key\" prop": "List rendering missing unique 'key' props. Add a stable ID (not array index if elements can reorder) to the elements returned from `.map()`.",
    r"Warning: Invalid DOM property \"class\"": "JSX Syntax error. In React, use `className` instead of `class` and `htmlFor` instead of `for`.",
    r"React.createElement: type is invalid": "Check your imports and exports. You might be importing a default export as a named export, or vice-versa, or the file path is incorrect.",
    r"Maximum update depth exceeded": "Infinite loop in your component logic. Check `useEffect` dependencies or state updates triggered by prop changes.",
    r"Hydration failed": "Server-side versus client-side mismatch. The HTML rendered by the server doesn't match the client's initial render. Check for random values (dates, Math.random) or conditional rendering based on `window`.",
    r"Expected server HTML to contain a matching": "Another hydration error common in SSR. Ensure your component doesn't use browser-only globals (like `localStorage`) during the initial render.",
    r"Stale closure": "A function (like an event handler) is using an old value of state. This happens when the function is defined inside a component but not updated when state changes. Use `useCallback` or `useEffect` dependencies.",
    r"Cannot read propert(?:y|ies) of (?:undefined|null)": "Accessing a property on undefined/null (Chrome: `Cannot read properties of undefined (reading 'x')`). Usual cause: data not loaded yet on first render. Initialise state with a safe default, use optional chaining `data?.items`, or render a loading state before touching the value.",
    r"\.map is not a function": "The value being mapped is not an array (often `null`, an object, or `{ data: [...] }` instead of `[...]`). Log the value's type, check the API response shape, and default to `[]`.",
    r"Can't perform a React state update on an unmounted component": "React 17 or older only (the warning was removed in React 18). An async result arrived after unmount. Cancel the request with `AbortController` or an `ignore` flag in the `useEffect` cleanup.",
    r"[Rr]endered fewer hooks than expected": "A hook is skipped on some renders, usually after an early `return` placed above a hook. Move every hook above any conditional return.",
    r"changing an uncontrolled input to be controlled": "An input's `value` went from `undefined` to defined. Initialise the state with `''` (or `false`/`0`) instead of `undefined`/`null`.",
    r"Minified React error #\d+": "Production build hides the message. Look the number up at react.dev/errors/<number>, or reproduce in a development build for the full text.",
    r"not wrapped in act\(": "A state update happened outside `act()` in a test. Use `await screen.findBy...` / `waitFor`, or `await userEvent...`, instead of asserting synchronously.",
    r"Module not found: Can't resolve|Failed to resolve import": "Bad import path or missing dependency. Check the relative path and file-name casing (case-sensitive on Linux/CI), the `exports` of the package, and run the install command.",
    r"is not a function": "A value that is not callable is being called. Check default-vs-named imports, a prop that was not passed, or a hook/helper whose return shape changed.",
    r"Text content does not match server-rendered HTML": "Hydration mismatch. Remove non-deterministic render output (dates, `Math.random`, `window`/`localStorage` reads) from the first render or move it into `useEffect`.",
}

GENERIC = "General React debugging: open the console, find the first error (not the last), read the component stack, then trace the data flow of props/state into that component."


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
