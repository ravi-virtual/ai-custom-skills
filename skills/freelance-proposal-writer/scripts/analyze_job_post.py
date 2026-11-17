#!/usr/bin/env python3
"""analyze_job_post.py - screen a freelance job post: fit, red flags, missing information, bid advice.

Usage:
  python analyze_job_post.py job.txt [--profile profile.json] [--json]
  cat job.txt | python analyze_job_post.py - --profile profile.json

profile.json (all optional):
{ "skills": ["python", "django", "react", "postgresql"],
  "min_hourly": 40, "min_fixed": 500,
  "avoid": ["wordpress", "php"] }

Heuristic helper for a human decision, not a verdict: it reads the text only. Verify the client's history,
payment verification and reviews on the platform before bidding.
"""
import argparse
import json
import re
import sys

TECH = """python django flask fastapi javascript typescript node nodejs express react nextjs vue angular svelte html css tailwind
php laravel wordpress woocommerce shopify java spring kotlin swift flutter react-native ios android c# dotnet .net go golang rust ruby rails
sql mysql postgresql postgres mongodb redis firebase supabase graphql rest api aws azure gcp docker kubernetes terraform linux
selenium playwright cypress puppeteer scraping scrapy pandas numpy tensorflow pytorch openai gpt llm langchain rag chatbot
zapier make n8n airtable notion stripe paypal twilio figma photoshop illustrator excel sheets bigquery tableau powerbi
wordpress seo analytics hubspot salesforce zendesk shopify""".split()

RED_FLAGS = [
    ("high", r"\b(free|unpaid)\s+(test|trial|sample|work|project)|\btest project\b.*\bfree\b|\bwithout pay", "Unpaid work requested. Offer a paid pilot or a short paid milestone instead."),
    ("high", r"whatsapp|telegram|skype|\bgmail\b|@[a-z0-9.-]+\.[a-z]{2,}|\bcontact me (at|on|outside)|off[- ]?platform|outside (of )?(upwork|fiverr|the platform)", "Wants to move off-platform. This usually breaks platform terms and removes payment protection."),
    ("high", r"\bequity\b|revenue share|\bexposure\b|pay (you )?(later|after (we|i) (raise|get))", "No guaranteed cash payment."),
    ("medium", r"\b(cheap|cheapest|lowest (price|bid|rate)|low budget|budget is (tight|small)|tight budget)\b", "Price-driven client; expect scope pressure."),
    ("medium", r"\b(simple|easy|quick|small)\b.{0,40}\b(job|task|fix|project|change)\b|should (only )?take (an hour|a few hours|1-2 hours)", "Scope may be underestimated; clarify before pricing."),
    ("medium", r"\b(clone of|like (uber|airbnb|facebook|tiktok|amazon|instagram))\b", "Large product described as a single task; scope is probably huge."),
    ("medium", r"\bmust (start|begin) (today|immediately|now)\b|\bright now\b", "Rush with no stated reason; confirm real deadline."),
    ("info", r"\b(urgent|asap)\b", "Marked urgent; confirm deadline and what 'done' means."),
    ("info", r"\bnda\b", "NDA requested; read it before signing, keep it proportionate."),
]

REQUIRE_QUESTIONS = [
    (r"\$\s?\d|budget|per hour|/hr|fixed[- ]price|hourly", "What is the budget or expected range, and is it fixed price or hourly?"),
    (r"deadline|within \d|by (the )?(end|\w+day)|\d+\s*(day|week|month)s?|asap|date", "What is the target date, and is anything time-critical (launch, event)?"),
    (r"existing|current(ly)?|legacy|codebase|repo|already (have|built)|from scratch|new (project|build)", "Is this a new build or an existing system? Can I get access to the code or environment?"),
    (r"success|goal|objective|deliverable|acceptance|done when|requirements?", "What does success look like, and what are the concrete deliverables?"),
]

MONEY = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)(?:\s*(?:-|to)\s*\$?\s?(\d[\d,]*(?:\.\d+)?))?\s*(k)?", re.I)


def words(text):
    return re.findall(r"[A-Za-z0-9#.+-]+", text.lower())


def analyze(text, profile):
    low = text.lower()
    toks = set(words(text))
    job_terms = sorted({t for t in TECH if (t in toks) or re.search(r"\b" + re.escape(t) + r"\b", low)})
    skills = [s.lower() for s in profile.get("skills", [])]
    matched = sorted({s for s in skills if re.search(r"(?<![\w])" + re.escape(s) + r"(?![\w])", low)})
    avoid_hit = sorted({a for a in (x.lower() for x in profile.get("avoid", [])) if re.search(r"\b" + re.escape(a) + r"\b", low)})

    money = []
    for m in MONEY.finditer(text):
        lo = float(m.group(1).replace(",", "")) * (1000 if m.group(3) else 1)
        hi = float(m.group(2).replace(",", "")) * (1000 if m.group(3) else 1) if m.group(2) else None
        money.append((lo, hi))
    hourly = bool(re.search(r"/\s?hr|per hour|hourly|an hour", low))
    budget = {"found": bool(money), "values": money[:3], "type": "hourly" if hourly else ("fixed" if money else "unknown")}

    flags = []
    for sev, pattern, why in RED_FLAGS:
        if re.search(pattern, text, re.I | re.S):
            flags.append({"severity": sev, "issue": why})
    n_words = len(words(text))
    if n_words < 60:
        flags.append({"severity": "medium", "issue": f"Very short post ({n_words} words): scope is probably undefined."})
    if avoid_hit:
        flags.append({"severity": "medium", "issue": "Mentions technologies you avoid: " + ", ".join(avoid_hit)})

    rate_note = None
    if money and profile:
        top = max((hi or lo) for lo, hi in money)
        if hourly and profile.get("min_hourly") and top < profile["min_hourly"]:
            rate_note = f"Stated hourly rate (up to {top:g}) is below your minimum ({profile['min_hourly']})."
        if not hourly and profile.get("min_fixed") and top < profile["min_fixed"]:
            rate_note = f"Stated budget (up to {top:g}) is below your minimum fixed price ({profile['min_fixed']})."
    if rate_note:
        flags.append({"severity": "medium", "issue": rate_note})

    questions = [q for pattern, q in REQUIRE_QUESTIONS if not re.search(pattern, low)]

    coverage = (len(matched) / len(job_terms)) if job_terms else None
    score = None
    if skills:
        score = 50 if coverage is None else round(100 * min(1.0, coverage * 1.2))
        score -= 15 * sum(f["severity"] == "medium" for f in flags) + 30 * sum(f["severity"] == "high" for f in flags)
        score = max(0, min(100, score))

    if any(f["severity"] == "high" for f in flags):
        verdict = "SKIP"
    elif score is not None and score < 35:
        verdict = "SKIP (weak fit)"
    elif any(f["severity"] == "medium" for f in flags) or (score is not None and score < 60) or len(questions) >= 3:
        verdict = "BID WITH CAUTION: ask clarifying questions first"
    else:
        verdict = "BID"
    return {"verdict": verdict, "fit_score": score, "job_terms": job_terms, "matched_skills": matched,
            "budget": budget, "red_flags": flags, "questions_to_ask": questions, "word_count": n_words}


def render(r):
    out = [f"VERDICT: {r['verdict']}   FIT: {r['fit_score'] if r['fit_score'] is not None else 'n/a (no profile)'}",
           f"Job mentions: {', '.join(r['job_terms']) or 'no recognised technologies'}",
           f"Your matching skills: {', '.join(r['matched_skills']) or 'none'}",
           f"Budget: {r['budget']['type']} {r['budget']['values'] or '(not stated)'}", ""]
    out.append("Red flags:" if r["red_flags"] else "Red flags: none found")
    out += [f"  [{f['severity'].upper()}] {f['issue']}" for f in r["red_flags"]]
    out.append("")
    out.append("Questions worth asking in the proposal:" if r["questions_to_ask"] else "Scope questions: the post covers the basics")
    out += [f"  - {q}" for q in r["questions_to_ask"]]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Screen a freelance job post.")
    ap.add_argument("job", help="job text file, or - for stdin")
    ap.add_argument("--profile", help="profile.json with skills, min rates, avoid list")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        text = sys.stdin.read() if args.job == "-" else open(args.job, encoding="utf-8").read()
        profile = json.load(open(args.profile, encoding="utf-8")) if args.profile else {}
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    result = analyze(text, profile)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
