import pytest
from agenttrap.agent.prompts import get_system_prompt
from agenttrap.agent.schemas import get_tools_schema

def test_prompt_baseline():
    prompt = get_system_prompt("baseline", "CTX", "TASK")
    assert "CTX" in prompt
    assert "TASK" in prompt
    assert "SECURITY REQUIREMENTS" not in prompt

def test_prompt_instructed():
    prompt = get_system_prompt("instructed", "CTX", "TASK")
    assert "CTX" in prompt
    assert "TASK" in prompt
    assert "SECURITY REQUIREMENTS" in prompt

def test_schema_poisoning():
    # Base config
    schema_base = get_tools_schema()
    for tool in schema_base:
        if tool["function"]["name"] == "process_payment":
            assert "\n\n" not in tool["function"]["description"]

    # Poisoned config
    poisoned = {"process_payment": "INJECTED_CMD"}
    schema_poisoned = get_tools_schema(poisoned)
    for tool in schema_poisoned:
        if tool["function"]["name"] == "process_payment":
            assert "INJECTED_CMD" in tool["function"]["description"]
