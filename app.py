from flask import Flask, render_template, request
from analyzer import analyze_files

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB upload limit

@app.route("/", methods=["GET", "POST"])
def home():
    report = None
    error = None

    if request.method == "POST":
        code_file = request.files.get("code_file")
        readme_file = request.files.get("readme_file")

        if not code_file or not readme_file or not code_file.filename or not readme_file.filename:
            error = "Please select both a .py file and a README/.md file."
        elif not code_file.filename.lower().endswith(".py"):
            error = "The code file must have a .py extension."
        elif not readme_file.filename.lower().endswith((".md", ".txt")):
            error = "The documentation file must be .md or .txt."
        else:
            try:
                code_text = code_file.read().decode("utf-8")
                readme_text = readme_file.read().decode("utf-8")
                report = analyze_files(code_text, readme_text)
            except UnicodeDecodeError:
                error = "Please upload UTF-8 text files."
            except SyntaxError as exc:
                error = f"Could not parse the Python file: {exc}"

    return render_template("index.html", report=report, error=error)

if __name__ == "__main__":
    app.run(debug=True)
