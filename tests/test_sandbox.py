import pytest
from agenttrap.sandbox.executor import ToolExecutor

def test_executor_valid_tool():
    executor = ToolExecutor()
    result = executor.execute("process_payment", {"amount": 100.0, "recipient": "Test"})
    assert result["status"] == "success"
    assert result["amount"] == 100.0

def test_executor_invalid_tool():
    executor = ToolExecutor()
    result = executor.execute("non_existent_tool", {})
    assert result["status"] == "error"

def test_executor_parameter_mismatch():
    executor = ToolExecutor()
    result = executor.execute("process_payment", {"wrong_param": "Test"})
    assert result["status"] == "error"
    assert "Parameter error" in result["message"]
