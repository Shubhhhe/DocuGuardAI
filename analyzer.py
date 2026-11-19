import ast
import re

def extract_constants(source):
    """
    Extract simple top-level assignments such as:
        MAX_USERS = 100
        PORT = 5000
    This starter version intentionally supports simple constants only.
    """
    tree = ast.parse(source)
    constants = {}

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    continue

                if isinstance(value, (str, int, float, bool)):
                    constants[target.id] = {
                        "value": str(value),
                        "line": node.lineno
                    }

        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue

            if isinstance(value, (str, int, float, bool)):
                constants[node.target.id] = {
                    "value": str(value),
                    "line": node.lineno
                }

    return constants

def analyze_files(code_text, readme_text):
    constants = extract_constants(code_text)
    sentences = re.split(r"(?<=[.!?])\s+|\n+", readme_text.strip())
    results = []
    checked = 0

    for name, info in constants.items():
        # Find documentation lines/sentences that mention this exact setting.
        matching = [s.strip() for s in sentences
                    if re.search(r"\b" + re.escape(name) + r"\b", s, re.IGNORECASE)]

        for sentence in matching:
            checked += 1
            # Find a simple documented value after :, =, or is.
            match = re.search(
                r"(?:[:=]\s*| is\s+)(['\"]?[-\w.]+['\"]?)\s*$",
                sentence,
                re.IGNORECASE
            )

            if not match:
                results.append({
                    "name": name,
                    "code_value": info["value"],
                    "code_line": info["line"],
                    "doc_sentence": sentence,
                    "doc_value": "Could not identify",
                    "status": "uncertain",
                    "suggestion": f"Review this sentence and verify that {name} is documented as {info['value']}."
                })
                continue

            doc_value = match.group(1).strip("'\"")
            if doc_value != info["value"]:
                corrected = re.sub(
                    r"(['\"]?[-\w.]+['\"]?)\s*$",
                    info["value"],
                    sentence
                )
                results.append({
                    "name": name,
                    "code_value": info["value"],
                    "code_line": info["line"],
                    "doc_sentence": sentence,
                    "doc_value": doc_value,
                    "status": "mismatch",
                    "suggestion": corrected
                })
            else:
                results.append({
                    "name": name,
                    "code_value": info["value"],
                    "code_line": info["line"],
                    "doc_sentence": sentence,
                    "doc_value": doc_value,
                    "status": "match",
                    "suggestion": "No correction needed."
                })

    return {
        "constants_found": len(constants),
        "sentences_checked": checked,
        "results": results,
        "note": "Prototype supports simple top-level Python constants and documentation lines that explicitly mention the same setting name. It does not prove general semantic consistency."
    }
