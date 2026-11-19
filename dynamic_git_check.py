
import argparse
import subprocess
import sys
from pathlib import Path

from diff_analyzer import analyze_changed_constants


ROOT = Path(__file__).resolve().parent


def git_output(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout


def read_old_file(base, path):
    result = subprocess.run(
        ["git", "show", f"{base}:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    return result.stdout if result.returncode == 0 else ""


def collect_documentation():
    docs = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if ".git" in path.parts or ".venv" in path.parts:
            continue

        if path.suffix.lower() not in (".md", ".txt"):
            continue

        relative = path.relative_to(ROOT).as_posix()
        content = path.read_text(encoding="utf-8")

        docs.append(f"\n# Documentation file: {relative}\n{content}")

    return "\n".join(docs)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze documentation for all changed Python files."
    )

    parser.add_argument(
        "--base",
        default="HEAD~1",
        help="Git reference to compare against"
    )

    args = parser.parse_args()

    try:
        changed_files = git_output(
            "diff",
            "--name-only",
            f"{args.base}...HEAD",
            "--",
            "*.py"
        ).splitlines()

        docs = collect_documentation()

        print("\nDOCUGUARD DYNAMIC GIT CHECK")
        print("-" * 40)

        if not changed_files:
            print("No changed Python files found.")
            return 0

        failed = False

        for file_name in changed_files:
            code_path = ROOT / file_name

            if code_path.exists():
                new_code = code_path.read_text(encoding="utf-8")
            else:
                new_code = ""

            old_code = read_old_file(args.base, file_name)

            report = analyze_changed_constants(
                old_code,
                new_code,
                docs
            )

            print(f"\nFile: {file_name}")
            print("Changed settings:", report["changed_settings"])

            for item in report["results"]:
                print(f"\nSetting: {item['name']}")
                print("Status:", item["status"])
                print("Suggestion:", item["suggestion"])

                if item["status"] != "match":
                    failed = True

        print("\n" + "-" * 40)

        if failed:
            print("FAILED: Documentation needs review.")
            return 1

        print("PASSED: No documentation issues detected.")
        return 0

    except (RuntimeError, OSError) as error:
        print("ERROR:", error)
        return 2


if __name__ == "__main__":
    sys.exit(main())
