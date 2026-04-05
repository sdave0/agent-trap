import uuid
import random
from datetime import datetime, timezone
from typing import List
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os

from agenttrap.db.client import DBClient
from agenttrap.registry.loader import ScenarioRegistry
from agenttrap.api.orchestrator import run_evaluation_batch

app = FastAPI(title="AgentTrap Evaluation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DBClient("agenttrap.db")
registry = ScenarioRegistry()

class RunRequest(BaseModel):
    name: str
    agent_configs: List[str] = ["baseline", "instructed"]
    scenarios: List[str] = ["all"]
    model: str = Field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"))
    max_steps_per_scenario: int = 10
    notes: str = ""

@app.post("/api/runs")
def create_run(request: RunRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    scenario_poolSize = 20 if "all" in request.scenarios else len(request.scenarios)
    total_scenarios = scenario_poolSize * len(request.agent_configs)
    
    with db.get_connection() as conn:
        conn.execute(
            """INSERT INTO runs 
            (id, name, created_at, agent_config, model, status, total_scenarios, completed_scenarios, notes)
            VALUES (?, ?, ?, ?, ?, 'pending', ?, 0, ?)""",
            (run_id, request.name, created_at, ",".join(request.agent_configs), request.model, total_scenarios, request.notes)
        )
        conn.commit()
        
    background_tasks.add_task(
        run_evaluation_batch,
        run_id,
        "agenttrap.db",
        request.scenarios,
        request.agent_configs,
        request.model,
        request.max_steps_per_scenario
    )
    
    return {"message": "Run queued successfully.", "run_id": run_id}

@app.get("/api/runs")
def list_runs():
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, created_at, status, total_scenarios, completed_scenarios, asr_overall, agent_config FROM runs ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
        run = cursor.fetchone()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found.")
        return dict(run)

@app.get("/api/runs/{run_id}/results")
def get_run_results(run_id: str):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scenario_results WHERE run_id = ?", (run_id,))
        return [dict(row) for row in cursor.fetchall()]

@app.get("/api/results/{result_id}/traces")
def get_result_traces(result_id: str):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM action_traces WHERE scenario_result_id = ? ORDER BY step_index ASC", (result_id,))
        return [dict(row) for row in cursor.fetchall()]

@app.get("/api/stats")
def get_stats():
    """Calculates global ASR metrics for the dashboard."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        def get_asr(config):
            cursor.execute("SELECT AVG(asr_overall) as asr FROM runs WHERE agent_config LIKE ? AND status = 'completed'", (f"%{config}%",))
            res = cursor.fetchone()
            return res['asr'] if res and res['asr'] is not None else 0.0

        return {
            "baseline_asr": get_asr("baseline"),
            "instructed_asr": get_asr("instructed"),
            "total_runs": cursor.execute("SELECT COUNT(*) as total FROM runs").fetchone()['total']
        }

@app.get("/api/scenarios")
def list_scenarios():
    try:
        scenarios = registry.load_all()
        return [s.model_dump() for s in scenarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
