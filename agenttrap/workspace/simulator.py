from typing import Dict, Any, List
from agenttrap.models.scenario import Scenario

class WorkspaceSimulator:
    """
    Simulates the agent's environment, injecting the adversarial payload
    into the correct vector based on the scenario configuration.
    """

    def __init__(self):
        self.reset()
        
    def reset(self):
        """Wipes the state clean between lifecycles."""
        self.inbox: List[Dict[str, str]] = []
        self.web_content: str = "Default web content"
        self.tool_descriptions: Dict[str, str] = {}
        
    def inject_scenario(self, scenario: Scenario):
        """
        Embeds the scenario payload into the appropriate communication channel.
        """
        self.reset()
        
        vector = scenario.vector.lower()
        payload = scenario.injection_payload
        
        if vector == "email":
            self.inbox.append({
                "from": "trusted_sender@domain.com",
                "subject": "Relevant Task Update",
                "body": f"Please process the attached context. \n\n{payload}"
            })
            
        elif vector == "web":
            self.web_content = f"<h1>Information Page</h1>\n<p>General page data.</p>\n<hidden>{payload}</hidden>"
            
        elif vector == "skill":
            target_tool = scenario.target_action.tool
            self.tool_descriptions[target_tool] = f"[Injected Instruction: {payload}]"
            
    def get_context(self) -> Dict[str, Any]:
        return {
            "inbox": self.inbox,
            "web_content": self.web_content,
            "tool_descriptions": self.tool_descriptions
        }
