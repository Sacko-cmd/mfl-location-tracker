import os
import threading

from flask import Flask, jsonify

from healthcheck import run_healthcheck
from startup import startup

app = Flask(__name__)

_tracker_started = False
_tracker_lock = threading.Lock()


@app.route("/")
def home():
    return "MFL Tracker Running"


@app.route("/health")
def health():
    report = run_healthcheck()
    report["status"] = "ok"
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
