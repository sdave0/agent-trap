"""
AgentTrap Database Schema
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS runs (
    id          TEXT PRIMARY KEY,  -- UUID
    name        TEXT NOT NULL,
    created_at  TEXT NOT NULL,     -- ISO 8601
    agent_config TEXT NOT NULL,    -- baseline | instructed
    model       TEXT NOT NULL,     -- e.g. gemini/gemini-3-flash-preview
    status      TEXT DEFAULT 'pending',
    total_scenarios INT NOT NULL,
    completed_scenarios INT DEFAULT 0,
    asr_overall REAL,              -- populated after completion
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS scenario_results (
    id              TEXT PRIMARY KEY,
    run_id          TEXT REFERENCES runs(id),
    scenario_id     TEXT NOT NULL,   -- e.g. EM-02
    vector          TEXT NOT NULL,   -- skill | email | web
    harm_domain     TEXT NOT NULL,
    outcome         TEXT NOT NULL,   -- attack_success | attack_failed | incomplete
    failure_mode    TEXT,            -- what kind of failure (if attack_success)
    steps_taken     INT NOT NULL,
    attack_succeeded BOOLEAN NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS action_traces (
    id              TEXT PRIMARY KEY,
    scenario_result_id TEXT REFERENCES scenario_results(id),
    step_index      INT NOT NULL,
    tool_name       TEXT NOT NULL,
    parameters      TEXT NOT NULL,   -- JSON string
    reasoning       TEXT,            -- agent's reasoning for this call
    verdict         TEXT NOT NULL,   -- intended | injected
    timestamp       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_scenario_results_run ON scenario_results(run_id);
CREATE INDEX IF NOT EXISTS idx_action_traces_result ON action_traces(scenario_result_id);
CREATE INDEX IF NOT EXISTS idx_scenario_results_outcome ON scenario_results(run_id, outcome);
"""
