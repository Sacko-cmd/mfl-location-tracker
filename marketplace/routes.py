from flask import Blueprint, jsonify, request

from config import MAX_MONITORS_PER_INSTALL
from marketplace.poll import poll_monitor
from marketplace.scheduler import clear_timer, reschedule_one, schedule_one
from marketplace.storage import load_monitors, save_monitors

marketplace_bp = Blueprint("marketplace", __name__)


@marketplace_bp.after_request
def cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PATCH,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,X-Install-ID"
    return response


@marketplace_bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return "", 204


def get_install_id():
    return (request.headers.get("X-Install-ID") or "").strip()


def count_for_install(install_id):
    return sum(1 for m in load_monitors() if m.get("installId") == install_id)


@marketplace_bp.get("/monitors")
def list_monitors():
    install_id = get_install_id()
    if not install_id:
        return jsonify({"error": "X-Install-ID header required"}), 400
    return jsonify([m for m in load_monitors() if m.get("installId") == install_id])


@marketplace_bp.post("/monitors")
def add_monitor():
    install_id = get_install_id()
    if not install_id:
        return jsonify({"error": "X-Install-ID header required"}), 400

    body = request.get_json(silent=True) or {}
    monitor_id = body.get("id")
    api_url = body.get("apiUrl")
    if not monitor_id or not api_url:
        return jsonify({"error": "id and apiUrl required"}), 400

    monitors = load_monitors()
    if any(m.get("id") == monitor_id for m in monitors):
        return jsonify({"error": "already exists"}), 409

    install_count = sum(1 for m in monitors if m.get("installId") == install_id)
    if install_count >= MAX_MONITORS_PER_INSTALL:
        return jsonify({
            "error": f"monitor limit reached ({MAX_MONITORS_PER_INSTALL} max per install)",
        }), 403

    monitor = {
        "id": monitor_id,
        "installId": install_id,
        "label": body.get("label"),
        "pageUrl": body.get("pageUrl"),
        "apiUrl": api_url,
        "discordWebhook": body.get("discordWebhook"),
        "notifMode": body.get("notifMode") or "discord",
        "intervalMinutes": body.get("intervalMinutes") or 1,
        "enabled": True,
        "seenIds": [],
        "lastCheck": None,
        "lastError": None,
    }

    monitors.append(monitor)
    save_monitors(monitors)
    schedule_one(monitor)
    return jsonify(monitor), 201


@marketplace_bp.patch("/monitors/<monitor_id>")
def update_monitor(monitor_id):
    install_id = get_install_id()
    monitors = load_monitors()
    idx = next(
        (i for i, m in enumerate(monitors)
         if m.get("id") == monitor_id and m.get("installId") == install_id),
        -1,
    )
    if idx == -1:
        return jsonify({"error": "not found"}), 404

    body = request.get_json(silent=True) or {}
    for key in ("enabled", "intervalMinutes", "label", "discordWebhook", "notifMode"):
        if key in body:
            monitors[idx][key] = body[key]
    if body.get("enabled"):
        monitors[idx]["lastError"] = None

    save_monitors(monitors)
    reschedule_one(monitors[idx])
    return jsonify(monitors[idx])


@marketplace_bp.delete("/monitors/<monitor_id>")
def delete_monitor(monitor_id):
    install_id = get_install_id()
    monitors = load_monitors()
    monitor = next(
        (m for m in monitors
         if m.get("id") == monitor_id and m.get("installId") == install_id),
        None,
    )
    if not monitor:
        return jsonify({"error": "not found"}), 404

    save_monitors([m for m in monitors if m.get("id") != monitor_id])
    clear_timer(monitor_id)
    return "", 204


@marketplace_bp.post("/monitors/<monitor_id>/poll")
def trigger_poll(monitor_id):
    install_id = get_install_id()
    monitor = next(
        (m for m in load_monitors()
         if m.get("id") == monitor_id and m.get("installId") == install_id),
        None,
    )
    if not monitor:
        return jsonify({"error": "not found"}), 404

    poll_monitor(monitor)
    return jsonify({"ok": True})
