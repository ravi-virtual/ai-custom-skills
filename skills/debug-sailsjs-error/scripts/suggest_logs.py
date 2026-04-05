import sys
import os
import re
import json

def suggest_sailsjs_logs(filepath):
    """
    Analyzes a Sails.js action, helper, or model file and suggests strategic
    console.log placements for debugging.
    """
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    suggestions = []

    # ---- Sails.js ActionsV2: fn async function ----
    # Matches: fn: async function (inputs, exits) {
    action_fn_matches = re.findall(r"fn:\s*async\s+function\s*\(([\w,\s]+)\)", content)
    for params in action_fn_matches:
        param_list = [p.strip() for p in params.split(',')]
        inputs_param = param_list[0] if param_list else 'inputs'
        exits_param = param_list[1] if len(param_list) > 1 else 'exits'
        suggestions.append({
            "type": "action_fn_start",
            "suggestion": f"Add at the top of `fn`: `console.log('// [DEBUG] Action inputs:', {inputs_param});`"
        })
        suggestions.append({
            "type": "action_fn_exits",
            "suggestion": f"Add before every `{exits_param}.success()` call: `console.log('// [DEBUG] Calling exits.success with:', <result_variable>);`"
        })

    # ---- Sails.js Helpers: fn async function ----
    # Matches: fn: async function ({ input1, input2 }, ... )
    helper_fn_matches = re.findall(r"fn:\s*async\s+function\s*\(\s*\{([^}]+)\}", content)
    for destructured_inputs in helper_fn_matches:
        input_names = [i.strip() for i in destructured_inputs.split(',')]
        suggestions.append({
            "type": "helper_fn_start",
            "suggestion": f"Add at the top of `fn`: `console.log('// [DEBUG] Helper inputs:', {{ {', '.join(input_names)} }});`"
        })
        suggestions.append({
            "type": "helper_fn_return",
            "suggestion": "Add before `return`: `console.log('// [DEBUG] Helper returning:', <return_value>);`"
        })

    # ---- Waterline ORM Queries ----
    # Matches: await Model.find(...), await User.findOne(...), etc.
    db_matches = re.findall(r"await\s+(\w+)\.(findOne|find|create|update|updateOne|destroy|destroyOne)\(([^)]*)\)", content)
    for model, action, params in db_matches:
        suggestions.append({
            "model": model,
            "action": action,
            "type": "waterline_query",
            "suggestion": f"Add before the `await {model}.{action}(...)` call: `console.log('// [DEBUG] Waterline {action} on {model} with criteria:', {params.strip() or '{}'});`"
        })
        suggestions.append({
            "type": "waterline_result",
            "suggestion": f"Add after the `await {model}.{action}(...)` call: `console.log('// [DEBUG] Waterline {action} result:', <result_variable>);`"
        })

    # ---- Lifecycle Callbacks in Models ----
    # Matches: beforeCreate, afterCreate, beforeUpdate, etc.
    lifecycle_matches = re.findall(r"(before|after)(Create|Update|Destroy|Validate)\s*(?::\s*async\s+function|:\s*function)", content)
    for prefix, event in lifecycle_matches:
        callback_name = f"{prefix}{event}"
        suggestions.append({
            "type": "lifecycle_callback",
            "callback": callback_name,
            "suggestion": f"Add at the top of `{callback_name}`: `console.log('// [DEBUG] Lifecycle {callback_name} triggered with values:', valuesToSet);`"
        })

    # ---- Policy Functions ----
    # Matches: module.exports = async function (req, res, proceed) {
    policy_matches = re.findall(r"module\.exports\s*=\s*async\s+function\s*\(\s*req,\s*res,\s*(proceed|next)\s*\)", content)
    for proceed_param in policy_matches:
        suggestions.append({
            "type": "policy_function",
            "suggestion": f"Add at the top of the policy: `console.log('// [DEBUG] Policy triggered for:', req.method, req.path);`"
        })
        suggestions.append({
            "type": "policy_proceed",
            "suggestion": f"Add before `{proceed_param}()`: `console.log('// [DEBUG] Policy calling {proceed_param}() - user is authorized.');`"
        })

    if not suggestions:
        suggestions.append({
            "type": "general",
            "suggestion": "No recognizable Sails.js patterns found. Add `console.log('// [DEBUG] File reached:', __filename);` at the top of the file to confirm it is being executed."
        })

    return suggestions


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided. Usage: python suggest_logs.py <file_path>"}))
        sys.exit(1)

    file_path = sys.argv[1]
    result = suggest_sailsjs_logs(file_path)
    print(json.dumps(result, indent=2))
