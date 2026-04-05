import sys
import os
import re
import json

def suggest_express_logs(filepath):
    """
    Analyzes an Express.js controller or route file for log suggestions.
    """
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    suggestions = []
    
    # Identify route handlers (req, res, next)
    route_matches = re.findall(r"(?:const|async)\s+(.*?)\s*=\s*(?:async\s*)?\((?:req,\s*res|req,\s*res,\s*next)\)\s*=>\s*{", content)
    for handler in route_matches:
        suggestions.append({
            "handler": handler,
            "type": "route_handler",
            "suggestion": f"Add `console.log('// [DEBUG] Processing request in {handler}:', req.body);` at the start."
        })
        
    # Identify database calls (await Model.find, etc.)
    db_matches = re.findall(r"await\s+(.*?)\.(find|findOne|findById|create|update|delete|save)\((.*?)\)", content)
    for model, action, params in db_matches:
        suggestions.append({
            "model": model,
            "action": action,
            "type": "db_query",
            "suggestion": f"Add `console.log('// [DEBUG] DB {action} on {model} with:', {params});` before the await."
        })
        
    # Check for res.json() or res.send()
    res_matches = re.findall(r"res\.(json|send|status)\((.*?)\)", content)
    for method, data in res_matches:
        suggestions.append({
            "method": method,
            "type": "api_response",
            "suggestion": f"Add `console.log('// [DEBUG] API response ({method}):', {data});` before the response is sent."
        })
        
    if not suggestions:
        suggestions.append({
            "type": "general",
            "suggestion": "Add `console.log('// [DEBUG] Middleware executed');` at the top of the file."
        })
        
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided. Usage: python suggest_logs.py <file_path>"}))
        sys.exit(1)
        
    file_path = sys.argv[1]
    result = suggest_express_logs(file_path)
    print(json.dumps(result, indent=2))
