# SELF_IMPROVEMENT.md — Agent Self-Assessment & Improvement Plan

## Purpose
The AI agent must continuously improve its performance, accuracy, and adherence to standards. This file defines the self-evaluation framework, current gaps, and improvement actions.

---

## Self-Assessment Rubric

### Dimension 1: Instruction Compliance
**Question**: Do all outputs fully comply with AGENT_RULES.md and CONSTRAINTS.md?

| Behavior | Current Score | Target |
|---|---|---|
| Return keyword on all response calls | ✅ 100% | 100% |
| isDeleted filter on all DB reads | ✅ 100% | 100% |
| ApiResponse/sendError (no raw res.json) | ✅ 100% | 100% |
| No process.env outside constants.js | ✅ 100% | 100% |
| JSDoc on all controller methods | ✅ 100% | 100% |
| Try/catch on all async controllers | ✅ 100% | 100% |
| Debug logs removed before delivery | ✅ 100% | 100% |
| Soft delete only (no hard deletes) | ✅ 100% | 100% |

### Dimension 2: Code Quality
**Question**: Does delivered code meet CODING_STANDARDS.md?

| Behavior | Current Score | Target |
|---|---|---|
| Naming conventions followed | ✅ High | 100% |
| Complete error path coverage | ✅ High | 100% |
| No placeholder/TODO code | ✅ High | 100% |
| Security review applied | ✅ High | 100% |
| Mental test performed | ✅ High | 100% |

### Dimension 3: Memory Utilization
**Question**: Is existing knowledge being used efficiently?

| Behavior | Current Score | Target |
|---|---|---|
| Check MEMORY.md before generating patterns | ⚠️ Medium | High |
| Check FAILURES.md before debugging | ⚠️ Medium | High |
| Update DECISIONS.md after decisions | ✅ High | 100% |
| Update LEARNINGS.md after sessions | ✅ High | 100% |
| Write to KNOWLEDGE_BASE.md when verified | ⚠️ Medium | High |

### Dimension 4: Communication Quality
**Question**: Are responses clear, concise, and actionable?

| Behavior | Current Score | Target |
|---|---|---|
| No filler sentences | ✅ High | 100% |
| Confidence stated when uncertain | ⚠️ Medium | High |
| Plan presented before complex execution | ✅ High | 100% |
| Sources referenced | ✅ High | 100% |

---

## Known Gaps & Improvement Actions

### Gap 1: Memory Retrieval Not Always First
**Observation**: Sometimes patterns are generated without checking MEMORY.md first, leading to slight inconsistencies.
**Improvement Action**: Add explicit checkpoint: "Have I checked MEMORY.md for this pattern?" before any code generation.
**Target Metric**: 100% of code generation tasks check MEMORY.md first.

### Gap 2: Confidence Level Not Always Stated
**Observation**: Confidence is sometimes stated implicitly rather than explicitly. AGENT_RULES.md requires explicit confidence % for decisions.
**Improvement Action**: End every architectural decision with "Confidence: X%"
**Target Metric**: 100% of decisions include explicit confidence score.

### Gap 3: KNOWLEDGE_BASE.md Not Always Updated
**Observation**: Verified facts are sometimes used without being written to KNOWLEDGE_BASE.md for future sessions.
**Improvement Action**: Before ending each session, review what was learned and add verified facts to KNOWLEDGE_BASE.md.
**Target Metric**: 5+ knowledge base entries per session involving new technical discovery.

### Gap 4: Long Context Compression Not Always Applied
**Observation**: In long sessions, earlier context may be duplicated instead of compressed.
**Improvement Action**: After every 10+ file creation, summarize completed sections in working memory.
**Target Metric**: No redundant context processing in sessions > 30 minutes.

---

## Improvement Experiments Log

### Experiment 1: Explicit Memory Retrieval Checkpoint
**Status**: Planned  
**Hypothesis**: Adding "Memory Check" as Step 0 in every code generation task will reduce pattern inconsistency by 80%.  
**Implementation**: Update AI_WORKFLOW.md to include explicit memory check step in all workflows.  
**Measurement**: Count instances of pattern deviation per 10 tasks.  

### Experiment 2: Structured Confidence Scoring
**Status**: Planned  
**Hypothesis**: Requiring explicit confidence % will surface hidden uncertainty before it causes errors.  
**Implementation**: Add confidence scoring template to PERSONA.md decision-making voice section.  
**Measurement**: Track decisions made with confidence < 80% that required revision.  

---

## Quarterly Self-Assessment Schedule
```
Q1 Assessment: Review all failure patterns from FAILURES.md
               → Identify top 3 recurring failure types
               → Design targeted improvements for each

Q2 Assessment: Review LEARNINGS.md for implemented vs unimplemented learnings
               → Any learning marked "Action Required" must have an owner by Q2

Q3 Assessment: Benchmark code quality against CODING_STANDARDS.md checklist
               → Run systematic audit of 10 recent outputs

Q4 Assessment: Full system review
               → Update AGENT_RULES.md if new immutable rules are needed
               → Archive outdated DECISIONS.md entries
               → Compress old FAILURES.md and LEARNINGS.md to archives
```

---

## Improvement Tracking Table

| ID | Gap | Action | Status | Measured Improvement |
|----|-----|--------|--------|---------------------|
| IMP-001 | Memory retrieval not first | Add memory check to all workflow step 0 | Planned | — |
| IMP-002 | Confidence not explicit | Confidence template in PERSONA.md | Planned | — |
| IMP-003 | KNOWLEDGE_BASE not updated | Session-end knowledge review | Planned | — |
| IMP-004 | Long context compression | Summarize every 10 files in session | In-Progress | — |
