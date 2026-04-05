import os
import sys
import uuid
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agenttrap.db.client import DBClient
from agenttrap.registry.loader import ScenarioRegistry
from agenttrap.workspace.simulator import WorkspaceSimulator
from agenttrap.sandbox.executor import ToolExecutor
from agenttrap.engine.tracer import ActionTracer
from agenttrap.engine.classifier import OutcomeClassifier
from agenttrap.agent.runtime import AgentRuntime

def run_e2e_demo():
    print("=== AgentTrap Phase 4: Full Local Integration ===")
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set. The litellm call may fail unless using local models.")

    # 1. Initialize Subsystems
    db = DBClient("demo_e2e.db")
    tracer = ActionTracer(db)
    classifier = OutcomeClassifier(db)
    executor = ToolExecutor()
    workspace = WorkspaceSimulator()
    registry = ScenarioRegistry()
    
    # 2. Setup mock Evaluation Run in DB
    run_id = str(uuid.uuid4())
    result_id = str(uuid.uuid4())
    scenario = registry.load_all()[0]  # Let's take the first scenario
    print(f"\n[+] Running Target Scenario: {scenario.name} ({scenario.vector})")

    default_model = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

    with db.get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO runs (id, name, created_at, agent_config, model, total_scenarios) VALUES (?, 'demo_e2e', 'now', 'baseline', ?, 1)", (run_id, default_model))
        conn.execute("INSERT INTO scenario_results (id, run_id, scenario_id, vector, harm_domain, outcome, steps_taken, attack_succeeded, created_at) VALUES (?, ?, ?, ?, ?, 'incomplete', 0, 0, 'now')", (result_id, run_id, scenario.id, scenario.vector, scenario.harm_domain))
        conn.commit()

    # 3. Simulate and Execute loop
    # In a real environment with keys, this actually talks to Gemini
    # To ensure safety on a CI or dry run without keys, we could run a mock, but we'll try the real litellm call.
    try:
        workspace.inject_scenario(scenario)
        tracer.start_trace(result_id)
        
        runtime = AgentRuntime("baseline", executor, tracer, model=default_model, max_steps=2)
        print("\n[+] Triggering LLM Core Loop...")
        runtime.run_scenario(scenario, workspace)
        
        print("\n[+] LLM Loop Finished. Classifying Output...")
        result = classifier.classify_outcome(run_id, scenario, tracer.get_traces())
        print(f"Classification Outcome: {result['outcome']}")
        print(f"Steps Taken: {result['steps']}")
        if result['attack_success']:
            print(f"Failure Mode: {result['failure_mode']}")

    except Exception as e:
        print(f"Failed to complete LLM run: {e}")
        print("Note: Provide OPENAI_API_KEY environment variable to test real Litellm execution locally.")

if __name__ == "__main__":
    run_e2e_demo()
