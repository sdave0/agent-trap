import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from agenttrap.api.main import app

def run_demo():
    print("=== AgentTrap Phase 5: Pipeline Orchestration API ===")
    
    # We use TestClient as a reliable local execution harness for scripts without spinning up actual uvicorn socket
    client = TestClient(app)
    
    # Check scenarios
    scenarios = client.get("/api/scenarios").json()
    print(f"\n[+] Fetched {len(scenarios)} Scenarios endpoints safely.")

    payload = {
        "name": "E2E Pipeline Demo Test",
        "agent_configs": ["baseline"],
        "scenarios": ["SI-01"], # run 1 scenario to save API costs
        "model": os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        "notes": "Triggering Sequential Execution!"
    }
    
    print("\n[+] Triggering full pipeline pipeline via API background worker...")
    response = client.post("/api/runs", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    run_id = response.json()["run_id"]
    
    # Poll for completion
    print("\n[+] Polling /api/runs for completion state...")
    max_retries = 5
    while max_retries > 0:
        run_data = client.get(f"/api/runs/{run_id}").json()
        print(f"  -> DB Run Status: {run_data['status']} | Completed: {run_data['completed_scenarios']} / {run_data['total_scenarios']}")
        
        if run_data['status'] == 'completed':
            print("\n[+] Background Execution Successfully Navigated SQLite Pipeline sequentially!")
            break
            
        time.sleep(2)
        max_retries -= 1
        
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    run_demo()
