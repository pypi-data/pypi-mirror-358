-- PostgreSQL Database Schema for NoLink Connector
-- This schema supports millions of users with proper indexing and partitioning

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User connections table (main table for tracking active connections)
CREATE TABLE user_connections (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    connection_token VARCHAR(255) UNIQUE NOT NULL,
    socket_port INTEGER NOT NULL,
    hostname VARCHAR(255),
    platform VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'expired', 'error')),
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    metadata JSONB DEFAULT '{}',
    
    -- Indexes for performance
    CONSTRAINT uk_api_key UNIQUE (api_key),
    CONSTRAINT uk_connection_token UNIQUE (connection_token)
);

-- Indexes for user_connections
CREATE INDEX idx_user_connections_user_id ON user_connections(user_id);
CREATE INDEX idx_user_connections_status_heartbeat ON user_connections(status, last_heartbeat);
CREATE INDEX idx_user_connections_expires_at ON user_connections(expires_at);
CREATE INDEX idx_user_connections_created_at ON user_connections(created_at);
CREATE INDEX idx_user_connections_port ON user_connections(socket_port);

-- Active terminal sessions table
CREATE TABLE terminal_sessions (
    id SERIAL PRIMARY KEY,
    connection_id INTEGER REFERENCES user_connections(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    socket_id VARCHAR(255),
    working_directory VARCHAR(1000),
    shell_type VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    session_data JSONB DEFAULT '{}',
    
    CONSTRAINT uk_session_id UNIQUE (session_id)
);

-- Indexes for terminal_sessions
CREATE INDEX idx_terminal_sessions_connection_id ON terminal_sessions(connection_id);
CREATE INDEX idx_terminal_sessions_socket_id ON terminal_sessions(socket_id);
CREATE INDEX idx_terminal_sessions_active_activity ON terminal_sessions(is_active, last_activity);
CREATE INDEX idx_terminal_sessions_created_at ON terminal_sessions(created_at);

-- Command execution log (partitioned by date for performance)
CREATE TABLE command_executions (
    id BIGSERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES terminal_sessions(id) ON DELETE SET NULL,
    connection_id INTEGER REFERENCES user_connections(id) ON DELETE SET NULL,
    command_text TEXT NOT NULL,
    command_hash VARCHAR(64), -- SHA256 hash for duplicate detection
    output_preview TEXT, -- First 1000 chars of output
    output_size INTEGER DEFAULT 0,
    exit_code INTEGER,
    execution_time_ms INTEGER,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255),
    
    -- Constraint to prevent extremely long commands
    CONSTRAINT chk_command_length CHECK (LENGTH(command_text) <= 10000)
) PARTITION BY RANGE (executed_at);

-- Create partitions for command_executions (example for current month)
CREATE TABLE command_executions_2024_12 PARTITION OF command_executions
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

CREATE TABLE command_executions_2025_01 PARTITION OF command_executions
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Indexes for command_executions
CREATE INDEX idx_command_executions_session_id ON command_executions(session_id, executed_at);
CREATE INDEX idx_command_executions_connection_id ON command_executions(connection_id, executed_at);
CREATE INDEX idx_command_executions_user_id ON command_executions(user_id, executed_at);
CREATE INDEX idx_command_executions_command_hash ON command_executions(command_hash);
CREATE INDEX idx_command_executions_executed_at ON command_executions(executed_at);

-- Connection statistics table (for analytics)
CREATE TABLE connection_stats (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    connection_id INTEGER REFERENCES user_connections(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    total_commands INTEGER DEFAULT 0,
    total_execution_time_ms BIGINT DEFAULT 0,
    successful_commands INTEGER DEFAULT 0,
    failed_commands INTEGER DEFAULT 0,
    session_duration_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_connection_stats_daily UNIQUE (connection_id, date)
);

-- Indexes for connection_stats
CREATE INDEX idx_connection_stats_user_id_date ON connection_stats(user_id, date);
CREATE INDEX idx_connection_stats_date ON connection_stats(date);

-- Security events table (for audit logging)
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    connection_id INTEGER REFERENCES user_connections(id) ON DELETE SET NULL,
    user_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL, -- 'blocked_command', 'invalid_token', 'path_violation', etc.
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    command_attempted TEXT,
    client_ip INET,
    user_agent TEXT,
    additional_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for security_events
CREATE INDEX idx_security_events_connection_id ON security_events(connection_id, created_at);
CREATE INDEX idx_security_events_user_id ON security_events(user_id, created_at);
CREATE INDEX idx_security_events_type_severity ON security_events(event_type, severity, created_at);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);

-- System metrics table (for monitoring server health)
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (recorded_at);

-- Create partitions for system_metrics
CREATE TABLE system_metrics_2024_12 PARTITION OF system_metrics
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

CREATE TABLE system_metrics_2025_01 PARTITION OF system_metrics
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Indexes for system_metrics
CREATE INDEX idx_system_metrics_name_time ON system_metrics(metric_name, recorded_at);

-- Functions for automatic partition creation
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name text, start_date date)
RETURNS void AS $$
DECLARE
    partition_name text;
    end_date date;
BEGIN
    partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
    end_date := start_date + interval '1 month';
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete old command executions (older than 90 days)
    DELETE FROM command_executions 
    WHERE executed_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    -- Delete old system metrics (older than 30 days)
    DELETE FROM system_metrics 
    WHERE recorded_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    -- Delete old security events (older than 1 year)
    DELETE FROM security_events 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 year';
    
    -- Mark expired connections as inactive
    UPDATE user_connections 
    SET status = 'expired' 
    WHERE expires_at < CURRENT_TIMESTAMP AND status = 'active';
    
    -- Close inactive terminal sessions
    UPDATE terminal_sessions 
    SET is_active = false, closed_at = CURRENT_TIMESTAMP
    WHERE last_activity < CURRENT_TIMESTAMP - INTERVAL '1 hour' AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Views for common queries
CREATE VIEW active_connections AS
SELECT 
    uc.id,
    uc.user_id,
    uc.connection_token,
    uc.socket_port,
    uc.hostname,
    uc.platform,
    uc.last_heartbeat,
    uc.created_at,
    COUNT(ts.id) as active_sessions
FROM user_connections uc
LEFT JOIN terminal_sessions ts ON uc.id = ts.connection_id AND ts.is_active = true
WHERE uc.status = 'active' AND uc.expires_at > CURRENT_TIMESTAMP
GROUP BY uc.id, uc.user_id, uc.connection_token, uc.socket_port, uc.hostname, uc.platform, uc.last_heartbeat, uc.created_at;

CREATE VIEW connection_summary AS
SELECT 
    user_id,
    COUNT(*) as total_connections,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_connections,
    MIN(created_at) as first_connection,
    MAX(last_heartbeat) as last_activity
FROM user_connections
GROUP BY user_id;

-- Trigger to update last_activity in terminal_sessions
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE terminal_sessions 
    SET last_activity = CURRENT_TIMESTAMP 
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_activity
    AFTER INSERT ON command_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();

-- Schedule cleanup function (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data();');

-- Grant permissions (adjust as needed for your environment)
-- CREATE ROLE nolink_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nolink_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nolink_app;
