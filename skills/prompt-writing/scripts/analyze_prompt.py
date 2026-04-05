import argparse
import sys

def analyze_prompt(prompt_text):
    """
    Analyzes a prompt for common structural elements and provides feedback.
    """
    issues = []
    
    # Check for Context
    if any(word in prompt_text.lower() for word in ["context", "background", "you are a", "role"]):
        pass
    else:
        issues.append("- Missing Context/Role: Consider defining a role (e.g., 'You are a expert...') or providing background.")

    # Check for Objective
    if any(word in prompt_text.lower() for word in ["objective", "goal", "task", "do", "write", "create", "analyze"]):
        pass
    else:
        issues.append("- Ambiguous Objective: Ensure the core task is explicitly stated.")

    # Check for Output Format
    if any(word in prompt_text.lower() for word in ["format", "structure", "markdown", "json", "list", "table"]):
        pass
    else:
        issues.append("- Missing Output Format: Specify how the AI should structure its response (e.g., 'Return the result as a Markdown table').")

    # Check for Delimiters
    if any(char in prompt_text for char in ["\"\"\"", "###", "---", "<", ">"]):
        pass
    else:
        issues.append("- No Delimiters: Use delimiters like '###' or '\"\"\"' to separate instructions from input data.")

    # Check for Few-Shot
    if "example" not in prompt_text.lower():
        issues.append("- No Examples: Adding 1-2 examples (few-shot) can significantly improve performance for complex tasks.")

    return issues

def main():
    parser = argparse.ArgumentParser(description="Analyze an AI prompt for structural weaknesses.")
    parser.add_argument("file", help="Path to a text file containing the prompt.")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print(f"--- Analysis for: {args.file} ---")
    issues = analyze_prompt(content)
    
    if not issues:
        print("✅ Prompt looks structurally sound!")
    else:
        print("⚠️ Potential Improvements Found:")
        for issue in issues:
            print(issue)
    
    print("\nTip: Use the CO-STAR framework (Context, Objective, Style, Tone, Audience, Response) for best results.")

if __name__ == "__main__":
    main()
