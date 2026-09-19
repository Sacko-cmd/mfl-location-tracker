CREATE TABLE tracker (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  state_json TEXT NOT NULL DEFAULT '{}',
  initialized INTEGER NOT NULL DEFAULT 0,
  pool_count INTEGER NOT NULL DEFAULT 0,
  pending_count INTEGER NOT NULL DEFAULT 0,
  last_attempt TEXT,
  last_success TEXT,
  last_error TEXT,
  lock_token TEXT,
  locked_until INTEGER NOT NULL DEFAULT 0
);
INSERT INTO tracker(id) VALUES(1);
CREATE TABLE transfers (
  event_id TEXT PRIMARY KEY,
  detected_at TEXT NOT NULL,
  club_id TEXT NOT NULL,
  city TEXT,
  country TEXT,
  manager TEXT,
  wallet TEXT,
  club_name TEXT,
  delivery TEXT NOT NULL,
  delivery_attempts INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX transfers_delivery ON transfers(delivery, detected_at);
