CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT create_hypertable('quota_usage', 'date', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_ab_tests_user_id ON ab_tests(user_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_title_rotations_ab_test_id ON title_rotations(ab_test_id);
CREATE INDEX IF NOT EXISTS idx_quota_usage_user_id ON quota_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_quota_usage_date ON quota_usage(date);
