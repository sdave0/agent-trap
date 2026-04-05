import sys
import logging
from agenttrap.registry.loader import ScenarioRegistry

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def validate_scenarios():
    setup_logging()
    registry = ScenarioRegistry()
    try:
        scenarios = registry.load_all()
        logging.info(f"Successfully loaded and validated {len(scenarios)} scenarios.")
        if len(scenarios) != 20:
            logging.warning(f"Expected 20 scenarios, found {len(scenarios)}.")
        else:
            logging.info("Milestone Check passed: All 20 YAML scenarios loaded flawlessly.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate-scenarios":
        validate_scenarios()
    else:
        print("Usage: python -m agenttrap validate-scenarios")
