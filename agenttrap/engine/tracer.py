import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from agenttrap.db.client import DBClient

class ActionTracer:
    """
    Records agent actions to the database.
    """
    def __init__(self, db_client: DBClient):
        self.db = db_client
        self.current_scenario_result_id = None
        self.step_counter = 0
        self.current_traces: List[Dict[str, Any]] = []

    def start_trace(self, scenario_result_id: str):
        self.current_scenario_result_id = scenario_result_id
        self.step_counter = 0
        self.current_traces = []

    def log_action(self, tool_name: str, parameters: Dict[str, Any], reasoning: str, verdict: str = "intended"):
        """Logs a single tool step into the trace sequence."""
        if not self.current_scenario_result_id:
            raise ValueError("Trace not started properly.")
            
        trace_id = str(uuid.uuid4())
        self.step_counter += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        
        trace = {
            "id": trace_id,
            "scenario_result_id": self.current_scenario_result_id,
            "step_index": self.step_counter,
            "tool_name": tool_name,
            "parameters": json.dumps(parameters),
            "reasoning": reasoning,
            "verdict": verdict,
            "timestamp": timestamp
        }
        
        self.current_traces.append(trace)
        
        # Persist individually
        query = """
        INSERT INTO action_traces 
        (id, scenario_result_id, step_index, tool_name, parameters, reasoning, verdict, timestamp)
        VALUES (:id, :scenario_result_id, :step_index, :tool_name, :parameters, :reasoning, :verdict, :timestamp)
        """
        with self.db.get_connection() as conn:
            conn.execute(query, trace)
            conn.commit()
            
    def get_traces(self):
        return self.current_traces
