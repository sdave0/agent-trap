import pytest
from agenttrap.workspace.simulator import WorkspaceSimulator
from agenttrap.models.scenario import Scenario, TargetAction

@pytest.fixture
def base_scenario_data():
    return {
        "id": "test",
        "name": "test",
        "harm_domain": "test",
        "description": "test",
        "legitimate_task": "test",
        "injection_payload": "DANGEROUS_PAYLOAD",
        "target_action": TargetAction(tool="test_tool", injected_parameters={}),
        "success_criteria": [],
        "safe_behavior": "test",
        "expected_safe_tool_sequence": []
    }

def test_workspace_reset(base_scenario_data):
    ws = WorkspaceSimulator()
    ws.inbox.append({"test": "data"})
    ws.reset()
    assert len(ws.inbox) == 0

def test_workspace_inject_email(base_scenario_data):
    data = base_scenario_data.copy()
    data["vector"] = "email"
    scenario = Scenario(**data)
    
    ws = WorkspaceSimulator()
    ws.inject_scenario(scenario)
    ctx = ws.get_context()
    
    assert len(ctx["inbox"]) == 1
    assert "DANGEROUS_PAYLOAD" in ctx["inbox"][0]["body"]

def test_workspace_inject_skill(base_scenario_data):
    data = base_scenario_data.copy()
    data["vector"] = "skill"
    scenario = Scenario(**data)
    
    ws = WorkspaceSimulator()
    ws.inject_scenario(scenario)
    ctx = ws.get_context()
    
    assert "test_tool" in ctx["tool_descriptions"]
    assert "DANGEROUS_PAYLOAD" in ctx["tool_descriptions"]["test_tool"]
