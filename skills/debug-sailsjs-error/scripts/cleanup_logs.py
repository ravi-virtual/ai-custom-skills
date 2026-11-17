#!/usr/bin/env python3
"""cleanup_logs.py - remove temporary debug instrumentation added during a debugging session.

Only statements that were tagged with the marker (default: ``// [DEBUG]``) are touched:

  console.log('[DEBUG] x', x); // [DEBUG]      -> statement removed (multi-line calls too)
  // [DEBUG] remember to remove this           -> comment line removed
  // [DEBUG:START] ... // [DEBUG:END]          -> whole block removed
  doRealWork(); // [DEBUG]                     -> KEPT and reported (a tag on real code
                                                  needs a human decision)

Usage:
  python cleanup_logs.py <file-or-dir> [<file-or-dir> ...] [--dry-run] [--check]
                         [--marker "// [DEBUG]"] [--ext .js,.jsx,.ts,.tsx]

Exit codes: 0 = clean, 1 = tagged lines remain (--check) or need manual review.
"""
import argparse
import os
import re
import sys

DEFAULT_MARKER = "// [DEBUG]"
DEFAULT_EXTS = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", ".next", ".sails", ".cache"}
# A line that *starts* a debug statement we are allowed to delete.
STATEMENT_RE = re.compile(r"^\s*(?:console\.\w+\s*\(|debugger\b)")


def find_comment_marker(line, marker):
    """Index of `marker` when it sits in a comment (not inside a string literal), else -1."""
    quote = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"`":
            quote = ch
        elif line.startswith(marker, i):
            return i
        i += 1
    return -1


def paren_balance(code):
    """Open-minus-close parentheses in `code`, ignoring strings and trailing // comments."""
    depth, quote, i = 0, None, 0
    while i < len(code):
        ch = code[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"`":
            quote = ch
        elif code.startswith("//", i):
            break
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        i += 1
    return depth


def block_markers(marker):
    if marker.endswith("]"):
        return marker[:-1] + ":START]", marker[:-1] + ":END]"
    return None, None


def clean_text(text, marker=DEFAULT_MARKER):
    """Return (new_text, removed, review) where removed/review are lists of (lineno, line)."""
    start_tag, end_tag = block_markers(marker)
    lines = text.splitlines(keepends=True)
    out, removed, review = [], [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        if start_tag and start_tag in line:
            j = i + 1
            while j < len(lines) and end_tag not in lines[j]:
                j += 1
            if j < len(lines):
                removed.extend((n + 1, lines[n].rstrip("\r\n")) for n in range(i, j + 1))
                i = j + 1
                continue
            review.append((i + 1, line.rstrip("\r\n") + "   <- unterminated block, no END tag"))
            out.append(line)
            i += 1
            continue

        idx = find_comment_marker(line, marker)
        if idx >= 0:
            code = line[:idx]
            if not code.strip():                       # pure marker comment
                removed.append((i + 1, line.rstrip("\r\n")))
                i += 1
                continue
            if STATEMENT_RE.match(code):               # tagged debug statement
                depth = paren_balance(code)
                j = i
                while depth > 0 and j + 1 < len(lines):
                    j += 1
                    depth += paren_balance(lines[j])
                removed.extend((n + 1, lines[n].rstrip("\r\n")) for n in range(i, j + 1))
                i = j + 1
                continue
            review.append((i + 1, line.rstrip("\r\n")))  # real code carrying a tag
        elif marker in line and STATEMENT_RE.match(line):
            # legacy style: marker inside the log string, e.g. console.log('// [DEBUG] x')
            depth = paren_balance(line)
            j = i
            while depth > 0 and j + 1 < len(lines):
                j += 1
                depth += paren_balance(lines[j])
            removed.extend((n + 1, lines[n].rstrip("\r\n")) for n in range(i, j + 1))
            i = j + 1
            continue
        out.append(line)
        i += 1
    return "".join(out), removed, review


def iter_files(paths, exts):
    for path in paths:
        if os.path.isfile(path):
            yield path
            continue
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in sorted(files):
                if name.endswith(exts):
                    yield os.path.join(root, name)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Remove tagged temporary debug statements.")
    ap.add_argument("paths", nargs="+", help="files or directories to clean")
    ap.add_argument("--marker", default=DEFAULT_MARKER, help=f"tag to look for (default: {DEFAULT_MARKER})")
    ap.add_argument("--ext", default=",".join(DEFAULT_EXTS), help="extensions scanned inside directories")
    ap.add_argument("--dry-run", action="store_true", help="report what would change, write nothing")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if any tagged line exists (CI/pre-commit)")
    args = ap.parse_args(argv)

    exts = tuple(e if e.startswith(".") else "." + e for e in args.ext.split(","))
    missing = [p for p in args.paths if not os.path.exists(p)]
    if missing:
        print("Error: not found: " + ", ".join(missing), file=sys.stderr)
        return 2

    total_removed = total_review = 0
    for path in iter_files(args.paths, exts):
        with open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        if args.marker not in text and block_markers(args.marker)[0] not in text:
            continue
        new_text, removed, review = clean_text(text, args.marker)
        total_removed += len(removed)
        total_review += len(review)
        for n, l in removed:
            print(f"{path}:{n}: {'would remove' if args.dry_run or args.check else 'removed'}: {l.strip()}")
        for n, l in review:
            print(f"{path}:{n}: REVIEW (tag on real code, left untouched): {l.strip()}")
        if removed and not (args.dry_run or args.check):
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_text)

    verb = "would remove" if args.dry_run or args.check else "removed"
    print(f"\n{verb} {total_removed} line(s); {total_review} line(s) need manual review.")
    if args.check:
        return 1 if (total_removed or total_review) else 0
    return 1 if total_review else 0


if __name__ == "__main__":
    sys.exit(main())
