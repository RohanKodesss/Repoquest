from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def check_repo():
    """
    Validate the URL, look in the cache first, otherwise fetch GitHub data,
    build the map, check connectivity, save to cache, return traffic light.
    """
    # Placeholder — Step 2 wires in repo_check and github_fetch.
    return jsonify({"status": "todo"})


@app.route("/api/start", methods=["POST"])
def start_game():
    """
    Load the saved map, add LLM narration (with template fallback),
    validate names, generate quiz, save, return the full game JSON.
    """
    # Placeholder — Step 8 wires in narrator, name_validator, quiz.
    return jsonify({"status": "todo"})


if __name__ == "__main__":
    import os
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(port=5000, debug=debug)
