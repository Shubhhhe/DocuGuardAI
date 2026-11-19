
import argparse
import subprocess
import sys

from analyzer import analyze_files


def run_git(command):
    """Run a Git command and return its output."""
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        return None

    return result.stdout


def get_file_at_commit(commit, file_path):
    """Read a file exactly as it existed in a Git commit."""
    return run_git(["git", "show", f"{commit}:{file_path}"])


def get_commit_info(commit):
    """Get short commit hash and commit message."""
    output = run_git([
        "git", "show", "-s", "--format=%h|%s", commit
    ])

    if not output:
        return commit[:7], "Unknown commit"

    parts = output.strip().split("|", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def find_doc_line(docs_text, sentence):
    """Find the documentation line containing a reported sentence."""
    for number, line in enumerate(docs_text.splitlines(), start=1):
        if sentence.strip().casefold() in line.strip().casefold():
            return number

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Replay Git history to detect historical documentation drift."
    )

    parser.add_argument(
        "--code",
        default="samples/demo_config.py",
        help="Python file to analyze"
    )

    parser.add_argument(
        "--docs",
        default="samples/README.md",
        help="Markdown documentation file"
    )

    args = parser.parse_args()

    commits_output = run_git([
        "git", "rev-list", "--reverse", "--first-parent", "HEAD"
    ])

    if commits_output is None:
        print("ERROR: Could not read Git history.")
        return 2

    commits = commits_output.splitlines()

    if not commits:
        print("ERROR: No commits found.")
        return 2

    print("\nDOCUGUARD AI - HISTORICAL REPLAY")
    print("=" * 55)
    print("Code file:", args.code)
    print("Documentation:", args.docs)
    print("Commits found:", len(commits))
    print("=" * 55)

    previous_issues = set()
    checked = 0
    drift_commits = 0

    for commit in commits:
        old_code = get_file_at_commit(commit, args.code)
        docs = get_file_at_commit(commit, args.docs)

        # Skip commits where either file did not exist.
        if old_code is None or docs is None:
            continue

        try:
            report = analyze_files(old_code, docs)
        except (SyntaxError, ValueError) as error:
            short_hash, message = get_commit_info(commit)
            print(f"\nSKIPPED: {short_hash} - {message}")
            print("Reason:", error)
            continue

        checked += 1
        short_hash, message = get_commit_info(commit)

        issues = [
            item for item in report["results"]
            if item["status"] in ("mismatch", "uncertain")
        ]

        current_issues = {
            (
                item["name"],
                item["status"],
                item["code_value"],
                item.get("doc_value")
            )
            for item in issues
        }

        if issues:
            drift_commits += 1

            print(f"\nCOMMIT: {short_hash}")
            print("Message:", message)

            for item in issues:
                signature = (
                    item["name"],
                    item["status"],
                    item["code_value"],
                    item.get("doc_value")
                )

                label = (
                    "NEW DRIFT"
                    if signature not in previous_issues
                    else "ONGOING ISSUE"
                )

                doc_line = find_doc_line(
                    docs, item["doc_sentence"]
                )

                print(f"\n  [{label}]")
                print("  Setting:", item["name"])
                print("  Status:", item["status"])
                print("  Code value:", item["code_value"])
                print("  Documented value:", item.get("doc_value"))
                print(
                    "  Code reference:",
                    f"{args.code}:{item['code_line']}"
                )

                if doc_line is not None:
                    print(
                        "  Documentation reference:",
                        f"{args.docs}:{doc_line}"
                    )

                print("  Documentation:", item["doc_sentence"])
                print("  Suggestion:", item["suggestion"])

        elif previous_issues:
            print(f"\nRESOLVED: {short_hash} - {message}")

        previous_issues = current_issues

    print("\n" + "=" * 55)
    print("HISTORICAL REPLAY SUMMARY")
    print("=" * 55)
    print("Commits checked:", checked)
    print("Commits containing documentation issues:", drift_commits)

    if drift_commits:
        print("Result: Historical documentation drift was detected.")
    else:
        print("Result: No documentation drift detected in checked commits.")

    print("\nHistorical replay completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
