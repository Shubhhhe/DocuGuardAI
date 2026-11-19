
import re

from analyzer import extract_constants, analyze_files


def _source_line(source, line_number):
    """Return a source line by its one-based line number, if it exists."""
    if line_number is None:
        return None

    lines = source.splitlines()
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1].strip()
    return None


def _doc_line_number(docs_text, sentence, start_at=0):
    """Find the documentation line containing a sentence, preserving line refs."""
    normalized_sentence = " ".join(sentence.split()).casefold()
    lines = docs_text.splitlines()

    for index in range(start_at, len(lines)):
        normalized_line = " ".join(lines[index].split()).casefold()
        if normalized_sentence and normalized_sentence in normalized_line:
            return index + 1, index + 1

    for index, line in enumerate(lines):
        normalized_line = " ".join(line.split()).casefold()
        if normalized_sentence and normalized_sentence in normalized_line:
            return index + 1, max(start_at, index + 1)

    return None, start_at


def analyze_changed_constants(
    old_source,
    new_source,
    docs_text,
    code_file=None,
    docs_file=None,
):
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
            for line_number, line in enumerate(docs_text.splitlines(), start=1)
            if re.search(r"\b" + re.escape(name) + r"\b", line, re.IGNORECASE)
        ]

        # A removed setting should not remain in documentation.
        if change_type == "removed":
            for line_number, line in matching_lines:
                results.append({
                    "name": name,
                    "change_type": change_type,
                    "old_value": old_value,
                    "code_value": None,
                    "code_file": code_file,
                    "old_code_line": old_info["line"],
                    "old_code_line_text": _source_line(old_source, old_info["line"]),
                    "code_line": None,
                    "code_line_text": None,
                    "doc_file": docs_file,
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
                "code_file": code_file,
                "old_code_line": old_info["line"] if old_info else None,
                "old_code_line_text": (
                    _source_line(old_source, old_info["line"]) if old_info else None
                ),
                "code_line": new_info["line"],
                "code_line_text": _source_line(new_source, new_info["line"]),
                "doc_file": docs_file,
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

        next_doc_line = 0
        for item in matching_results:
            doc_line, next_doc_line = _doc_line_number(
                docs_text, item["doc_sentence"], next_doc_line
            )

            results.append({
                "name": name,
                "change_type": change_type,
                "old_value": old_value,
                "code_value": new_value,
                "code_file": code_file,
                "old_code_line": old_info["line"] if old_info else None,
                "old_code_line_text": (
                    _source_line(old_source, old_info["line"]) if old_info else None
                ),
                "code_line": new_info["line"],
                "code_line_text": _source_line(new_source, new_info["line"]),
                "doc_file": docs_file,
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
