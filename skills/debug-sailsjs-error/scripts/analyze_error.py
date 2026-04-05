import sys
import json
import re

def analyze_sailsjs_error(error_log):
    """
    Analyzes common Sails.js/Waterline error patterns and returns targeted fix suggestions.
    """
    suggestions = []

    # Sails.js / Waterline Error Patterns
    patterns = {
        r"E_UNIQUE": "A uniqueness constraint was violated. Another record with the same value already exists. Check the model attribute marked `unique: true` and handle the error gracefully in the action (e.g., catch the error and return a user-friendly message).",
        r"E_MISSING_OR_INVALID_PARAMS": "The action or helper received inputs that don't match its defined `inputs` block. Check that all required inputs are being passed correctly from the client or calling code, and verify their types match the schema.",
        r"E_INVALID_CRITERIA": "A Waterline query was called with invalid or undefined criteria. Check for `undefined` values being passed to `.findOne()`, `.find()`, `.update()`, or `.destroy()`. A common cause is an unresolved route parameter.",
        r"E_UNAUTHENTICATED": "A policy blocked the request because the user is not authenticated. Ensure the session is active, the JWT token is valid and being sent in the `Authorization` header, or that the policy logic correctly calls `proceed()` for valid users.",
        r"E_FORBIDDEN": "A policy rejected the request because the user lacks the necessary permissions. Review the policy logic to confirm the authorization checks are correct.",
        r"UsageError": "A Sails helper or method was called incorrectly. Check the inputs/options passed to the helper and compare against its defined `inputs` contract. Ensure all required inputs are present.",
        r"AdapterError": "A low-level database adapter error occurred. Check your database connection configuration in `config/datastores.js` and ensure the database server is reachable.",
        r"exits\.error is not a function": "The action was called with an incomplete `exits` object. Ensure the action is being called via Sails.js routing or `sails.helpers.*()` and not invoked directly without the exits context.",
        r"Cannot call an exit after the machine has already exited": "An exit (e.g., `exits.success()`) was called more than once in the same action. Ensure only one exit is called per request, and use `return exits.success()` to prevent further execution.",
        r"Error: Timeout": "The action or helper timed out. A long-running asynchronous operation (DB query, external API call) may not be completing. Check your async logic and await all promises.",
        r"response.send: Cannot set headers after they are sent to the client": "A response was sent more than once for the same request. Ensure you use `return exits.success()` or `return res.ok()` to exit the action immediately after sending a response.",
        r"ECONNREFUSED": "The Sails.js server failed to connect to the database or an external service. Verify your `config/datastores.js` connection string and ensure the target service (e.g., MongoDB, MySQL) is running and accessible.",
        r"ER_ACCESS_DENIED_ERROR": "Database access was denied. Check your database username, password, and host configuration in `config/datastores.js`.",
        r"not found": "A resource was not found. In an action, ensure you check the result of `.findOne()` before proceeding and call `exits.notFound()` if the result is `undefined`.",
        r"blueprint": "A blueprint route may be conflicting with a custom route or action. Review your `config/routes.js` and ensure custom routes don't shadow or conflict with auto-generated blueprint routes.",
    }

    for pattern, advice in patterns.items():
        if re.search(pattern, error_log, re.IGNORECASE):
            suggestions.append({"pattern": pattern, "advice": advice})

    if not suggestions:
        suggestions.append({
            "pattern": "Unknown",
            "advice": "General Sails.js debugging recommended: Check the full stack trace in the `sails lift` terminal output, verify all action exits are being called, and ensure policies call `proceed()` on success."
        })

    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No error log provided. Usage: python analyze_error.py <error_log>"}))
        sys.exit(1)

    log_input = sys.argv[1]
    result = analyze_sailsjs_error(log_input)
    print(json.dumps(result, indent=2))
