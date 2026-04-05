---
name: prompt-writing
description: Create, optimize, and refine high-quality AI prompts for various tasks. Use when the user wants to build a prompt for a chatbot, research agent, code assistant, or specialized task, or when they need to improve an existing prompt for better performance, accuracy, or format adherence.
---

# Prompt Writing Skill

A specialized skill for engineering high-performance prompts that maximize AI productivity and accuracy. This skill uses industry-standard frameworks and advanced prompting techniques.

## Core Framework: CO-STAR
When drafting a new prompt, ALWAYS consider these six dimensions:
- **C**ontext: Provide background information on the task.
- **O**bjective: Explicitly state the task you want the AI to perform.
- **S**tyle: Specify the writing style (e.g., formal, conversational, technical).
- **T**one: Set the emotional tone (e.g., professional, enthusiastic, neutral).
- **A**udience: Define who the output is for (e.g., experts, beginners, stakeholders).
- **R**esponse: Specify the output format (e.g., Markdown, JSON, List).

## Prompting Techniques
Depending on the complexity of the task, use these techniques:

### 1. Chain of Thought (CoT)
Encourage the model to "think step-by-step" before providing the final answer. This is critical for logic-heavy tasks.
*Example: "Explain your reasoning step-by-step before providing the final recommendation."*

### 2. Few-Shot Prompting
Provide 2-3 examples of the input-output pair to clarify tricky formats or styles.
*Format:*
```
Input: [Example Input]
Output: [Example Output]
---
Input: [Real Input]
Output: 
```

### 3. Delimiters
Use delimiters like `###`, `"""`, or `<tag></tag>` to clearly separate instructions from content.
*Example: "Summarize the text delimited by triple quotes: \"\"\"[Text Here]\"\"\""*

### 4. Role Assignment
Assign a specific persona to the AI to ground its perspective and expertise.
*Example: "You are a senior DevOps engineer with 10 years of experience in Kubernetes security."*

## Output Formats
When generating a prompt for a user, present it in a clean code block and explain why specific sections were included.

### Template for Complex Prompts:
```markdown
# Role
[Persona Description]

# Context
[Background Info]

# Task
[Core Objective]

# Constraints
- [Do's and Don'ts]

# Output Format
[Specific Structure/JSON/Markdown]

# Examples (Optional)
[Few-shot examples]
```

## Optimization Workflow
If the user provides an existing prompt to "fix" or "improve":
1. **Analyze**: Identify missing context or ambiguous instructions.
2. **Apply CO-STAR**: Fill the gaps.
3. **Inject Techniques**: Add CoT, delimiters, or role assignment where applicable.
4. **Test**: Provide a sample "test run" of how the AI would respond to the improved prompt.

## References
Consult `references/prompt_engineering_guide.md` for deep-dive examples of system prompts and advanced patterns.
