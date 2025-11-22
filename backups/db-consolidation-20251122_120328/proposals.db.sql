PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE orchestration_tasks (
	id INTEGER NOT NULL, 
	task_id VARCHAR(255) NOT NULL, 
	task_type VARCHAR(100) NOT NULL, 
	description TEXT, 
	priority FLOAT NOT NULL, 
	status VARCHAR(50) NOT NULL, 
	allocated_agent_id VARCHAR(255), 
	created_at DATETIME NOT NULL, 
	started_at DATETIME, 
	completed_at DATETIME, 
	result TEXT, 
	error_message TEXT, 
	retry_count INTEGER NOT NULL, 
	max_retries INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE agent_allocations (
	id INTEGER NOT NULL, 
	agent_id VARCHAR(255) NOT NULL, 
	task_id VARCHAR(255) NOT NULL, 
	allocated_at DATETIME NOT NULL, 
	released_at DATETIME, 
	status VARCHAR(50) NOT NULL, 
	capability_score FLOAT, 
	cost_score FLOAT, 
	performance_score FLOAT, 
	workload_score FLOAT, 
	final_score FLOAT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_agent_task_active UNIQUE (agent_id, task_id, status)
);
CREATE TABLE agent_performance (
	id INTEGER NOT NULL, 
	agent_id VARCHAR(255) NOT NULL, 
	total_tasks INTEGER NOT NULL, 
	successful_tasks INTEGER NOT NULL, 
	failed_tasks INTEGER NOT NULL, 
	success_rate FLOAT NOT NULL, 
	average_duration FLOAT NOT NULL, 
	task_type_stats TEXT, 
	last_updated DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE agent_workload (
	agent_id VARCHAR(255) NOT NULL, 
	workload INTEGER NOT NULL, 
	updated_at FLOAT NOT NULL, 
	PRIMARY KEY (agent_id)
);
CREATE TABLE agent_history (
	agent_id VARCHAR(255) NOT NULL, 
	successes INTEGER NOT NULL, 
	failures INTEGER NOT NULL, 
	attempts INTEGER NOT NULL, 
	updated_at FLOAT NOT NULL, 
	PRIMARY KEY (agent_id)
);
CREATE TABLE task_type_history (
	capability VARCHAR(255) NOT NULL, 
	agent_id VARCHAR(255) NOT NULL, 
	success_rate FLOAT NOT NULL, 
	updated_at FLOAT NOT NULL, 
	PRIMARY KEY (capability, agent_id)
);
CREATE TABLE preflight_checks (
	id INTEGER NOT NULL, 
	session_id VARCHAR(255) NOT NULL, 
	task_id VARCHAR(255), 
	check_type VARCHAR(100) NOT NULL, 
	passed BOOLEAN NOT NULL, 
	details TEXT, 
	error_message TEXT, 
	checked_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE task_history (
	id INTEGER NOT NULL, 
	task_type VARCHAR(255), 
	capability_required VARCHAR(255), 
	complexity VARCHAR(100), 
	tokens_used INTEGER, 
	estimated_tokens INTEGER, 
	agent_id VARCHAR(255), 
	timestamp FLOAT NOT NULL, 
	metadata TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE orchestration_decisions (
	id VARCHAR(255) NOT NULL, 
	timestamp FLOAT NOT NULL, 
	task_id VARCHAR(255) NOT NULL, 
	agent_id VARCHAR(255), 
	task_type VARCHAR(255), 
	success INTEGER, 
	failure_reason TEXT, 
	tokens_used INTEGER, 
	duration_seconds FLOAT, 
	dry_run INTEGER NOT NULL, 
	decision_process TEXT, 
	metadata TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE proposals (
	id VARCHAR(255) NOT NULL, 
	hypothesis TEXT NOT NULL, 
	rationale TEXT NOT NULL, 
	pattern_id VARCHAR(255), 
	performance_data TEXT, 
	implementation_result TEXT, 
	metadata TEXT, 
	status VARCHAR(50) NOT NULL, 
	created_at FLOAT NOT NULL, 
	reviewed_at FLOAT, 
	implemented_at FLOAT, 
	review_notes TEXT, 
	PRIMARY KEY (id)
);
INSERT INTO proposals VALUES('286ae236-f28c-4467-991c-5afeac8529c5','Route security queries to claude for better results','claude has shown 90.0% average confidence for security queries across 5 sessions','agent_specialization_claude_security','{"period_days": 7, "total_sessions": 5, "avg_confidence": 90.0, "agent_usage": {"claude": 5}, "agent_avg_confidence": {"claude": 90.0}, "skill_usage": {"security-review": 5}, "decisions": [{"session_id": "session-004", "query": "security query 4", "skill": "security-review", "confidence": 90.0, "agents": ["claude"], "timestamp": "2025-11-19T09:08:46.868239+00:00"}, {"session_id": "session-003", "query": "security query 3", "skill": "security-review", "confidence": 90.0, "agents": ["claude"], "timestamp": "2025-11-19T09:08:46.868037+00:00"}, {"session_id": "session-002", "query": "security query 2", "skill": "security-review", "confidence": 90.0, "agents": ["claude"], "timestamp": "2025-11-19T09:08:46.867863+00:00"}, {"session_id": "session-001", "query": "security query 1", "skill": "security-review", "confidence": 90.0, "agents": ["claude"], "timestamp": "2025-11-19T09:08:46.867660+00:00"}, {"session_id": "session-000", "query": "security query 0", "skill": "security-review", "confidence": 90.0, "agents": ["claude"], "timestamp": "2025-11-19T09:08:46.867440+00:00"}], "metrics": {"avg_confidence": 90.0, "total_sessions": 5, "unique_skills": 1, "unique_agents": 1}}',NULL,'{"agent": "claude", "query_type": "security", "suggested_weight": 1.15}','pending',1763543326.879959106,NULL,NULL,NULL);
CREATE TABLE learning_proposals (
	id INTEGER NOT NULL, 
	proposal_id VARCHAR(255) NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT NOT NULL, 
	pattern_detected TEXT NOT NULL, 
	proposed_changes TEXT NOT NULL, 
	confidence FLOAT NOT NULL, 
	impact_estimate VARCHAR(50), 
	status VARCHAR(50) NOT NULL, 
	reviewed_by VARCHAR(255), 
	reviewed_at DATETIME, 
	review_notes TEXT, 
	applied_at DATETIME, 
	application_result TEXT, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE task_completions (
	id VARCHAR(255) NOT NULL, 
	task_id VARCHAR(255) NOT NULL, 
	task_title VARCHAR(500), 
	status VARCHAR(100) NOT NULL, 
	agent_id VARCHAR(255), 
	completed_at FLOAT NOT NULL, 
	created_at FLOAT NOT NULL, 
	duration_seconds FLOAT, 
	tokens_used INTEGER, 
	success INTEGER NOT NULL, 
	failure_reason TEXT, 
	output_file_path VARCHAR(500), 
	markdown_file_path VARCHAR(500), 
	metadata TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE voting_sessions (
	id VARCHAR(255) NOT NULL, 
	vote_type VARCHAR(100) NOT NULL, 
	timestamp FLOAT NOT NULL, 
	winner VARCHAR(255), 
	consensus_score FLOAT NOT NULL, 
	total_votes INTEGER NOT NULL, 
	voter_ids TEXT NOT NULL, 
	candidates TEXT NOT NULL, 
	similarity_history TEXT, 
	metadata TEXT, 
	convergence_state VARCHAR(100), 
	convergence_score FLOAT, 
	rounds_completed INTEGER NOT NULL, 
	termination_reason VARCHAR(255), 
	context TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE model_detections (
	id INTEGER NOT NULL, 
	model_id VARCHAR(255) NOT NULL, 
	context_length INTEGER, 
	api_base_url VARCHAR(500), 
	detected_at FLOAT NOT NULL, 
	model_info TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_model_api UNIQUE (model_id, api_base_url)
);
CREATE TABLE model_configurations (
	id INTEGER NOT NULL, 
	model_id VARCHAR(255) NOT NULL, 
	temperature FLOAT, 
	max_tokens INTEGER, 
	top_p FLOAT, 
	frequency_penalty FLOAT, 
	presence_penalty FLOAT, 
	success_rate FLOAT, 
	avg_response_time FLOAT, 
	total_uses INTEGER NOT NULL, 
	successful_uses INTEGER NOT NULL, 
	created_at FLOAT NOT NULL, 
	updated_at FLOAT NOT NULL, 
	metadata TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_model_config UNIQUE (model_id, temperature, max_tokens)
);
CREATE TABLE vote_records (
	id INTEGER NOT NULL, 
	vote_id VARCHAR(255) NOT NULL, 
	task_id VARCHAR(255), 
	question TEXT NOT NULL, 
	voters TEXT NOT NULL, 
	consensus VARCHAR(255), 
	confidence FLOAT, 
	votes TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	completed_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE tasks (
	id VARCHAR(255) NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	status VARCHAR(100) NOT NULL, 
	priority VARCHAR(50) NOT NULL, 
	capability_required VARCHAR(255), 
	estimated_tokens INTEGER, 
	tags TEXT, 
	dependencies TEXT, 
	failures TEXT, 
	metadata TEXT, 
	file VARCHAR(500), 
	created_by VARCHAR(255), 
	created_at VARCHAR(100), 
	updated_at VARCHAR(100), 
	version INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE task_queue_metadata (
	"key" VARCHAR(255) NOT NULL, 
	value TEXT NOT NULL, 
	updated_at VARCHAR(100) NOT NULL, 
	PRIMARY KEY ("key")
);
CREATE TABLE review_sessions (
	id VARCHAR(255) NOT NULL, 
	timestamp FLOAT NOT NULL, 
	scope VARCHAR(100) NOT NULL, 
	reviewers TEXT, 
	files_reviewed TEXT, 
	total_issues INTEGER NOT NULL, 
	consensus_issues INTEGER NOT NULL, 
	unique_issues INTEGER NOT NULL, 
	metadata TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE task_executions (
	id INTEGER NOT NULL, 
	task_id INTEGER NOT NULL, 
	agent_id VARCHAR(255) NOT NULL, 
	attempt_number INTEGER NOT NULL, 
	started_at DATETIME NOT NULL, 
	completed_at DATETIME, 
	duration_seconds FLOAT, 
	success BOOLEAN NOT NULL, 
	result TEXT, 
	error_message TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(task_id) REFERENCES orchestration_tasks (id)
);
CREATE TABLE decision_edges (
	id INTEGER NOT NULL, 
	from_session_id VARCHAR(255) NOT NULL, 
	to_session_id VARCHAR(255) NOT NULL, 
	relationship_type VARCHAR(100) NOT NULL, 
	strength FLOAT NOT NULL, 
	created_at FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(from_session_id) REFERENCES voting_sessions (id), 
	FOREIGN KEY(to_session_id) REFERENCES voting_sessions (id)
);
CREATE TABLE configuration_performance (
	id INTEGER NOT NULL, 
	config_id INTEGER NOT NULL, 
	model_id VARCHAR(255) NOT NULL, 
	task_type VARCHAR(255), 
	success BOOLEAN, 
	response_time FLOAT, 
	tokens_used INTEGER, 
	error_type VARCHAR(255), 
	recorded_at FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(config_id) REFERENCES model_configurations (id)
);
CREATE TABLE review_issues (
	id VARCHAR(255) NOT NULL, 
	session_id VARCHAR(255) NOT NULL, 
	reviewer_id VARCHAR(255), 
	scope VARCHAR(100) NOT NULL, 
	severity VARCHAR(50) NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	file_path VARCHAR(500), 
	line_number INTEGER, 
	suggested_fix TEXT, 
	estimated_effort VARCHAR(100), 
	is_consensus INTEGER NOT NULL, 
	created_at FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES review_sessions (id)
);
CREATE TABLE ai_reviews (
	id VARCHAR(255) NOT NULL, 
	session_id VARCHAR(255) NOT NULL, 
	reviewer_id VARCHAR(255) NOT NULL, 
	scope VARCHAR(100) NOT NULL, 
	summary TEXT, 
	overall_assessment TEXT, 
	confidence FLOAT NOT NULL, 
	timestamp FLOAT NOT NULL, 
	raw_response TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES review_sessions (id)
);
CREATE INDEX ix_tasks_status_priority ON orchestration_tasks (status, priority);
CREATE UNIQUE INDEX ix_orchestration_tasks_task_id ON orchestration_tasks (task_id);
CREATE INDEX ix_orchestration_tasks_task_type ON orchestration_tasks (task_type);
CREATE INDEX ix_tasks_status_created ON orchestration_tasks (status, created_at);
CREATE INDEX ix_orchestration_tasks_status ON orchestration_tasks (status);
CREATE INDEX ix_orchestration_tasks_allocated_agent_id ON orchestration_tasks (allocated_agent_id);
CREATE INDEX ix_agent_allocations_task_id ON agent_allocations (task_id);
CREATE INDEX ix_agent_allocations_agent_id ON agent_allocations (agent_id);
CREATE INDEX ix_allocations_agent_status ON agent_allocations (agent_id, status);
CREATE UNIQUE INDEX ix_agent_performance_agent_id ON agent_performance (agent_id);
CREATE INDEX ix_preflight_checks_session_id ON preflight_checks (session_id);
CREATE INDEX ix_preflight_session_time ON preflight_checks (session_id, checked_at);
CREATE INDEX ix_preflight_checks_task_id ON preflight_checks (task_id);
CREATE INDEX ix_task_history_task_type ON task_history (task_type);
CREATE INDEX ix_task_history_capability_required ON task_history (capability_required);
CREATE INDEX ix_orchestration_decisions_task_id ON orchestration_decisions (task_id);
CREATE INDEX ix_orchestration_decisions_success ON orchestration_decisions (success);
CREATE INDEX idx_decisions_agent_id ON orchestration_decisions (agent_id);
CREATE INDEX idx_decisions_success ON orchestration_decisions (success);
CREATE INDEX ix_orchestration_decisions_timestamp ON orchestration_decisions (timestamp);
CREATE INDEX ix_orchestration_decisions_agent_id ON orchestration_decisions (agent_id);
CREATE INDEX ix_orchestration_decisions_dry_run ON orchestration_decisions (dry_run);
CREATE INDEX idx_decisions_task_id ON orchestration_decisions (task_id);
CREATE INDEX idx_decisions_dry_run ON orchestration_decisions (dry_run);
CREATE INDEX ix_orchestration_decisions_task_type ON orchestration_decisions (task_type);
CREATE INDEX idx_decisions_task_type ON orchestration_decisions (task_type);
CREATE INDEX idx_decisions_timestamp ON orchestration_decisions (timestamp);
CREATE INDEX idx_proposals_pattern ON proposals (pattern_id);
CREATE INDEX idx_proposals_status ON proposals (status);
CREATE INDEX ix_proposals_created_at ON proposals (created_at);
CREATE INDEX idx_proposals_created ON proposals (created_at);
CREATE INDEX ix_proposals_pattern_id ON proposals (pattern_id);
CREATE INDEX ix_proposals_status ON proposals (status);
CREATE UNIQUE INDEX ix_learning_proposals_proposal_id ON learning_proposals (proposal_id);
CREATE INDEX ix_learning_proposals_status ON learning_proposals (status);
CREATE INDEX ix_task_completions_status ON task_completions (status);
CREATE INDEX ix_task_completions_completed_at ON task_completions (completed_at);
CREATE INDEX ix_task_completions_task_id ON task_completions (task_id);
CREATE INDEX ix_voting_sessions_timestamp ON voting_sessions (timestamp);
CREATE INDEX ix_voting_sessions_vote_type ON voting_sessions (vote_type);
CREATE INDEX ix_model_detections_model_id ON model_detections (model_id);
CREATE INDEX ix_model_detections_api_base_url ON model_detections (api_base_url);
CREATE INDEX ix_model_configurations_model_id ON model_configurations (model_id);
CREATE UNIQUE INDEX ix_vote_records_vote_id ON vote_records (vote_id);
CREATE INDEX ix_vote_records_task_id ON vote_records (task_id);
CREATE INDEX ix_tasks_priority ON tasks (priority);
CREATE INDEX ix_tasks_capability_required ON tasks (capability_required);
CREATE INDEX idx_tasks_tags ON tasks (tags);
CREATE INDEX ix_tasks_status ON tasks (status);
CREATE INDEX ix_tasks_updated_at ON tasks (updated_at);
CREATE INDEX ix_review_sessions_scope ON review_sessions (scope);
CREATE INDEX ix_review_sessions_timestamp ON review_sessions (timestamp);
CREATE INDEX ix_task_executions_task_id ON task_executions (task_id);
CREATE INDEX ix_decision_edges_to_session_id ON decision_edges (to_session_id);
CREATE INDEX ix_decision_edges_from_session_id ON decision_edges (from_session_id);
CREATE INDEX ix_configuration_performance_model_id ON configuration_performance (model_id);
CREATE INDEX ix_configuration_performance_config_id ON configuration_performance (config_id);
CREATE INDEX idx_issues_consensus ON review_issues (is_consensus);
CREATE INDEX ix_review_issues_session_id ON review_issues (session_id);
CREATE INDEX ix_review_issues_severity ON review_issues (severity);
CREATE INDEX ix_review_issues_is_consensus ON review_issues (is_consensus);
CREATE INDEX ix_review_issues_scope ON review_issues (scope);
CREATE INDEX ix_review_issues_file_path ON review_issues (file_path);
CREATE INDEX ix_ai_reviews_session_id ON ai_reviews (session_id);
CREATE INDEX ix_ai_reviews_reviewer_id ON ai_reviews (reviewer_id);
COMMIT;
