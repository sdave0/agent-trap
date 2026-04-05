import uuid
from typing import List, Optional
from datetime import datetime, timezone
import json

from pydantic import BaseModel
from agenttrap.db.client import DBClient
from agenttrap.registry.loader import ScenarioRegistry
from agenttrap.workspace.simulator import WorkspaceSimulator
from agenttrap.sandbox.executor import ToolExecutor
from agenttrap.engine.tracer import ActionTracer
from agenttrap.engine.classifier import OutcomeClassifier
from agenttrap.agent.runtime import AgentRuntime

def run_evaluation_batch(
    run_id: str,
    db_path: str,
    scenarios: List[str],
    agent_configs: List[str],
    model: str,
    max_steps: int = 3
):
    """
    Background worker that executes scenarios sequentially to avoid DB locks.
    Every major dependency is instantiated within the worker to isolate state.
    """
    db = DBClient(db_path)
    registry = ScenarioRegistry()
    registry_scenarios = registry.load_all()
    
    # Map requested 'scenarios' to actual objects ('all' means all)
    if "all" in scenarios:
        target_scenarios = registry_scenarios
    else:
        target_scenarios = [s for s in registry_scenarios if s.id in scenarios]
        
    for config in agent_configs:
        for scenario in target_scenarios:
            
            executor = ToolExecutor()
            workspace = WorkspaceSimulator()
            tracer = ActionTracer(db)
            classifier = OutcomeClassifier(db)
            
            result_id = str(uuid.uuid4())
            
            # Setup incomplete scenario_result state
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO scenario_results (id, run_id, scenario_id, vector, harm_domain, outcome, steps_taken, attack_succeeded, created_at) VALUES (?, ?, ?, ?, ?, 'incomplete', 0, 0, ?)",
                    (result_id, run_id, scenario.id, scenario.vector, scenario.harm_domain, datetime.now(timezone.utc).isoformat())
                )
                conn.commit()
                
            workspace.inject_scenario(scenario)
            tracer.start_trace(result_id)
            
            runtime = AgentRuntime(config, executor, tracer, model=model, max_steps=max_steps)
            runtime.run_scenario(scenario, workspace)
            
            # 4. Classify and Store Results
            classifier.classify_outcome(run_id, scenario, tracer.get_traces(), result_id=result_id)
            
            # Update Runs progress ticker
            with db.get_connection() as conn:
                conn.execute("UPDATE runs SET completed_scenarios = completed_scenarios + 1 WHERE id = ?", (run_id,))
                conn.commit()

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM scenario_results WHERE run_id = ? AND outcome != 'incomplete'", (run_id,))
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as success FROM scenario_results WHERE run_id = ? AND outcome = 'attack_success'", (run_id,))
        success = cursor.fetchone()["success"]
        
        asr_overall = (success / total) * 100 if total > 0 else 0.0
        
        conn.execute("UPDATE runs SET status = 'completed', asr_overall = ? WHERE id = ?", (asr_overall, run_id))
        conn.commit()
