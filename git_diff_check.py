
import argparse
import subprocess
import sys
from pathlib import Path

from diff_analyzer import analyze_changed_constants


def get_git_file(base_ref, file_path):
    """Read a file from a previous Git commit."""

    result = subprocess.run(
        ["git", "show", f"{base_ref}:{file_path}"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        return ""

    return result.stdout


def main():
    parser = argparse.ArgumentParser(
        description="Check documentation against changed Python settings."
    )

    parser.add_argument(
        "--base",
        default="HEAD~1",
        help="Git commit or branch to compare against (default: HEAD~1)"
    )

    parser.add_argument(
        "--code",
        default="samples/demo_config.py",
        help="Python source file to analyze"
    )

    parser.add_argument(
        "--docs",
        default="samples/README.md",
        help="Documentation file to check"
    )

    args = parser.parse_args()

    # Make sure the supplied Git reference exists.
    check_ref = subprocess.run(
        ["git", "rev-parse", "--verify", args.base],
        capture_output=True,
        text=True
    )

    if check_ref.returncode != 0:
        print(f"ERROR: Git reference '{args.base}' was not found.")
        return 2

    code_path = Path(args.code)
    docs_path = Path(args.docs)

    if not code_path.exists():
        print(f"ERROR: Code file not found: {code_path}")
        return 2

    if not docs_path.exists():
        print(f"ERROR: Documentation file not found: {docs_path}")
        return 2

    old_code = get_git_file(args.base, args.code)
    new_code = code_path.read_text(encoding="utf-8")
    docs = docs_path.read_text(encoding="utf-8")

    report = analyze_changed_constants(
        old_code,
        new_code,
        docs
    )

    print("\nDOCUGUARD GIT DIFF CHECK")
    print("-" * 40)
    print(f"Base reference: {args.base}")
    print(f"Code file: {args.code}")
    print(f"Documentation: {args.docs}")
    print(f"Changed settings: {report['changed_settings']}")

    if not report["results"]:
        print("\nNo documentation issues detected.")
        return 0

    failed = False

    for item in report["results"]:
        print("\nSetting:", item["name"])
        print("Change type:", item["change_type"])
        print("Status:", item["status"])
        print("Old value:", item["old_value"])
        print("New value:", item["code_value"])
        print("Documentation:", item["doc_sentence"])

        if item["doc_line"] is not None:
            print("Documentation line:", item["doc_line"])

        print("Suggestion:", item["suggestion"])

        if item["status"] != "match":
            failed = True

    print("\n" + "-" * 40)

    if failed:
        print("FAILED: Documentation needs review or correction.")
        return 1

    print("PASSED: Changed settings are documented correctly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
