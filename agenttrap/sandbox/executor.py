from typing import Dict, Any
from agenttrap.sandbox.tools import MockTools

class ToolExecutor:
    """Executes mock tools safely and parses outputs."""

    def __init__(self):
        self.available_tools = MockTools.get_all_tool_names()

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a mapped mock tool. Returns an error dict if tool not found.
        """
        if tool_name not in self.available_tools:
            return {"status": "error", "message": f"Tool '{tool_name}' not found."}
        
        func = getattr(MockTools, tool_name)
        try:
            # We pass **parameters dict directly to the method.
            result = func(**parameters)
            return result
        except TypeError as e:
            # Catch signature mismatches
            return {"status": "error", "message": f"Parameter error for '{tool_name}': {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error executing '{tool_name}': {e}"}
