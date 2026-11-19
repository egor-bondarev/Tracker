import io
import json
import unittest
from contextlib import redirect_stdout
from urllib.error import HTTPError
from unittest.mock import patch

from scripts import check_tracker


class TrackerHealthTests(unittest.TestCase):
    def test_empty_database_can_still_be_ready(self):
        with patch.object(check_tracker, "request", side_effect=[
            b'<div id="root"></div>',
            b'{"data":{"tasksInPeriod":[]}}',
            b'{"status":"ready"}',
        ]) as request:
            result = check_tracker.check_tracker("http://web/", "http://record/")

        self.assertTrue(result["ok"])
        self.assertEqual(
            [call.args[0] for call in request.call_args_list],
            ["http://web/", "http://web/graphql", "http://record/ready"],
        )
        self.assertIn("tasksInPeriod", request.call_args_list[1].args[2]["query"])

    def test_graphql_errors_and_record_failure_make_cli_exit_nonzero(self):
        output = io.StringIO()
        with patch("sys.argv", ["check_tracker.py"]), redirect_stdout(output):
            with patch.object(check_tracker, "request", side_effect=[
                b'<div id="root"></div>',
                b'{"errors":[{"message":"internal database details"}],"data":{"tasksInPeriod":null}}',
                HTTPError("http://record/ready", 503, "Unavailable", None, None),
            ]):
                self.assertEqual(check_tracker.main(), 1)

        result = json.loads(output.getvalue())
        self.assertFalse(result["ok"])
        self.assertEqual([check["ok"] for check in result["checks"]], [True, False, False])
        self.assertEqual(result["checks"][2]["detail"], "HTTP 503")
        self.assertNotIn("internal database details", output.getvalue())
