# Content Creation Workflows

Domain guidance for workflows that plan, draft, review, and publish content.

## Common Content Workflow Goals
- Write a blog post, article, or report
- Generate social media content from a long-form piece
- Create personalized outreach messages at scale
- Translate and localize content
- Repurpose content across formats

## Recommended Patterns
- **Critic-Refine** for quality-sensitive content
- **Map-Reduce** for content at scale
- **Human-in-the-Loop** for publishing approval

## Always-Present Steps
1. **Brief understanding** — extract audience, goal, tone, format, length
2. **Outline generation** — structure before writing
3. **Draft writing** — first draft from outline
4. **Quality review** — check for accuracy, tone, completeness
5. **Revision** — apply feedback
6. **Final formatting** — apply style guide
7. **Output / publish**

## Quality Criteria for Content
- Addresses the stated goal
- Matches the target audience's level
- Correct tone (formal/casual/persuasive)
- No factual errors (flag for human review if uncertain)
- Meets length requirements
- Follows brand voice guidelines

## Prompt Templates

### Outline Generation
```
Create a detailed outline for: {{content_type}} about "{{topic}}"
Target audience: {{audience}}
Tone: {{tone}}
Target length: {{length}}
Key points to include: {{key_points}}
Format the outline with H2 sections and bullet-point sub-items.
```

### Critique Prompt
```
Evaluate this draft against these criteria:
1. Does it address: {{goal}}?
2. Is the tone appropriate for: {{audience}}?
3. Are all claims accurate and specific?
4. Is the structure logical and clear?
5. Does it meet the length of {{length}}?

Draft: {{draft}}

Return JSON: { score: 1-10, passed: bool (score >= 7), feedback: string, specific_improvements: [...] }
```
