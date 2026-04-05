import sys
import json
import re

def analyze_express_error(error_log):
    """
    Analyzes common Express.js/Node.js error patterns.
    """
    suggestions = []
    
    # Common Express/Mongoose Error Patterns
    patterns = {
        r"EADDRINUSE": "Port is already in use. Another instance of the server might be running elsewhere, or another application is using this port. Use `lsof -i :<port>` to find and kill the process.",
        r"ValidationError: .*": "Mongoose validation failed. Check if the input data matches your schema requirements (required fields, types, etc.). Ensure all required fields are present in the request body.",
        r"CastError: Cast to ObjectId failed": "Invalid ID format passed to a database query. Check if the ID string matches the MongoDB ObjectId format. This often happens in route parameters like `/api/users/:id`.",
        r"MongoNetworkError": "Database connection failed. Ensure your MongoDB URI is correct, the database is accessible, and your IP is whitelisted (if using Atlas).",
        r"Route.get\(\) requires a callback function but got a \[object Undefined\]": "Check your route definitions. You're likely trying to use a controller function that wasn't exported correctly or is misspelled in the import.",
        r"PayloadTooLargeError": "The request body is too large. Consider increasing the limit in your body-parser middleware: `app.use(express.json({ limit: '10mb' }))`.",
        r"JsonWebTokenError": "Invalid JWT. Check if the token was signed correctly or if the secret key matches on both sides. Verify the 'Authorization' header format.",
        r"ERR_HTTP_HEADERS_SENT": "Multiple responses sent for a single request. Ensure you are using `return res.status(...).json(...)` to exit early and avoid continuing execution after sending a response.",
        r"req.body is undefined": "Missing body-parsing middleware. Add `app.use(express.json())` and `app.use(express.urlencoded({ extended: true }))` before your routes.",
        r"MongooseServerSelectionError": "The server failed to connect to MongoDB. Check your connection string and ensure the database server is running.",
        r"RangeError: Maximum call stack size exceeded": "Infinite recursion in your middleware or logic. Check your `next()` calls and ensure you aren't calling the same middleware recursively.",
        r"TokenExpiredError": "The JWT has expired. The client needs to re-authenticate or use a refresh token.",
        r"ReferenceError: next is not defined": "You are trying to call `next()` in a middleware or route handler, but it wasn't included in the parameter list: `(req, res, next) => { ... }`.",
        r"SyntaxError: Unexpected token": "Likely a JSON parsing error. The client sent malformed JSON, or you are trying to parse something that isn't JSON.",
        r"UnhandledPromiseRejectionWarning": "An async operation failed without a `.catch()` block. Wrap your async route logic in a `try-catch` block and pass the error to `next(err)`."
    }
    
    for pattern, advice in patterns.items():
        if re.search(pattern, error_log, re.IGNORECASE):
            suggestions.append({"pattern": pattern, "advice": advice})
            
    if not suggestions:
        suggestions.append({
            "pattern": "Unknown",
            "advice": "General debugging recommended: Check middleware order, API responses, and database connectivity."
        })
        
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No error log provided. Usage: python analyze_error.py <error_log>"}))
        sys.exit(1)
        
    log_input = sys.argv[1]
    result = analyze_express_error(log_input)
    print(json.dumps(result, indent=2))
