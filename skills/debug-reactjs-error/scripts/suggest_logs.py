import sys
import os
import re
import json

def suggest_logs(filepath):
    """
    Analyzes a React component and suggests where to add logs.
    """
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    suggestions = []
    
    # Identify state variables (useState)
    state_matches = re.findall(r"const \[(.*?), (.*?)\] = useState\((.*?)\)", content)
    for state_var, set_state, initial in state_matches:
        suggestions.append({
            "variable": state_var,
            "type": "state",
            "suggestion": f"Add `console.log('// [DEBUG] {state_var}:', {state_var});` before return or in useEffect."
        })
        
    # Identify effect hooks
    effect_matches = re.findall(r"useEffect\(.*?, \[(.*?)\]\)", content)
    for deps in effect_matches:
        suggestions.append({
            "type": "effect",
            "dependencies": deps,
            "suggestion": f"Add `console.log('// [DEBUG] Effect triggered with deps: {deps}');` inside the effect hook."
        })
        
    # Identify function calls (API calls, etc.)
    func_matches = re.findall(r"const (.*?) = async \(.*?\) => \{", content)
    for func_name in func_matches:
        suggestions.append({
            "function": func_name,
            "type": "async_function",
            "suggestion": f"Add logs at the start and end of {func_name} to trace the lifecycle."
        })
        
    if not suggestions:
        suggestions.append({
            "type": "general",
            "suggestion": "Add `console.log('// [DEBUG] Render cycle triggered');` at the top of the component."
        })
        
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided. Usage: python suggest_logs.py <file_path>"}))
        sys.exit(1)
        
    file_path = sys.argv[1]
    result = suggest_logs(file_path)
    print(json.dumps(result, indent=2))
