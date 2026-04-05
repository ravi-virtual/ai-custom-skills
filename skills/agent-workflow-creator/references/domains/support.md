# Customer Support & Triage Workflows

Domain-specific guidance for building agent workflows that handle customer support, helpdesk triage, issue routing, and resolution pipelines.

---

## Core Challenges in Support Workflows

Support workflows are unique because:
- **Input is unstructured** — customers write in natural language, often emotionally charged
- **Priority is latency-sensitive** — slow responses erode trust
- **Routing must be accurate** — wrong team = bad experience + wasted effort
- **Escalation paths matter** — some issues *must* reach a human
- **Context must persist** — conversation history, account data, prior tickets all matter

---

## Key Phases

### 1. Intake & Classification
- Parse the incoming message (chat, email, form, call transcript)
- Extract: intent, urgency, sentiment, product/feature area, account tier
- Classify issue type: bug report, billing, feature request, account access, complaint, general inquiry
- Tools: `llm_completion` (classification), `entity_extraction`, `sentiment_analysis`

### 2. Context Enrichment
- Pull customer profile from CRM (account age, tier, prior tickets, open orders)
- Retrieve knowledge base articles relevant to the classified issue
- Check system status pages for known outages that may explain the issue
- Tools: `api_call` (CRM, status page), `vector_search` (knowledge base)

### 3. Triage & Routing
- Apply routing rules based on: issue type × urgency × account tier
- Priority tiers:
  - **P0**: Data loss, security incidents, total outage → immediate human escalation
  - **P1**: Billing disputes, enterprise customers → priority queue
  - **P2**: Feature bugs, account issues → standard queue
  - **P3**: General questions → self-serve or async
- Tools: `rule_engine`, `llm_completion` (edge cases)

### 4. Resolution Attempt
- For P2/P3: attempt automated resolution using knowledge base
- Draft a response using retrieved context + customer history
- If confidence is high enough (e.g., > 0.85): send draft response
- If low confidence: flag for agent review with draft pre-populated
- Tools: `vector_search`, `llm_completion`, `human_input` (review gate)

### 5. Escalation Handling
- For issues that cannot be resolved automatically:
  - Summarize conversation, issue type, and attempted resolution in handoff note
  - Route to appropriate team with full context
  - Set SLA timer and notify customer of expected response time
- Tools: `api_call` (ticketing system), `notification`

### 6. Resolution & Closure
- After resolution: send confirmation to customer
- Log outcome, root cause, and resolution to CRM
- Tag ticket for QA review if it was escalated or took > N minutes
- Update knowledge base if a new pattern was discovered
- Tools: `api_call` (CRM, ticketing), `llm_completion` (KB article draft)

---

## Decision Branch Patterns

### Sentiment Gate
```
IF sentiment == "angry" OR urgency_signal == true
  → Escalate to human regardless of tier
ELSE
  → Continue automated flow
```

### Confidence Gate
```
IF resolution_confidence >= 0.85
  → Send response automatically
ELSE IF resolution_confidence >= 0.60
  → Send to agent for 1-click approval
ELSE
  → Route to agent for full manual response
```

### Account Tier Gate
```
IF account.tier == "enterprise"
  → Always route to dedicated team (skip automated resolution)
ELSE IF account.tier == "pro"
  → Attempt automation with 60s human review window
ELSE
  → Full automation
```

---

## Error Handling in Support Workflows

| Failure Type | Recovery Strategy |
|---|---|
| CRM API timeout | Use cached profile; flag for manual sync after |
| KB search returns no results | Fall back to generic response + escalate |
| LLM classification fails | Route to "general" bucket + flag for review |
| Ticketing system unavailable | Queue locally; retry with exponential backoff |
| Customer email malformed | Acknowledge receipt; ask for info via fallback channel |

---

## Metrics to Track

- **First Response Time (FRT)** — Time from ticket open to first reply
- **Automation Rate** — % of tickets resolved without human touch
- **Escalation Rate** — % that needed human handoff
- **Customer Satisfaction (CSAT)** — Post-resolution survey score
- **Ticket Re-open Rate** — Proxy for resolution quality
- **Misclassification Rate** — Wrong routing decisions

---

## Example Step Sequence

```
1. Receive ticket (email/chat/form)
2. Classify intent + sentiment
3. Enrich with CRM + KB context
4. Apply triage rules → assign priority + route
5. [P0/P1] → immediate escalation to human
6. [P2/P3] → generate draft response using KB
7. Confidence check → auto-send or human review
8. Log outcome → update CRM and KB
9. Send CSAT survey (delayed 24h)
```

---

## Anti-Patterns to Avoid

- **Over-automating high-stakes issues** — never auto-resolve billing disputes or security reports without human confirmation
- **No context in escalation handoffs** — always summarize what was tried and why it failed
- **Fixed routing without sentiment check** — a "billing" query from an angry enterprise customer behaves differently than the same query from a satisfied free-tier user
- **Ignoring repeat tickets** — if a customer opens the same issue 3+ times, flag it as a systemic problem, not an individual support case
