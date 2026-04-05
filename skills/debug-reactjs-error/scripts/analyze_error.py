import sys
import json
import re

def analyze_error(error_log):
    """
    Analyzes common React error patterns and suggests likely causes.
    """
    suggestions = []
    
    # Common React Error Patterns
    patterns = {
        r"Too many re-renders": "Infinite loop detected. This usually happens when you call a state update function in the main body of the component or inside a `useEffect` without proper dependencies.",
        r"Cannot update a component while rendering a different component": "State update triggered during render phase. Move the state update to a `useEffect` or an event handler to avoid this warning.",
        r"Invalid hook call": "Hooks can only be called inside the body of a functional component. You might be calling a hook inside a loop, condition, or a regular JavaScript function.",
        r"rendered more hooks than during the previous render": "Hooks must be called in the same order every time. Do not place hooks inside `if` statements or loops.",
        r"Objects are not valid as a React child": "You're trying to render a plain object. Instead, render a primitive (string, number) or an element, or use `JSON.stringify(obj)` for debugging.",
        r"ReferenceError: .* is not defined": "A variable or function is being used before it's defined or is out of scope. Check your imports, especially for components used in JSX.",
        r"TypeError: Cannot read property '.*' of undefined": "Accessing a property on an undefined object. This often happens with async data fetching. Use optional chaining `?.` or initialize state with a default value.",
        r"Warning: Each child in a list should have a unique \"key\" prop": "List rendering missing unique 'key' props. Add a stable ID (not array index if elements can reorder) to the elements returned from `.map()`.",
        r"Warning: Invalid DOM property \"class\"": "JSX Syntax error. In React, use `className` instead of `class` and `htmlFor` instead of `for`.",
        r"Warning: Can't perform a React state update on an unmounted component": "Memory leak detected. Ensure you're canceling async operations (API calls, timers) in the cleanup function of `useEffect`.",
        r"React.createElement: type is invalid": "Check your imports and exports. You might be importing a default export as a named export, or vice-versa, or the file path is incorrect.",
        r"Maximum update depth exceeded": "Infinite loop in your component logic. Check `useEffect` dependencies or state updates triggered by prop changes.",
        r"Hydration failed": "Server-side versus client-side mismatch. The HTML rendered by the server doesn't match the client's initial render. Check for random values (dates, Math.random) or conditional rendering based on `window`.",
        r"Expected server HTML to contain a matching": "Another hydration error common in SSR. Ensure your component doesn't use browser-only globals (like `localStorage`) during the initial render.",
        r"Stale closure": "A function (like an event handler) is using an old value of state. This happens when the function is defined inside a component but not updated when state changes. Use `useCallback` or `useEffect` dependencies.",
        r"Cannot read property 'map' of null": "The data you're mapping over is null. Check your initial state or the API response. Use `data?.map(...)` or `(data || []).map(...)`."
    }
    
    for pattern, advice in patterns.items():
        if re.search(pattern, error_log, re.IGNORECASE):
            suggestions.append({"pattern": pattern, "advice": advice})
            
    if not suggestions:
        suggestions.append({
            "pattern": "Unknown",
            "advice": "General debugging recommended: Trace the data flow and verify component props/state."
        })
        
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No error log provided. Usage: python analyze_error.py <error_log>"}))
        sys.exit(1)
        
    log_input = sys.argv[1]
    result = analyze_error(log_input)
    print(json.dumps(result, indent=2))
