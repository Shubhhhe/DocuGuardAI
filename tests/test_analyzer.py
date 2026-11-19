
import unittest
from analyzer import analyze_files


class TestDocuGuard(unittest.TestCase):

    def test_mismatch_detection(self):
        code = "MAX_USERS = 100"
        docs = "MAX_USERS: 50"

        result = analyze_files(code, docs)
        self.assertEqual(result["results"][0]["status"], "mismatch")

    def test_correct_documentation(self):
        code = "MAX_USERS = 100"
        docs = "MAX_USERS: 100"

        result = analyze_files(code, docs)
        self.assertEqual(result["results"][0]["status"], "match")

    def test_uncertain_documentation(self):
        code = "MAX_USERS = 100"
        docs = "MAX_USERS controls the user limit."

        result = analyze_files(code, docs)
        self.assertEqual(result["results"][0]["status"], "uncertain")


if __name__ == "__main__":
    unittest.main()
