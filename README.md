# DocuGuard AI – Hackathon MVP

A small Flask prototype that checks simple top-level Python constants against README sentences that explicitly mention the same constant.

## Run on Windows

1. Install Python 3 and tick "Add Python to PATH".
2. Open this folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:

```bash
python -m pip install -r requirements.txt
python app.py
```

If `python` is not recognized, try `py` instead.

5. Open http://127.0.0.1:5000 in your browser.
6. Upload `samples/demo_config.py` as the Python file and `samples/README.md` as the documentation file.

## What this prototype supports

- Simple top-level assignments such as `MAX_USERS = 100`
- README lines that explicitly mention the same setting name and a simple value
- Reporting matching values, potential mismatches, and uncertain cases
- Showing source line evidence and a suggested text correction
- For changed settings, reporting the previous and current Python file lines and the matching documentation file and line

## Limitations

This is a controlled prototype, not a complete semantic documentation drift detector. It does not analyze Git diffs, historical pull requests, arbitrary prose, dynamic code, or all programming languages. The correction is rule-based; no AI API is required for the core demo.

## Suggested next steps

- Add GitHub pull request / commit comparison.
- Add tests for supported and unsupported examples.
- Add semantic matching and AI-assisted explanations, while keeping evidence visible.
- Evaluate on historical documentation-fix commits from public repositories.
