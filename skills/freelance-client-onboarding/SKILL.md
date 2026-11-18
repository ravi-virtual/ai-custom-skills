---
name: freelance-client-onboarding
description: Onboards a new freelance client from "yes" to a running project - intake questionnaire, scope of work with deliverables, exclusions, assumptions, milestones and payment terms, kickoff agenda, welcome email, change-request form and wrap-up checklist, all generated from one project file. Use when the user won a job or signed a client and needs to define scope, write a statement of work, set up payment milestones, prepare a kickoff, handle scope creep with change requests, or close a project cleanly. Produces working-agreement documents, not legal advice or a contract.
---

# Freelance Client Onboarding

A clear start prevents most freelance problems: scope creep, late feedback, unpaid invoices. Spend one hour here to save days later.

## Workflow

1. **Collect the facts** (ask only for what is missing): client and freelancer names; project goal; concrete deliverables with how each is judged done; what is explicitly out of scope; assumptions and what the client must provide (access, content, decisions); milestones with dates and amounts; currency, deposit and payment days; revision rounds; communication channel, update day, response time; access list. Reuse the proposal or job post where possible; never invent figures or dates, ask instead.
2. **Write `project.json`** (see `references/project.example.json`).
3. **Generate the kit:** `python scripts/generate_onboarding_kit.py project.json --out ./onboarding/<client>`. It fills six documents and lists any `[[MISSING: key]]` fields; resolve each before sending.

   | File | Purpose | Send when |
   |---|---|---|
   | `welcome-email.md` | next steps, access request, kickoff scheduling | within 24 hours of the win |
   | `intake-questionnaire.md` | goals, success measures, constraints, existing assets | with the welcome email |
   | `scope-of-work.md` | deliverables, exclusions, assumptions, milestones, fees, acceptance, change process | before work starts; get written approval |
   | `kickoff-agenda.md` | 30 to 45 minute call plan | before the call |
   | `change-request.md` | any scope or schedule change | whenever the client asks for something new |
   | `offboarding-checklist.md` | delivery, access removal, final invoice, testimonial | at completion |

4. **Review each document with the user** and adjust tone and details. Make deliverables measurable ("three landing pages, up to two revision rounds" rather than "a website").
5. **Before starting work** confirm: scope approved in writing, deposit or first payment arranged as agreed, access received, kickoff held, first update scheduled.
6. **During the project** run weekly updates (done, next, blockers, decisions needed), and route every new request through the change-request form: estimate cost and time, get written approval, then work.
7. **At the end** follow the wrap-up checklist and ask for a review.

## Principles

- **Scope in writing, with exclusions.** "Out of scope" is as important as "in scope". Phrase assumptions as conditions the timeline and price depend on.
- **Define done.** Each deliverable has acceptance criteria and a review window (silence after the window counts as acceptance).
- **Money before momentum.** Common practice is a deposit and milestone-based invoicing for new clients (for example 30 to 50% upfront on fixed-price work); adapt to the client, platform and the size of the risk. On a platform, use its milestone and escrow features.
- **Protect credentials.** Ask for access through invites, password managers or scoped tokens; never accept or send passwords in plain email or chat; remove access at the end.
- **One decision maker.** Agree who approves work and that feedback arrives consolidated per round.
- **Say no kindly, price yes.** A change is not a refusal: "I can add that for X and it moves the date to Y."
- **Respect confidentiality and data protection.** Ask what is sensitive; do not copy client data to personal tools or AI services that are not approved for it.

## Boundaries

The generated documents are working agreements. Ownership of intellectual property, confidentiality, liability limits, termination, taxes and governing law are legal matters: recommend a reviewed contract template or the platform's contract terms and, for significant projects, a lawyer's review. Do not present these documents as legal advice.

## Files

- `scripts/generate_onboarding_kit.py` - fills the templates from `project.json`, reports missing fields
- `assets/*.md` - the six templates (placeholders look like `{{project.name}}`)
- `references/project.example.json` - a complete example input
