# GOVERNANCE.md — AI Governance & Compliance Framework

## Purpose
Defines the governance model for AI agent behavior, data handling, compliance requirements, and the human oversight structure for this AI Operating System.

---

## Governance Model

### Authority Hierarchy

```
Level 0: Human (Project Owner)
  └─ Final authority on all decisions
  └─ Sole authority on AGENT_RULES.md and CONSTRAINTS.md
  └─ Required for any destructive or production-changing action

Level 1: ORCH-01 (Orchestrator Agent)
  └─ Decomposes tasks, assigns to specialists
  └─ Validates consistency across agent outputs
  └─ Escalates to Level 0 when authority exceeded

Level 2: Specialist Agents (DEV, DBG, QA, etc.)
  └─ Execute within their defined domain
  └─ Cannot make architectural decisions alone
  └─ Report to ORCH-01

Level 3: External AI Services
  └─ Gemini, Grok, OpenAI — content generation only
  └─ No access to codebase or infrastructure
  └─ Output validated before use
```

---

## Section 1: AI Agent Boundaries

### What AI Agents Are Authorized to Do

```
✅ Read any file in the workspace
✅ Write new code files following established patterns
✅ Update documentation files (DECISIONS.md, FAILURES.md, etc.)
✅ Make architectural decisions within established patterns
✅ Run automated tests
✅ Propose database queries (but not execute on production)
✅ Suggest configuration changes (but not apply to production)
```

### What AI Agents Are NOT Authorized to Do

```
❌ Modify AGENT_RULES.md or CONSTRAINTS.md without explicit human instruction
❌ Delete or overwrite existing files without human confirmation
❌ Deploy to production environment
❌ Rotate credentials or secrets
❌ Access external systems beyond the defined tool set
❌ Execute database migrations on production
❌ Grant or revoke user permissions
❌ Make decisions with > 30% uncertainty without escalating
```

---

## Section 2: Data Governance

### Data Classification

| Classification | Examples | Handling |
|---|---|---|
| **Public** | Profile display content, public usernames | No restrictions |
| **Internal** | User IDs, profile metadata, usage counts | No logging, no external transfer |
| **Confidential** | Email addresses, names, profile content | Encrypted at rest, HTTPS only |
| **Secret** | Passwords, JWT tokens, API keys | Hashed/encrypted, never logged, never exposed |

### Data Minimization Rules
- Collect only what is necessary for the feature
- Do not store data "just in case" — define purpose before collecting
- Never log more data than needed for debugging
- User data deleted on account deletion (soft delete within 90 days, hard delete after retention period)

### Data Retention Policy

| Data Type | Retention Period | Deletion Method |
|---|---|---|
| User accounts | Until requested deletion + 90 days | Soft delete → hard delete |
| User profiles | Same as user account | Soft delete → hard delete |
| Generated content | Until profile deleted | Cascade delete with profile |
| Feedback/ratings | 1 year | Hard delete after retention |
| Auth logs | 90 days | Automated cleanup job |
| Error logs | 30 days | Log rotation |
| Backup data | 7 days | Automated backup rotation |

---

## Section 3: AI Content Governance

### AI-Generated Content Rules

```
1. AI-generated content is NEVER presented as human-written
2. Users must be informed when content is AI-generated
3. Users have full control to edit or discard generated content
4. AI-generated content is not stored as permanent truth — it's a draft
5. User feedback on AI content must be collected and stored
6. AI models used must be disclosed to users on request
```

### Prohibited AI Generation Uses
```
❌ Generating content that could harm or defame individuals
❌ Generating misleading professional credentials
❌ Generating content claiming skills or experience the user hasn't provided
❌ Using user data to train models without explicit consent
❌ Sharing user profile data with AI providers beyond the API call
```

### AI Provider Data Handling
```
Gemini API: Data sent per-request; Google's terms apply
Grok API: Data sent per-request; xAI's terms apply
OpenAI API: Data sent per-request; OpenAI's terms apply

RULE: Never include PII (email, phone, SSN) in AI prompts
RULE: Only include what the user has entered for profile content
RULE: Prompts are structured to be non-identifying where possible
```

---

## Section 4: Human Oversight Requirements

### Mandatory Human Review Triggers

| Event | Why Human Review Required |
|---|---|
| Any AGENT_RULES.md change | Immutable rules must have human intent |
| Any CONSTRAINTS.md change | Hard limits require human authorization |
| Production deployment | Risk to live users |
| Database migration | Risk to data integrity |
| Credential rotation | Security event |
| Incident P0/P1 | High impact, fast decisions needed |
| Architectural change (new service, new DB, etc.) | System-wide impact |

### Human Confirmation Format

For actions requiring human confirmation:
```
⚠️ HUMAN CONFIRMATION REQUIRED

Action: [Specific action about to be taken]
Impact: [What this affects]
Reversible: [Yes/No — if Yes, how]
Risk Level: [Low/Medium/High]

To proceed, reply with exactly:
"Confirmed: [action description]"

General approval ("yes", "go ahead") is NOT sufficient for this action.
```

---

## Section 5: Compliance Considerations

### GDPR Considerations (If EU Users)
- [ ] Privacy policy page exists and is accessible
- [ ] Cookie consent banner for non-essential cookies
- [ ] "Right to Deletion" implemented (soft delete → hard delete pipeline)
- [ ] "Right to Data Export" considered (user can download their data)
- [ ] Data Processing Agreement with AI providers reviewed
- [ ] No AI provider receives EU PII without appropriate safeguards

### Security Compliance
- [ ] OWASP Top 10 reviewed against current implementation
- [ ] Input validation on all endpoints (VALIDATION.md)
- [ ] Authentication and authorization on all protected routes
- [ ] HTTPS enforced (no HTTP in production)
- [ ] Sensitive data not logged (OBSERVABILITY.md rules)
- [ ] Dependency vulnerabilities checked (`npm audit`)

---

## Section 6: Audit Trail

### What Must Be Auditable

| Action | Audit Record |
|---|---|
| User registration | Timestamp, IP (optional), user ID |
| User login (success) | Timestamp, user ID |
| User login (failure) | Timestamp, email attempted, IP |
| Profile created | Timestamp, user ID, profile ID |
| Profile deleted | Timestamp, user ID, profile ID |
| AI generation | Timestamp, user ID, model used, input hash |
| Admin action | Timestamp, admin ID, target user ID, action |

### Audit Log Retention
- Security audit logs: 1 year minimum
- User action logs: 90 days
- Admin action logs: 2 years

---

## Section 7: Governance Review Schedule

| Review | Frequency | Reviewer |
|---|---|---|
| AGENT_RULES.md effectiveness | Quarterly | Human |
| CONSTRAINTS.md relevance | Quarterly | Human |
| Data retention compliance | Annually | Human |
| AI provider terms review | When terms change | Human |
| Security audit | Semi-annually | Human + external |
| Agent boundary violations | After every incident | Human |
