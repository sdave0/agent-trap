import pytest
import yaml
from agenttrap.registry.loader import ScenarioRegistry
import os

def test_registry_loading(tmp_path):
    # Create valid scenario
    valid_scenario = {
        "id": "TEST-01",
        "name": "Test",
        "vector": "skill",
        "harm_domain": "financial",
        "description": "desc",
        "legitimate_task": "task",
        "injection_payload": "payload",
        "target_action": {"tool": "test", "injected_parameters": {"a": 1}},
        "success_criteria": [{"tool_called": "test"}],
        "safe_behavior": "safe",
        "expected_safe_tool_sequence": ["read"]
    }
    
    with open(tmp_path / "valid.yaml", "w") as f:
        yaml.dump(valid_scenario, f)
        
    registry = ScenarioRegistry(scenarios_dir=str(tmp_path))
    scenarios = registry.load_all()
    assert len(scenarios) == 1
    assert scenarios[0].id == "TEST-01"

def test_registry_invalid_loading(tmp_path):
    # Create invalid scenario (missing fields)
    invalid_scenario = {"id": "BAD-01"}
    
    with open(tmp_path / "invalid.yaml", "w") as f:
        yaml.dump(invalid_scenario, f)
        
    registry = ScenarioRegistry(scenarios_dir=str(tmp_path))
    with pytest.raises(ValueError):
        registry.load_all()
