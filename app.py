import os
import logging
import threading

from flask import Flask, jsonify
from werkzeug.serving import WSGIRequestHandler

from healthcheck import run_healthcheck
from marketplace.routes import marketplace_bp
from marketplace.storage import load_monitors
from startup import startup

app = Flask(__name__)
app.register_blueprint(marketplace_bp)

_tracker_started = False
_tracker_lock = threading.Lock()


class QuietHealthCheckHandler(WSGIRequestHandler):
    def log_request(self, code="-", size="-"):
        if self.path.startswith("/health"):
            return
        super().log_request(code, size)


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "location_tracker": True,
        "marketplace_monitors": len(load_monitors()),
    })


@app.route("/health")
def health():
    report = run_healthcheck()
    report["status"] = "ok"
    return jsonify(report), 200


@app.route("/status")
def status():
    report = run_healthcheck()
    report["tracker_started"] = _tracker_started
    return jsonify(report), 200


def tracker_thread():
    startup()


def start_tracker():
    global _tracker_started

    with _tracker_lock:
        if _tracker_started:
            return

        _tracker_started = True
        threading.Thread(target=tracker_thread, daemon=True).start()


start_tracker()


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        request_handler=QuietHealthCheckHandler,
    )
