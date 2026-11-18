---
name: freelance-proposal-writer
description: Screens freelance job posts and writes tailored proposals and cover letters for platforms such as Upwork, Fiverr, Freelancer, LinkedIn or direct inquiries - fit and red-flag analysis, bid or skip advice, clarifying questions, pricing approach, a client-focused proposal with proof and a clear next step, and a pre-send checklist. Use when the user pastes a job post or client message and wants a proposal, asks whether a job is worth bidding on, wants to improve a proposal that is not getting replies, or wants reusable proposal templates. Drafts for a human to review and send; never auto-submits.
---

# Freelance Proposal Writer

Win fewer, better jobs. A proposal is a short, specific answer to the client's problem, not a résumé.

## Workflow

1. **Screen the job.** Save the post to a file and run `python scripts/analyze_job_post.py job.txt --profile profile.json` (profile: your skills, minimum rates, technologies to avoid). It returns a fit score, red flags, budget signals, missing information and a bid or skip suggestion. Then add what the text cannot show: the client's payment verification, hire history, reviews and typical spend (on the platform). Bid only when fit is real and no high red flag stands.
2. **Collect proof.** Ask the user for one or two relevant past projects with a measurable outcome (numbers, time saved, links), their availability, and their rate or price range. Never invent experience, clients, links or results; if proof is missing, say so and write around it honestly (a relevant approach, a small paid pilot).
3. **Draft** using the structure below. Write in the user's voice, plain and confident.
4. **Check:** `python scripts/check_proposal.py proposal.txt --job job.txt`. Fix every error and weigh each warning. It catches placeholders, off-platform contact details, generic openings, missing question or next step, and self-focus.
5. **Hand over for human review.** The user reads it aloud once, adjusts anything that is not true, and sends it themselves. Do not submit applications or messages on the user's behalf and do not mass-generate proposals: platforms restrict automated submission, clients notice copy-paste, and the user's account is at stake. Check the platform's current terms.
6. **Track outcomes** (job, date, price, replied?, won?) so the next proposals improve: which hooks, prices and proof get replies.

## Proposal structure (about 120 to 250 words)

1. **Hook (first two lines):** the client's problem in their own words plus the insight that you understand it. These lines show in the preview, so no greeting boilerplate and no "I am writing to apply".
2. **Approach:** two or three concrete steps you would take first, specific to their situation.
3. **Proof:** one relevant result with a number or a link; a sentence, not a portfolio dump.
4. **Questions:** one or two sharp clarifying questions that show expertise and are answerable in a line (use the ones the analyzer suggests).
5. **Price and timing:** a number or range with what is included, or a clear way to get one ("with repo access I can quote today"). Offer a small paid first step for large or unclear scope.
6. **Next step:** one easy action (answer the question, a 15-minute call).

Keep the focus on "you": their outcome, their constraint, their timeline. Use their vocabulary. Leave out your life story, long skill lists, flattery and guarantees.

## Pricing guidance

- Hourly suits unclear or evolving scope; fixed price suits well-defined deliverables with acceptance criteria. For fixed bids, price the value and the risk, not just the hours.
- Never go below your minimum to win; low-budget clients often bring the largest scope pressure. Prefer a smaller scope at your price to the full scope at theirs.
- Break larger work into milestones with payment per milestone; for new clients prefer a short paid pilot to unpaid samples.
- State assumptions that the price depends on (access, number of revisions, third-party fees).

## Red flags (see `references/screening-checklist.md`)

Unpaid tests, requests to move off-platform, equity or exposure instead of pay, "simple task" with a huge scope, no budget and no detail, price-only language, a client with no payment verification or a history of disputes. Decline politely or ask the questions that would resolve the doubt.

## Files

- `scripts/analyze_job_post.py` - fit, red flags, missing information, verdict (`--json` for automation)
- `scripts/check_proposal.py` - pre-send lint
- `references/proposal-templates.md` - annotated templates for common job types and follow-ups
- `references/screening-checklist.md` - what to verify before bidding, and polite decline messages
