from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TargetAction(BaseModel):
    tool: str
    injected_parameters: Dict[str, Any]

class SuccessCriteriaMatch(BaseModel):
    tool_called: Optional[str] = None
    parameter_match: Optional[Dict[str, Any]] = None

class Scenario(BaseModel):
    id: str
    name: str
    vector: str
    harm_domain: str
    description: str
    legitimate_task: str
    injection_payload: str
    target_action: TargetAction
    success_criteria: List[SuccessCriteriaMatch]
    safe_behavior: str
    expected_safe_tool_sequence: List[str]
