from datetime import datetime

from fastapi import HTTPException

from phoenix_ai_services.tool_sandbox import safe_eval


def run_tool(tool_name: str, input_data: str):
    try:
        if tool_name == "calculator":
            result = eval(input_data, {"__builtins__": {}}, {})
        elif tool_name == "system_time":
            result = datetime.now().isoformat()
        elif tool_name == "python":
            result = safe_eval(input_data)
        else:
            raise ValueError(f"Tool '{tool_name}' not found")

        return {"tool": tool_name, "result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")
