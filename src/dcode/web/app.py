"""
Flask Web Server Application Factory for Agent-DCODE.
"""

from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS
from dcode.config import BACKEND_HOST, BACKEND_PORT, OLLAMA_MODEL
from dcode.web.routes import ALL_BLUEPRINTS

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> Flask:
    """Create and configure the Flask web application."""
    flask_app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")
    CORS(flask_app)

    for bp in ALL_BLUEPRINTS:
        flask_app.register_blueprint(bp)

    @flask_app.route("/")
    def index():
        return send_from_directory(str(STATIC_DIR), "index.html")

    return flask_app


app = create_app()


def run_server(host: str = BACKEND_HOST, port: int = BACKEND_PORT, debug: bool = True) -> None:
    print(f"🚀 DCode Web UI starting on http://localhost:{port}")
    print(f"📝 Local model: {OLLAMA_MODEL}")
    app.run(debug=debug, host=host, port=port)


if __name__ == "__main__":
    run_server()
