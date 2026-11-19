
import unittest

from diff_analyzer import analyze_changed_constants


class TestDiffAnalyzer(unittest.TestCase):

    def test_modified_setting_mismatch(self):
        old = "MAX_USERS = 100"
        new = "MAX_USERS = 200"
        docs = "MAX_USERS: 100"

        result = analyze_changed_constants(old, new, docs)

        self.assertEqual(
            result["results"][0]["status"],
            "mismatch"
        )

    def test_modified_setting_correct(self):
        old = "MAX_USERS = 100"
        new = "MAX_USERS = 200"
        docs = "MAX_USERS: 200"

        result = analyze_changed_constants(old, new, docs)

        self.assertEqual(
            result["results"][0]["status"],
            "match"
        )

    def test_new_setting_missing_documentation(self):
        old = "PORT = 5000"
        new = "PORT = 5000\nMAX_USERS = 200"
        docs = "PORT: 5000"

        result = analyze_changed_constants(old, new, docs)

        self.assertEqual(
            result["results"][0]["status"],
            "missing_documentation"
        )

    def test_removed_setting_still_documented(self):
        old = "MAX_USERS = 100\nPORT = 5000"
        new = "PORT = 5000"
        docs = "MAX_USERS: 100\nPORT: 5000"

        result = analyze_changed_constants(old, new, docs)

        self.assertEqual(
            result["results"][0]["status"],
            "stale_reference"
        )

    def test_unchanged_setting_ignored(self):
        old = "PORT = 5000"
        new = "PORT = 5000"
        docs = "PORT: 5000"

        result = analyze_changed_constants(old, new, docs)

        self.assertEqual(len(result["results"]), 0)

    def test_line_number_change_is_not_a_setting_change(self):
        old = "PORT = 5000\nMAX_USERS = 100"
        new = "MAX_USERS = 100\nPORT = 5000"
        docs = "PORT: 5000\nMAX_USERS: 100"

        result = analyze_changed_constants(old, new, docs)

        self.assertEqual(result["changed_settings"], 0)
        self.assertEqual(len(result["results"]), 0)


if __name__ == "__main__":
    unittest.main()
