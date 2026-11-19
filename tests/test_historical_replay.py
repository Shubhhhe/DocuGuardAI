
import unittest
from unittest.mock import patch

from historical_replay import (
    find_doc_line,
    get_commit_info,
    get_file_at_commit,
    run_git,
)


class TestHistoricalReplay(unittest.TestCase):

    def test_run_git_returns_output(self):
        with patch("historical_replay.subprocess.run") as mocked:
            mocked.return_value.returncode = 0
            mocked.return_value.stdout = "abc123\n"

            result = run_git(["git", "log"])

        self.assertEqual(result, "abc123\n")

    def test_run_git_returns_none_on_error(self):
        with patch("historical_replay.subprocess.run") as mocked:
            mocked.return_value.returncode = 1
            mocked.return_value.stdout = ""

            result = run_git(["git", "invalid-command"])

        self.assertIsNone(result)

    def test_get_file_at_commit(self):
        with patch("historical_replay.run_git") as mocked:
            mocked.return_value = "MAX_USERS = 250"

            result = get_file_at_commit(
                "abc123",
                "samples/demo_config.py"
            )

        self.assertEqual(result, "MAX_USERS = 250")

    def test_get_commit_info(self):
        with patch("historical_replay.run_git") as mocked:
            mocked.return_value = "abc123|Fix documentation drift\n"

            short_hash, message = get_commit_info("abc123")

        self.assertEqual(short_hash, "abc123")
        self.assertEqual(message, "Fix documentation drift")

    def test_find_doc_line(self):
        docs = "# Demo\n\nMAX_USERS: 250\nPORT: 5000"

        result = find_doc_line(docs, "MAX_USERS: 250")

        self.assertEqual(result, 3)

    def test_find_doc_line_when_missing(self):
        docs = "# Demo\nMAX_USERS: 250"

        result = find_doc_line(docs, "PORT: 5000")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
