import pytest
import uuid
import json
from agenttrap.db.client import DBClient
from agenttrap.engine.tracer import ActionTracer
from agenttrap.engine.classifier import OutcomeClassifier
from agenttrap.models.scenario import Scenario, TargetAction, SuccessCriteriaMatch

@pytest.fixture
def mock_scenario():
    return Scenario(
        id="SI-01",
        name="test",
        vector="skill",
        harm_domain="financial",
        description="test",
        legitimate_task="test",
        injection_payload="test",
        target_action=TargetAction(tool="process_payment", injected_parameters={"amount": 999}),
        success_criteria=[SuccessCriteriaMatch(tool_called="process_payment", parameter_match={"amount": 999})],
        safe_behavior="test",
        expected_safe_tool_sequence=[]
    )

def test_classifier_accuracy(tmp_path, mock_scenario):
    db = DBClient(str(tmp_path / "test.db"))
    
    run_id = str(uuid.uuid4())
    result_id = str(uuid.uuid4())
    with db.get_connection() as conn:
        conn.execute("INSERT INTO runs (id, name, created_at, agent_config, model, total_scenarios) VALUES (?, 'test', 'now', 'base', 'm', 1)", (run_id,))
        conn.execute("INSERT INTO scenario_results (id, run_id, scenario_id, vector, harm_domain, outcome, steps_taken, attack_succeeded, created_at) VALUES (?, ?, 'SI-01', 'skill', 'val', 'incomplete', 0, 0, 'now')", (result_id, run_id))
        conn.commit()
        
    tracer = ActionTracer(db)
    tracer.start_trace(result_id)
    
    # Safe action
    tracer.log_action("process_payment", {"amount": 10}, "safe reason")
    
    classifier = OutcomeClassifier(db)
    res = classifier.classify_outcome(run_id, mock_scenario, tracer.get_traces())
    assert res["outcome"] == "attack_failed"
    assert res["attack_success"] is False

def test_classifier_accuracy_success(tmp_path, mock_scenario):
    db = DBClient(str(tmp_path / "test.db"))
    
    run_id = str(uuid.uuid4())
    result_id = str(uuid.uuid4())
    with db.get_connection() as conn:
        conn.execute("INSERT INTO runs (id, name, created_at, agent_config, model, total_scenarios) VALUES (?, 'test', 'now', 'base', 'm', 1)", (run_id,))
        conn.execute("INSERT INTO scenario_results (id, run_id, scenario_id, vector, harm_domain, outcome, steps_taken, attack_succeeded, created_at) VALUES (?, ?, 'SI-01', 'skill', 'val', 'incomplete', 0, 0, 'now')", (result_id, run_id))
        conn.commit()
        
    tracer = ActionTracer(db)
    tracer.start_trace(result_id)
    
    # Poisoned action
    tracer.log_action("process_payment", {"amount": 999}, "injected reason")
    
    classifier = OutcomeClassifier(db)
    res = classifier.classify_outcome(run_id, mock_scenario, tracer.get_traces())
    assert res["outcome"] == "attack_success"
    assert res["attack_success"] is True
