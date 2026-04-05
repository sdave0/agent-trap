import os
import yaml
from typing import List, Dict

from agenttrap.models.scenario import Scenario

class ScenarioRegistry:
    def __init__(self, scenarios_dir: str = "scenarios"):
        self.scenarios_dir = scenarios_dir
        self.scenarios: Dict[str, Scenario] = {}

    def load_all(self) -> List[Scenario]:
        """Loads all YAML scenarios from the scenarios directory."""
        if not os.path.exists(self.scenarios_dir):
            raise FileNotFoundError(f"Scenarios directory not found: {self.scenarios_dir}")

        self.scenarios = {}
        for filename in os.listdir(self.scenarios_dir):
            if filename.endswith((".yaml", ".yml")):
                filepath = os.path.join(self.scenarios_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if not data:
                            continue
                        scenario = Scenario(**data)
                        self.scenarios[scenario.id] = scenario
                except Exception as e:
                    # In a real app we might log, but here we intentionally raise or record errors
                    raise ValueError(f"Failed to load scenario {filename}: {e}")
        
        return list(self.scenarios.values())

    def get_scenario(self, scenario_id: str) -> Scenario:
        return self.scenarios.get(scenario_id)
