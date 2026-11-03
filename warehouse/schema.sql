-- CLARA Database Schema Definition for DuckDB

CREATE TABLE IF NOT EXISTS cloud_instances (
    instance_id VARCHAR PRIMARY KEY,
    cloud_provider VARCHAR,
    instance_type VARCHAR,
    region VARCHAR,
    cpu_cores INTEGER,
    memory_gb INTEGER,
    launch_date DATE,
    status VARCHAR,
    hourly_rate_usd DOUBLE
);

CREATE TABLE IF NOT EXISTS security_configurations (
    instance_id VARCHAR,
    open_ports VARCHAR,
    internet_exposed BOOLEAN,
    encryption_enabled BOOLEAN,
    iam_permission_level VARCHAR,
    failed_logins_7d INTEGER,
    last_patch_date DATE,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id)
);

CREATE TABLE IF NOT EXISTS metrics_daily (
    instance_id VARCHAR,
    date DATE,
    cpu_utilization_pct DOUBLE,
    memory_utilization_pct DOUBLE,
    network_in_mb DOUBLE,
    network_out_mb DOUBLE,
    disk_read_iops INTEGER,
    disk_write_iops INTEGER,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id)
);

CREATE TABLE IF NOT EXISTS cost_data (
    instance_id VARCHAR,
    date DATE,
    hourly_cost_usd DOUBLE,
    daily_cost_usd DOUBLE,
    utilization_pct DOUBLE,
    waste_score DOUBLE,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id)
);

CREATE TABLE IF NOT EXISTS security_events (
    event_id VARCHAR PRIMARY KEY,
    instance_id VARCHAR,
    event_type VARCHAR,
    severity VARCHAR,
    description VARCHAR,
    timestamp TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id)
);

CREATE TABLE IF NOT EXISTS risk_scores (
    score_id VARCHAR PRIMARY KEY,
    instance_id VARCHAR,
    anomaly_score DOUBLE,
    security_risk_score DOUBLE,
    cost_waste_score DOUBLE,
    overall_risk_score DOUBLE,
    model_version VARCHAR,
    calculated_at TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id VARCHAR,
    instance_id VARCHAR,
    risk_type VARCHAR,
    priority VARCHAR,
    title VARCHAR,
    description VARCHAR,
    implementation_steps VARCHAR,
    estimated_savings_usd DOUBLE,
    estimated_effort_hours DOUBLE,
    status VARCHAR DEFAULT 'pending',
    generated_at TIMESTAMP,
    generation_source VARCHAR DEFAULT 'legacy_unknown',
    model_name VARCHAR DEFAULT 'unknown',
    fallback_reason VARCHAR DEFAULT 'pre_migration_record',
    expected_benefit VARCHAR,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id)
);

-- Indexes for query optimization
CREATE INDEX IF NOT EXISTS idx_metrics_daily ON metrics_daily(instance_id, date);
CREATE INDEX IF NOT EXISTS idx_cost_data ON cost_data(instance_id, date);
CREATE INDEX IF NOT EXISTS idx_risk_scores ON risk_scores(instance_id);
CREATE INDEX IF NOT EXISTS idx_recommendations ON recommendations(instance_id, status);
CREATE INDEX IF NOT EXISTS idx_recommendations_id ON recommendations(recommendation_id);
