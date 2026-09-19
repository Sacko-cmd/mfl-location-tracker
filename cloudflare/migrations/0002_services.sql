ALTER TABLE transfers ADD COLUMN message_id TEXT;
ALTER TABLE transfers ADD COLUMN delivered_at TEXT;
CREATE TABLE service_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE monitors (
  id TEXT PRIMARY KEY,
  install_id TEXT NOT NULL,
  config_json TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  seen_json TEXT NOT NULL DEFAULT '[]',
  last_check TEXT,
  last_error TEXT,
  next_check INTEGER NOT NULL DEFAULT 0,
  lock_token TEXT,
  locked_until INTEGER NOT NULL DEFAULT 0,
  new_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX monitors_install ON monitors(install_id);
CREATE INDEX monitors_due ON monitors(enabled, next_check);
CREATE TABLE subscribers (
  user_id TEXT PRIMARY KEY,
  webhook TEXT NOT NULL,
  cities TEXT NOT NULL DEFAULT '[]',
  countries TEXT NOT NULL DEFAULT '[]',
  club_ids TEXT NOT NULL DEFAULT '[]',
  paused INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE notifications (
  id TEXT PRIMARY KEY,
  source_kind TEXT NOT NULL,
  source_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'pending',
  attempts INTEGER NOT NULL DEFAULT 0,
  next_attempt INTEGER NOT NULL DEFAULT 0,
  lease_until INTEGER NOT NULL DEFAULT 0,
  lock_token TEXT,
  last_error TEXT,
  message_id TEXT,
  channel_id TEXT,
  sent_at TEXT
);
CREATE INDEX notifications_due ON notifications(state, next_attempt);
