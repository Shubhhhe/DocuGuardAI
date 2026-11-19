
import re

from analyzer import extract_constants, analyze_files


def analyze_changed_constants(old_source, new_source, docs_text):
    """
    Compare old and new Python source.
    Analyze only configuration constants that changed.
    """

    old_constants = extract_constants(old_source)
    new_constants = extract_constants(new_source)

    changed_names = set(old_constants) | set(new_constants)

    results = []

    # Run the existing analyzer once on the new code and documentation.
    report = analyze_files(new_source, docs_text)

    for name in sorted(changed_names):
        old_info = old_constants.get(name)
        new_info = new_constants.get(name)

        old_value = old_info["value"] if old_info else None
        new_value = new_info["value"] if new_info else None

        # Ignore settings whose values have not changed.
        if old_value == new_value:
            continue

        if old_info is None:
            change_type = "added"
        elif new_info is None:
            change_type = "removed"
        else:
            change_type = "modified"

        matching_lines = [
            (line_number, line.strip())
            for line_number, line in enumerate(
                docs_text.splitlines(), start=1
            )
            if re.search(
                r"\b" + re.escape(name) + r"\b",
                line,
                re.IGNORECASE
            )
        ]

        # A removed setting should not remain in documentation.
        if change_type == "removed":
            for line_number, line in matching_lines:
                results.append({
                    "name": name,
                    "change_type": change_type,
                    "old_value": old_value,
                    "code_value": None,
                    "doc_line": line_number,
                    "doc_sentence": line,
                    "status": "stale_reference",
                    "suggestion": (
                        f"Remove or update the documentation for "
                        f"the removed setting {name}."
                    )
                })

            continue

        # New or modified settings must be documented.
        if not matching_lines:
            results.append({
                "name": name,
                "change_type": change_type,
                "old_value": old_value,
                "code_value": new_value,
                "doc_line": None,
                "doc_sentence": None,
                "status": "missing_documentation",
                "suggestion": (
                    f"Add documentation for {name} "
                    f"with value {new_value}."
                )
            })

            continue

        matching_results = [
            item for item in report["results"]
            if item["name"] == name
        ]

        for item in matching_results:
            doc_line = next(
                (
                    line_number
                    for line_number, line in matching_lines
                    if line == item["doc_sentence"]
                ),
                None
            )

            results.append({
                "name": name,
                "change_type": change_type,
                "old_value": old_value,
                "code_value": new_value,
                "doc_line": doc_line,
                "doc_sentence": item["doc_sentence"],
                "status": item["status"],
                "suggestion": item["suggestion"]
            })

    changed_settings = sum(
        1
        for name in changed_names
        if (
            old_constants.get(name, {}).get("value")
            != new_constants.get(name, {}).get("value")
        )
    )

    return {
        "changed_settings": changed_settings,
        "results": results
    }
