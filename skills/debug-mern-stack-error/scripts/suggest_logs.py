import sys
import os
import re
import json

def suggest_mern_logs(filepath):
    """
    Analyzes MERN stack files for full-stack log suggestions.
    """
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    suggestions = []
    
    # Frontend - Axios/Fetch (React)
    axios_matches = re.findall(r"(?:axios|api)\.(get|post|put|delete|patch)\((.*?)\)", content)
    for method, endpoint in axios_matches:
        suggestions.append({
            "method": method,
            "endpoint": endpoint,
            "type": "frontend_api_call",
            "suggestion": f"Add `console.log('// [DEBUG] Axios {method} to {endpoint}');` before call."
        })
        
    # Backend - Express routes
    route_matches = re.findall(r"router\.(get|post|put|delete|patch)\((.*?),(.*?)\)", content)
    for method, path, handler in route_matches:
        suggestions.append({
            "method": method,
            "path": path,
            "type": "backend_route",
            "suggestion": f"Add `console.log('// [DEBUG] Incoming MERN {method} request on {path}');` at the top of the route or middleware."
        })
        
    # Full-stack auth (JWT)
    auth_matches = re.findall(r"(?:localStorage\.setItem|setHeader)\(.*?(?:token|jwt).*?\)", content)
    for auth in auth_matches:
        suggestions.append({
            "type": "auth_handling",
            "suggestion": f"Add `console.log('// [DEBUG] Auth token being set/sent');` to trace full-stack auth."
        })
        
    if not suggestions:
        suggestions.append({
            "type": "general",
            "suggestion": "Add `console.log('// [DEBUG] MERN stack tracing initiated');`."
        })
        
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided. Usage: python suggest_logs.py <file_path>"}))
        sys.exit(1)
        
    file_path = sys.argv[1]
    result = suggest_mern_logs(file_path)
    print(json.dumps(result, indent=2))
