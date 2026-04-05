import json
from typing import Dict, Any
from openai import OpenAI
import time  # TEMP: Added for dev rate limits
import os

from agenttrap.models.scenario import Scenario
from agenttrap.workspace.simulator import WorkspaceSimulator
from agenttrap.sandbox.executor import ToolExecutor
from agenttrap.engine.tracer import ActionTracer
from agenttrap.agent.prompts import get_system_prompt
from agenttrap.agent.schemas import get_tools_schema

class AgentRuntime:
    """Core Loop that executes the scenario locally with LiteLLM."""
    
    def __init__(
        self,
        config: str, # "baseline" | "instructed"
        tool_executor: ToolExecutor,
        tracer: ActionTracer,
        model: str = None,
        max_steps: int = 10
    ):
        self.config = config
        self.tool_executor = tool_executor
        self.tracer = tracer
        self.model = model or os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
        self.max_steps = max_steps
        
    def run_scenario(self, scenario: Scenario, workspace: WorkspaceSimulator) -> None:
        """
        Executes a full scenario trace.
        Requires tracer.start_trace() to have been called upstream with a valid ID!
        """
        ctx = workspace.get_context()
        
        # 1. Inject schema overrides for 'skill' vector injections.
        tools = get_tools_schema(ctx.get("tool_descriptions", {}))
        
        # Construct context block
        ctx_block = f"Inbox: {json.dumps(ctx['inbox'])}\nWeb State: {ctx['web_content']}"
        system_content = get_system_prompt(self.config, ctx_block, scenario.legitimate_task)
        
        # We start our LLM message history
        messages = [{"role": "system", "content": system_content}]
        messages.append({"role": "user", "content": "Begin task now."})
        
        client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        for step in range(self.max_steps):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.0
                )
            except Exception as e:
                print(f"OpenAI Client completion error: {e}")
                import traceback
                traceback.print_exc()
                break
                
            msg = response.choices[0].message
            messages.append(dict(msg))
            
            # If the LLM didn't call a tool, we assume it's done.
            if not msg.tool_calls:
                break
                
            # If it did call a tool, we execute, trace, and append the result.
            tool_call = msg.tool_calls[0]
            function_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}
                
            # Execute sandbox tool securely
            result = self.tool_executor.execute(function_name, arguments)
            
            # Log trace reliably
            reasoning = "Executing explicit tool call."
            self.tracer.log_action(function_name, arguments, reasoning)
            
            # Respond to the LLM so it can observe state
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result)
            })
