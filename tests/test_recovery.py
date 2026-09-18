import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import healthcheck
import mfl_api
import tracker_status
from marketplace import storage
from marketplace.poll import poll_monitor

OLD = "https://z519wdyajg.execute-api.us-east-1.amazonaws.com/prod/listings"


class RecoveryTests(unittest.TestCase):
    def test_legacy_query_preserved_and_headers_sent(self):
        url = OLD + "?type=CLUB&clubStatus=NOT_FOUNDED&country=A%26B"
        with patch("mfl_api.requests.get") as get:
            mfl_api.mfl_get(url)
        self.assertEqual(get.call_args.args[0], url.replace(OLD, "https://api.playmfl.com/listings"))
        self.assertEqual(get.call_args.kwargs["headers"]["Origin"], "https://app.playmfl.com")
        self.assertIn("Mozilla", get.call_args.kwargs["headers"]["User-Agent"])

    def test_unrelated_hosts_are_not_rewritten(self):
        for url in ["https://example.com/prod/listings", OLD.replace("amazonaws.com", "amazonaws.com.example.org")]:
            self.assertEqual(mfl_api.normalize_mfl_url(url), url)

    def test_configured_base_applies_to_legacy_and_current_urls(self):
        with patch("mfl_api.MFL_API_BASE_URL", "https://example.test/v2"):
            self.assertEqual(mfl_api.normalize_mfl_url(OLD), "https://example.test/v2/listings")
            self.assertEqual(mfl_api.normalize_mfl_url("https://api.playmfl.com/clubs/35"), "https://example.test/v2/clubs/35")

    def test_old_monitor_polls_and_keeps_seen_history(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(storage, "MONITORS_FILE", str(Path(tmp) / "monitors.json")):
            monitor = {"id": "old", "apiUrl": OLD + "?type=CLUB", "enabled": True, "seenIds": ["123"]}
            storage.save_monitors([monitor])
            loaded = storage.load_monitors()[0]
            self.assertEqual(loaded["seenIds"], ["123"])
            self.assertTrue(loaded["apiUrl"].startswith("https://api.playmfl.com/"))
            with patch("mfl_api.requests.get") as get, patch("marketplace.poll.send_discord") as send:
                get.return_value.json.return_value = [{"listingResourceId": "123"}]
                poll_monitor(loaded)
                send.assert_not_called()
            saved = json.loads(Path(storage.MONITORS_FILE).read_text())[0]
            self.assertEqual(saved["seenIds"], ["123"])
            self.assertTrue(saved["lastCheck"])
            self.assertIsNone(saved["lastError"])
            self.assertTrue(saved["apiUrl"].startswith("https://api.playmfl.com/"))

    def test_poll_status_failure_recovery_and_staleness(self):
        with patch.object(tracker_status, "_state", {"last_attempt": None, "last_success": None, "last_error": None}):
            self.assertFalse(tracker_status.get_tracker_status()["healthy"])
            tracker_status.poll_started()
            tracker_status.poll_finished()
            self.assertTrue(tracker_status.get_tracker_status()["healthy"])
            tracker_status.poll_finished(ValueError("private data"))
            status = tracker_status.get_tracker_status()
            self.assertFalse(status["healthy"])
            self.assertEqual(status["last_error"], "ValueError")
            tracker_status.poll_finished()
            self.assertTrue(tracker_status.get_tracker_status()["healthy"])
            tracker_status._state["last_success"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            self.assertFalse(tracker_status.get_tracker_status()["healthy"])

    def test_health_does_not_create_missing_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "absent.db")
            with patch.object(healthcheck, "DATABASE_FILE", db), patch.object(healthcheck, "WALLET_CACHE_FILE", str(Path(tmp) / "missing.json")), patch.object(healthcheck, "load_monitors", return_value=[]):
                report = healthcheck.run_healthcheck()
            self.assertFalse(report["healthy"])
            self.assertFalse(Path(db).exists())
            self.assertEqual(report["marketplace"]["configured"], 0)

    def test_all_state_uses_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = """
import config, storage, pool_log, recipient_cache, stats
from pathlib import Path
paths = [config.DATABASE_FILE, config.MONITORS_FILE, config.WALLET_CACHE_FILE,
         config.WATCHLIST_FILE, storage.STATE_FILE, pool_log.POOL_LOG_FILE,
         recipient_cache.CACHE_FILE, stats.LAST_REFRESH_FILE]
assert all(Path(p).parent == config.DATA_DIR for p in paths), paths
"""
            subprocess.run([sys.executable, "-c", code], env={**os.environ, "DATA_DIR": tmp}, check=True)


if __name__ == "__main__":
    unittest.main()
