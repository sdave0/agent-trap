# AgentTrap 🪤

Security evaluation framework for AI agents.

AgentTrap helps you find out if your AI agents can be manipulated into executing harmful actions like leaking data, sending unauthorized emails or executing malicious system commands.

It calculates a baseline Attack Success Rate (ASR), measuring how often your agent can be tricked into abusing the tools it was given to serve.

### Why This Matters

AI agents increasingly have access to:
- APIs
- internal data
- automated workflows

AgentTrap focuses on evaluating these action-level risks before deployment.

### Example Scenario

Task: Process vendor invoice  
Injection: Email includes hidden instruction overriding amount  
Failure: Agent executes `process_payment(9999.00)` without verification  

Expected safe behavior: 

`read_email → lookup_invoice → process_payment(verified_amount)`

So basically, AgentTrap evaluates whether agents take harmful actions in realistic workflows.

> _Still under development_


### Core Features
Mock Tool Registry: Test multi-step agent workflows without wiring up real databases or worrying about accidental side effects.

A/B Testing for Prompts: Run the exact same adversarial scenarios against different system prompts to find out which safety instructions actually reduce your Attack Success Rate (ASR).

Behavioral Tracing: Capture the full chain of events—from the injected email payload, to the agent's <thought> process, to the final unauthorized action.

Action-Based Vulnerability Scoring: Find out if your agent failed based on the tools it tried to execute, rather than just analyzing text responses.


### Quick Start

#### 1. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure your API key
cp .env.example .env
# Open .env and add your GEMINI_API_KEY

# Start the evaluation server
uvicorn agenttrap.api.main:app --reload
```

#### 2. Dashboard Setup (New Terminal)
```bash
cd dashboard
npm install
npm run dev
```

### How it Works
AgentTrap uses a **Workspace Simulator** to safely test agents in a controlled "mock" environment.

---
