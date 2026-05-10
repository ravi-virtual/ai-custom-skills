# EVALUATION.md — AI & System Evaluation Framework

## Purpose
Defines how to evaluate the quality and effectiveness of AI outputs, generated content, system performance, and code deliveries. Establishes measurable standards rather than subjective judgment.

---

## Evaluation Dimensions

| Dimension | What is Measured | Evaluator |
|---|---|---|
| Code Quality | Compliance with CODING_STANDARDS.md | Automated + AI review |
| AI Output Quality | Usefulness, accuracy of generated content | User feedback + heuristics |
| System Performance | Response times, error rates | MONITORING.md metrics |
| Agent Behavior | Rule adherence, decision quality | Post-session audit |
| Test Coverage | % of critical paths covered by tests | Jest coverage report |

---

## Section 1: Code Quality Evaluation

### Automated Checks (Run in CI)
```bash
# 1. Lint check
npm run lint -- --max-warnings 0

# 2. Test coverage
npm test -- --coverage --coverageThreshold='{"global":{"lines":80}}'

# 3. Debug log audit
npx grep-cli "// \[DEBUG\]" src/ --fail-if-found

# 4. Secret audit  
npx detect-secrets scan src/
```

### Manual Code Scoring Rubric

| Category | Weight | Score Criteria |
|---|---|---|
| Naming conventions | 15% | All files/functions follow CODING_STANDARDS.md |
| Error handling | 25% | try/catch on all async, all paths handled |
| Security | 25% | No exposed secrets, auth on all routes, input validated |
| Completeness | 20% | No TODOs, no placeholders, no truncated code |
| Pattern adherence | 15% | Skill patterns applied, ApiResponse/sendError used |

**Scoring**:
- 90-100: Approve ✅
- 75-89: Approve with minor comments ⚠️
- 60-74: Revisions required ⛔
- < 60: Reject — rework required ❌

---

## Section 2: AI-Generated Content Evaluation

### Generation Quality Metrics

| Metric | Measurement | Target |
|---|---|---|
| Relevance | Does the content match the user's profile data? | > 90% relevant |
| Originality | Is it generic or personalized? | Personalized |
| Professionalism | Appropriate tone for professional profiles? | Always |
| Accuracy | Does it correctly reflect the user's background? | > 95% accurate |
| User Acceptance | Thumbs up rate from user feedback | > 70% |

### User Feedback Collection
```javascript
// Collect structured feedback on each generation
const feedbackSchema = {
  generationId: String,     // Which generation
  userId: String,           // Who gave feedback
  rating: Boolean,          // true = positive, false = negative
  model: String,            // Which AI model generated it
  timestamp: Date,
};

// Aggregate to track model performance over time
const modelStats = await Feedback.aggregate([
  { $group: {
    _id: '$model',
    positiveCount: { $sum: { $cond: ['$rating', 1, 0] } },
    negativeCount: { $sum: { $cond: ['$rating', 0, 1] } },
    total: { $sum: 1 }
  }}
]);
```

### AI Quality Heuristics (Before Delivering to User)
Before displaying generated content, validate:
```javascript
const validateGeneratedContent = (content) => {
  const issues = [];

  if (content.length < 50) issues.push('Content too short');
  if (content.length > 2000) issues.push('Content too long');
  if (/\[.*?\]/.test(content)) issues.push('Contains unfilled template placeholders');
  if (/lorem ipsum/i.test(content)) issues.push('Contains placeholder text');
  if (content.split(' ').length < 10) issues.push('Too few words');

  return { valid: issues.length === 0, issues };
};
```

---

## Section 3: Agent Behavior Evaluation

### Post-Session Audit Checklist

After each AI agent session, audit:

```
Code Rule Adherence:
□ All responses used ApiResponse/sendError (not raw res.json)
□ All async functions had try/catch
□ All responses had return before them
□ No process.env outside constants.js
□ All DB reads had { isDeleted: false } + .lean()

Communication Quality:
□ Confidence was stated for decisions
□ Uncertainty was acknowledged (not hidden)
□ Escalation to human triggered when required (confidence < 60%)
□ No filler language used

Memory Behavior:
□ DECISIONS.md updated for architectural choices
□ FAILURES.md updated for any bugs fixed
□ EXECUTION_MEMORY.md updated at session end
□ New facts written to KNOWLEDGE_BASE.md

Session Score: [N]/100
```

### Agent Performance Trends

Track these metrics across sessions:

| Metric | Target | How to Measure |
|---|---|---|
| Code delivered with 0 revisions | > 85% | Count post-delivery fixes |
| Correct skill activation | > 95% | Did the right skill get used? |
| Bugs introduced per session | < 1 | Count bugs found after delivery |
| Memory utilization | > 90% | Did AI check MEMORY.md before generating? |
| Session closure completeness | 100% | Were all 5 memory files updated? |

---

## Section 4: System Performance Evaluation

### API Performance Report Template

Run monthly against production:

```
## Performance Report: [Month Year]

### Response Time Percentiles
| Endpoint | p50 | p95 | p99 | Target p95 |
|---|---|---|---|---|
| GET /api/users/me | Xms | Xms | Xms | < 350ms |
| POST /api/profile | Xms | Xms | Xms | < 400ms |
| POST /api/generate/headline | Xs | Xs | Xs | < 15s |

### Error Rate
| Status | Count | % of total |
|---|---|---|
| 2xx (success) | X | X% |
| 4xx (client errors) | X | X% |
| 5xx (server errors) | X | X% |

### Slowest Endpoints This Month
1. [endpoint] — [reason if known]
2. [endpoint] — [reason if known]

### Action Items
- [ ] [Optimization needed]
```

---

## Section 5: Test Coverage Evaluation

### Coverage Targets

| Layer | Coverage Target | Current |
|---|---|---|
| Middleware (auth, validation) | 100% | Measured per sprint |
| Controller happy paths | 90% | Measured per sprint |
| Controller error paths | 80% | Measured per sprint |
| Redux slices | 85% | Measured per sprint |
| Utility functions | 95% | Measured per sprint |

### Coverage Report Command
```bash
cd backend && npm test -- --coverage --verbose

# Target thresholds in package.json:
"jest": {
  "coverageThreshold": {
    "global": {
      "branches": 75,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  }
}
```

---

## Evaluation Schedule

| Evaluation Type | Frequency | Owner |
|---|---|---|
| Code quality review | Every PR | AI + Human |
| AI content quality | Weekly aggregate | Automated via feedback data |
| Agent behavior audit | After every 5 sessions | Human |
| Performance report | Monthly | AI generates, human reviews |
| Test coverage | Every sprint | CI enforces thresholds |
| System health | Continuous | MONITORING.md dashboards |
