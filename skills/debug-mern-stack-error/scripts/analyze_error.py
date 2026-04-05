import sys
import json
import re

def analyze_mern_error(error_log):
    """
    Analyzes common full-stack MERN integration error patterns.
    """
    suggestions = []
    
    # Common MERN Error Patterns
    patterns = {
        r"Access-Control-Allow-Origin": "CORS issue. The backend is not allowing requests from the frontend origin. Check your `cors` configuration in Express and ensure `origin` matches your React dev server (usually localhost:5173 or 3000).",
        r"Network Error": "React cannot reach the Express server. Verify the server is running and the URL in your Axios/Fetch call is correct. Check if the server port is correct.",
        r"401 \(Unauthorized\)": "Authentication failure. The JWT is either missing, invalid, or expired. Check if the 'Authorization' header is being sent correctly in Axios interceptors.",
        r"404 \(Not Found\)": "The API endpoint does not exist. Verify the route definition in Express and ensure any prefixes like `/api` are included in the React request URL.",
        r"400 \(Bad Request\)": "Validation failed on the backend. The frontend is likely sending data that doesn't match the Mongoose schema or Yup/Zod validator. Compare the React request body with the Express schema.",
        r"500 \(Internal Server Error\)": "The backend server crashed while processing the request. Check the Express terminal for the stack trace to identify the bug in the controller or middleware.",
        r"Proxy error: Could not proxy request": "Vite/CRA proxy failure. The backend server is likely not running on the port specified in `vite.config.ts` or `package.json` proxy field.",
        r"AxiosError: Request failed with status code 403": "Forbidden. This often means CORS allows the origin but the specific request fails (e.g., missing 'withCredentials: true' for cookies or a mismatch in allowed methods).",
        r"Failed to fetch": "The browser blocked the request or the server is down. Check for CORS errors in the console or verify the server status.",
        r"Unexpected token < in JSON at position 0": "You're getting HTML (likely a 404 or index.html) instead of JSON. This happens when a React route or a missing API route falls back to the frontend's index.html.",
        r"ERR_CONNECTION_REFUSED": "The backend server is not listening on the expected port. Confirm the Express server is successfully started and listening.",
        r"Preflight response is not successful": "CORS preflight (OPTIONS) request failed. Ensure the backend handles OPTIONS requests (automatically done by the `cors` middleware) and allows the required headers.",
        r"ECONNRESET": "The connection was abruptly closed by the server. Check if the Express server crashed or if there's a timeout/limit being hit.",
        r"Error: No 'Access-Control-Allow-Origin' header is present": "CORS block. You MUST add the `cors()` middleware in your Express `app.js` or `server.js` before any routes.",
        r"withCredentials": "If you are using cookies for sessions/JWT, ensure `withCredentials: true` is set in the React Axios config AND `credentials: true` is set in the backend `cors` config."
    }
    
    for pattern, advice in patterns.items():
        if re.search(pattern, error_log, re.IGNORECASE):
            suggestions.append({"pattern": pattern, "advice": advice})
            
    if not suggestions:
        suggestions.append({
            "pattern": "Unknown",
            "advice": "General MERN debugging: Trace the request from the React component to the Axios call, then to the Express route and controller."
        })
        
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No error log provided. Usage: python analyze_error.py <error_log>"}))
        sys.exit(1)
        
    log_input = sys.argv[1]
    result = analyze_mern_error(log_input)
    print(json.dumps(result, indent=2))
