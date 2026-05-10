# VECTOR_MEMORY.md — Vector Memory & Semantic Retrieval Architecture

## Overview
This file defines the semantic/vector memory layer — how the AI retrieves relevant knowledge using meaning-based search rather than keyword matching. It complements the file-based memory system with embedding-powered retrieval.

## Why Vector Memory
Traditional file-based memory is exact — you retrieve by filename or keyword. Vector memory retrieves by meaning. When an agent asks "how do we handle token expiry?" vector search finds relevant code patterns, prior decisions, and documentation even if the exact words don't match.

## Vector Memory Architecture

### Knowledge Collections
```yaml
collections:
  code_patterns:
    description: "Reusable code snippets and implementation patterns"
    source: MEMORY.md (patterns section), CODING_STANDARDS.md
    embedding_model: text-embedding-3-small (or equivalent)
    update_frequency: "When new patterns are established"

  decisions:
    description: "Architectural decisions with full context"
    source: DECISIONS.md
    embedding_model: text-embedding-3-small
    update_frequency: "After every decision is written"

  failures:
    description: "Bug reports, root causes, and fixes"
    source: FAILURES.md
    embedding_model: text-embedding-3-small
    update_frequency: "After every bug fix is documented"

  api_docs:
    description: "API endpoint documentation and behavior"
    source: API.md, BACKEND.md
    embedding_model: text-embedding-3-small
    update_frequency: "When API changes are made"

  learnings:
    description: "Discovered patterns and optimizations"
    source: LEARNINGS.md
    embedding_model: text-embedding-3-small
    update_frequency: "After every session"

  terminology:
    description: "Domain-specific terms and definitions"
    source: TERMINOLOGY.md
    embedding_model: text-embedding-3-small
    update_frequency: "When new terms are added"
```

## Semantic Retrieval Workflows

### Workflow 1: Pattern Retrieval
**Trigger**: Agent needs to implement something and wants to check existing patterns

```yaml
steps:
  1. Extract intent: "What am I trying to implement?"
  2. Generate query embedding from intent description
  3. Search code_patterns collection with cosine similarity threshold: 0.80
  4. Return top-3 matching patterns with similarity scores
  5. Agent uses the highest-scoring pattern as template
  6. If no match > 0.80: fall back to CODING_STANDARDS.md
```

### Workflow 2: Historical Decision Retrieval
**Trigger**: Agent needs to make a decision and wants to know if it was decided before

```yaml
steps:
  1. Extract decision topic from current context
  2. Search decisions collection for similar past decisions
  3. Return matches with similarity > 0.75
  4. Present relevant decisions to agent for consideration
  5. Agent either reuses the decision or creates a new one and logs it
```

### Workflow 3: Similar Failure Detection
**Trigger**: An error is encountered; check if it matches a known failure

```yaml
steps:
  1. Extract error description, stack trace keywords, affected component
  2. Search failures collection for matching failure patterns
  3. If similarity > 0.85: apply the documented fix directly
  4. If 0.70-0.85: review the match and adapt the fix
  5. If < 0.70: treat as new failure; follow DEBUGGING.md workflow
```

### Workflow 4: Documentation Search
**Trigger**: Agent needs to understand an API or system behavior

```yaml
steps:
  1. Formulate a natural-language question about the API
  2. Search api_docs collection
  3. Return most relevant documentation sections
  4. If not found: search BACKEND.md and FRONTEND.md directly
```

## Embedding Schema

### Code Pattern Record
```json
{
  "id": "pattern_uuid",
  "title": "Express Controller with JSDoc and try/catch",
  "category": "backend_pattern",
  "content": "Full code pattern text here",
  "tags": ["express", "controller", "error-handling", "jsdoc"],
  "source_file": "MEMORY.md",
  "embedding": [0.023, -0.412, ...],
  "created_at": "2025-01-15T00:00:00Z",
  "last_used": "2025-03-10T00:00:00Z",
  "use_count": 42
}
```

### Decision Record
```json
{
  "id": "decision_uuid",
  "decision_id": "ARCH-001",
  "title": "Use UUID for MongoDB _id",
  "context": "Architectural decision context here",
  "decision": "Decision text",
  "rationale": "Why this was decided",
  "embedding": [0.102, -0.228, ...],
  "created_at": "2025-01-15T00:00:00Z"
}
```

### Failure Record
```json
{
  "id": "failure_uuid",
  "failure_id": "BUG-042",
  "error_description": "CastError: Cast to ObjectId failed",
  "affected_component": "UserController.getUser",
  "root_cause": "UUID string passed to ObjectId validator",
  "fix": "Changed mongoose schema to use String type for _id",
  "prevention": "Always define _id as String in UUID-based schemas",
  "embedding": [0.045, -0.318, ...],
  "created_at": "2025-02-20T00:00:00Z"
}
```

## Retrieval Quality Rules

### Similarity Thresholds
| Use Case | Min Similarity | Action Below Threshold |
|---|---|---|
| Direct pattern reuse | 0.85 | Use as reference, adapt significantly |
| Decision consideration | 0.75 | Review decision; may not apply |
| Failure pattern match | 0.80 | Treat as new; apply cautiously |
| Documentation lookup | 0.70 | Read full section for context |

### Re-Ranking Rules
When multiple results return above threshold:
1. Prefer more recent entries (last 30 days get +0.05 boost)
2. Prefer higher use-count entries (used 10+ times get +0.03 boost)
3. Prefer entries from the same component/module as current task

## Memory Indexing Schedule
| Trigger | Action |
|---|---|
| New pattern added to MEMORY.md | Index to code_patterns collection |
| New decision in DECISIONS.md | Index to decisions collection |
| New failure in FAILURES.md | Index to failures collection |
| New learning in LEARNINGS.md | Index to learnings collection |
| Session end | Re-index any modified entries |

## Fallback When Vector Search Unavailable
If embedding search is not available in the current environment:
1. Use keyword search on MEMORY.md (grep for key terms)
2. Read DECISIONS.md directly for architectural questions
3. Read FAILURES.md directly for error pattern matching
4. The system degrades gracefully — vector memory enhances but does not gate operation
