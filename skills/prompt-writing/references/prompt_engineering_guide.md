# Advanced Prompt Engineering Patterns

## Few-Shot Prompting Strategy
Provide examples that follow the same structure you want the AI to use.

### Example: Text Classification
```markdown
Classify the sentiment of the following movie reviews:

Review 1: "The acting was superb and the story truly moving."
Sentiment: Positive

Review 2: "A total waste of time, poorly directed and written."
Sentiment: Negative

Review 3: "It was okay, not great but not terrible either."
Sentiment: Neutral

Review: "{{input}}"
Sentiment:
```

## Strategy: Role Play (Persona)
Defining the persona is more than just naming a job; it's about the tone, expertise, and focus.

### Example: Security Auditor
```markdown
# Persona
You are a senior cybersecurity auditor with 15 years of experience in penetration testing and compliance. Your goal is to identify vulnerabilities and suggest remediations that align with NIST frameworks.

# Instructions
Audit the provided code for security flaws.
- Focus on OWASP Top 10 vulnerabilities.
- Provide a risk score (1-10) for each finding.
- Suggest specific code fixes.
```

## Strategy: XML Tagging
Using XML-like tags (e.g., `<instructions>`, `<content>`, `<examples>`) helps the model navigate complex nested instructions.

### Example: Content Extraction
```markdown
You will be provided with a document. Extract the following information:
- Author
- Publication Date
- Summary

<document>
{{text}}
</document>

Provide the output in valid JSON format inside <output> tags.
```

## Strategy: Iterative Feedback Loop
Ask the AI to generate a draft, critique its own draft based on a checklist, and then rewrite it.

### Example:
```markdown
# Process
1. Write a draft of a 500-word blog post on the topic of AI ethics.
2. Critique the draft for clarity, tone, and evidence.
3. Rewrite the post incorporating the critique.
```
