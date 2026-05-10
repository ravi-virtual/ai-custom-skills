# RETRIEVAL.md — Knowledge Retrieval Architecture

## Overview
This file defines how AI agents retrieve knowledge, context, and information — both from this file system and from external sources. Effective retrieval is what separates a knowledgeable agent from a confused one.

## Retrieval Hierarchy

```
Level 1 (Always Available): AGENT_RULES.md, CONSTRAINTS.md
Level 2 (Session Bootstrap): MEMORY.md, EXECUTION_MEMORY.md
Level 3 (Task Context):     OBJECTIVE.md, TASKS.md, CONTEXT.md
Level 4 (Domain Knowledge): KNOWLEDGE_BASE.md, TERMINOLOGY.md, ARCHITECTURE.md
Level 5 (Implementation):   CODING_STANDARDS.md, STACK.md, API.md
Level 6 (Reference):        EXAMPLES.md, DEBUGGING.md, TESTING.md
Level 7 (External):         Web search (only when internal knowledge insufficient)
```

## Retrieval Decision Tree

```
Query received
    ↓
Is this covered by AGENT_RULES.md or CONSTRAINTS.md?
    YES → Apply the rule directly; do not retrieve further
    NO  ↓
Is there a pattern in MEMORY.md?
    YES → Use the pattern; verify it's still current
    NO  ↓
Is this a domain terminology question?
    YES → Check TERMINOLOGY.md
    NO  ↓
Is this about system architecture?
    YES → Read ARCHITECTURE.md
    NO  ↓
Is this about a specific technology?
    YES → Check STACK.md
    NO  ↓
Is this about how to implement something?
    YES → Check CODING_STANDARDS.md, EXAMPLES.md
    NO  ↓
Is this about a known error pattern?
    YES → Check FAILURES.md
    NO  ↓
Is this about an external API or library?
    YES → Use web_search with targeted query
    NO  ↓
Escalate to human with specific question
```

## File-Based Retrieval Strategies

### Strategy 1: Direct File Read
When you know exactly which file contains the answer:
```
Use: file_read tool on the specific file
When: "How does the auth middleware work?" → read hasToken.js
Speed: Fastest
Accuracy: Highest for exact content
```

### Strategy 2: Pattern Matching
When searching for a pattern across memory files:
```
Use: grep/search across MEMORY.md, DECISIONS.md, FAILURES.md
Query: "UUID" or "soft delete" or specific error code
When: "Have we dealt with this type of error before?"
Speed: Fast
Accuracy: Depends on keyword match quality
```

### Strategy 3: Semantic Retrieval
When you know the concept but not the exact keywords:
```
Use: VECTOR_MEMORY.md embedding search
When: "How do we handle authentication in Express?" (might use different words)
Speed: Medium
Accuracy: High for conceptual questions
```

### Strategy 4: Structured Query
When you need a specific type of information with defined schema:
```
Use: Read the relevant schema-structured file
Examples:
  - DECISIONS.md for decision records
  - FAILURES.md for bug reports
  - TASKS.md for work items
Speed: Medium
Accuracy: High for structured data
```

## Context Loading Optimization

### Token Budget Management
When context is limited, prioritize loading in this order:
```
Priority 1 (always): AGENT_RULES.md (~500 tokens)
Priority 2 (always): CONSTRAINTS.md (~300 tokens)
Priority 3 (task):   OBJECTIVE.md + TASKS.md (~400 tokens)
Priority 4 (memory): EXECUTION_MEMORY.md current section (~200 tokens)
Priority 5 (domain): Only the specific sections needed for current task
Priority 6 (code):   Only the specific files being modified
```

### Context Compression Rules
When approaching context limits:
1. Summarize completed work into a 5-bullet summary
2. Replace full file contents with relevant section excerpts
3. Replace decision history with "Most recent decision: [X]"
4. Replace failure history with "Most recent relevant failure: [X]"

## External Knowledge Retrieval

### When to Use Web Search
Use web search ONLY when:
- The question involves a specific library version's API
- The question involves a known bug in a dependency
- The internal knowledge base has no relevant entry
- Verifying a fact that might have changed since training

### Web Search Query Formulation
```
Template: "[specific library] [specific behavior] [version if known]"
Good: "express-validator v7 isEmail options 2024"
Bad: "how to validate email"

Template: "[error message] [framework] [solution]"
Good: "CastError Cast to ObjectId failed mongoose UUID"
Bad: "mongoose error"
```

### External Knowledge Storage
After retrieving external knowledge:
1. Verify it applies to the current stack version
2. Test it before trusting it
3. If confirmed valid, add to KNOWLEDGE_BASE.md with the source URL

## Retrieval Quality Control

### Staleness Detection
Entries in retrieval results may be stale. Check staleness:
- DECISIONS.md entries: valid unless marked `[DEPRECATED]`
- FAILURES.md entries: always valid (past bugs happened)
- MEMORY.md patterns: verify against current codebase if > 30 days old
- STACK.md versions: verify against package.json

### Contradiction Resolution
When two retrieved sources contradict each other:
1. AGENT_RULES.md always wins
2. More specific source wins over general source
3. More recent entry wins over older entry
4. If still unclear, escalate to human

## Retrieval Metrics (Self-Assessment)
After every retrieval, assess:
- Did the retrieved context actually answer the question?
- Was there a more direct source that was missed?
- Should the relevant fact be added to KNOWLEDGE_BASE.md?
- Was external search used when internal knowledge was sufficient?

Track poor retrieval patterns in LEARNINGS.md:
```
Learning: Vector search returned low-relevance results for "X" type queries
Action: Improve KNOWLEDGE_BASE.md with better examples for "X" domain
```
