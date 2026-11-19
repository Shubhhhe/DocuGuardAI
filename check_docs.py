
from pathlib import Path
import sys
from analyzer import analyze_files

code_path = Path("samples/demo_config.py")
docs_path = Path("samples/README.md")

code = code_path.read_text(encoding="utf-8")
docs = docs_path.read_text(encoding="utf-8")

report = analyze_files(code, docs)

print("\nDOCUGUARD DOCUMENTATION CHECK")
print("-" * 35)

mismatches = 0

for item in report["results"]:
    print(f"\nSetting: {item['name']}")
    print(f"Status: {item['status']}")
    print(f"Code value: {item['code_value']}")
    print(f"Documentation: {item['doc_sentence']}")

    if item["status"] == "mismatch":
        mismatches += 1
        print(f"Suggested correction: {item['suggestion']}")

print("\nTotal mismatches:", mismatches)

if mismatches:
    print("FAILED: Documentation needs correction.")
    sys.exit(1)

print("PASSED: No detected value mismatches.")
