# Research & Knowledge Workflows

Domain-specific guidance for building agent workflows that research, synthesize, and report on topics.

## Common Research Workflow Goals
- Answer a specific question from multiple sources
- Generate a report with citations
- Monitor a topic over time (recurring)
- Compare multiple viewpoints
- Extract structured data from unstructured research

## Recommended Patterns
- **ReAct Loop** for open-ended research (you don't know how many searches you'll need)
- **Map-Reduce** for batch processing many sources
- **Critic-Refine** for ensuring report quality
- **RAG** when using an internal knowledge base

## Steps Always Present in Research Workflows
1. **Query planning** — derive 3–5 search queries from the topic
2. **Source retrieval** — web search or vector search
3. **Content extraction** — fetch full content, not just snippets
4. **Relevance filtering** — discard off-topic sources
5. **Fact extraction** — pull structured facts from content
6. **Synthesis** — combine facts into coherent narrative
7. **Citation formatting** — link facts back to sources
8. **Output formatting** — render as markdown/HTML/JSON

## Quality Checks
- Verify at least N credible sources found (recommend N≥3)
- Check for conflicting claims and flag them
- Ensure citations are real URLs (validate before including)
- Verify the output answers the original question

## Common Failure Points
| Risk | Mitigation |
|------|-----------|
| Search returns irrelevant results | Refine query with context |
| Source is paywalled | Try alternative sources |
| LLM hallucinates citations | Validate URLs programmatically |
| Topic too broad → shallow coverage | Decompose into sub-topics |
| Contradictory sources | Flag explicitly in report |

## Example Tools for Research Workflows
- `web_search` — primary discovery
- `web_fetch` — full page content
- `vector_search` — internal docs
- `llm_structured` — extract facts as JSON
- `llm_completion` — synthesize narrative
- `file_write` — save report

## Prompt Templates

### Query Planning Prompt
```
You are a research assistant. Given the topic: "{{topic}}"
Generate {{n}} search queries that together will provide comprehensive coverage.
Consider: definitions, recent developments, expert opinions, case studies, statistics.
Return as JSON list: ["query1", "query2", ...]
```

### Fact Extraction Prompt
```
Extract all factual claims from the following text. For each fact, record:
- claim: the specific factual statement
- source_url: where this came from
- confidence: high/medium/low
- date_mentioned: if a date is referenced

Text: {{content}}

Return as JSON array.
```

### Report Synthesis Prompt
```
Write a comprehensive report on "{{topic}}" using ONLY the following verified facts.
Do not add information not present in the facts.
Structure: Executive Summary → Key Findings → Analysis → Conclusion → Sources

Facts: {{extracted_facts}}
```
