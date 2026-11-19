from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dashboard.server import read_snapshot
from deployment.wsl.collect_metrics import projects


class DashboardMetricsTests(unittest.TestCase):
    def test_missing_and_stale_snapshots_are_distinguishable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "windows.json"
            self.assertEqual(read_snapshot(path), {"state": "unavailable"})
            now = datetime.now(timezone.utc)
            for state, age in [("current", 5), ("stale", 200)]:
                with self.subTest(state=state):
                    data = {"collected_at": (now - timedelta(seconds=age)).isoformat()}
                    path.write_text(json.dumps(data))
                    self.assertEqual(read_snapshot(path), {"state": state, "snapshot": data})

    @patch("deployment.wsl.collect_metrics.docker_lines")
    def test_containers_are_grouped_by_compose_and_completed_jobs_have_no_stats(self, docker):
        docker.side_effect = [
            [
                {"project": "tracker", "name": "db_init", "state": "exited", "status": "Exited (0)"},
                {"project": "", "name": "standalone", "state": "running", "status": "Up"},
                {"project": "tracker", "name": "web", "state": "running", "status": "Up"},
            ],
            [
                {"Name": "web", "CPUPerc": "0.10%", "MemUsage": "8MiB / 1GiB"},
                {"Name": "standalone", "CPUPerc": "0.20%", "MemUsage": "16MiB / 1GiB"},
            ],
        ]

        tracker, standalone = projects()
        self.assertEqual(tracker["name"], "tracker")
        self.assertIsNone(standalone["name"])
        init, web = tracker["containers"]
        self.assertIsNone(init["memory"])
        self.assertEqual((web["cpu"], web["memory"]), ("0.10%", "8MiB"))
