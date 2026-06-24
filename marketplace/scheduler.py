import threading

from logger import log_info
from marketplace.poll import poll_monitor
from marketplace.storage import load_monitors

_timers = {}
_lock = threading.Lock()


def clear_timer(monitor_id):
    with _lock:
        timer = _timers.pop(monitor_id, None)
        if timer:
            timer.cancel()


def _tick(monitor_id):
    monitors = load_monitors()
    monitor = next((m for m in monitors if m.get("id") == monitor_id), None)
    if not monitor or not monitor.get("enabled"):
        clear_timer(monitor_id)
        return

    poll_monitor(monitor)

    interval = (monitor.get("intervalMinutes") or 1) * 60
    timer = threading.Timer(interval, _tick, args=[monitor_id])
    timer.daemon = True
    with _lock:
        _timers[monitor_id] = timer
    timer.start()


def schedule_one(monitor):
    clear_timer(monitor["id"])
    if not monitor.get("enabled"):
        return

    poll_monitor(monitor)
    interval = (monitor.get("intervalMinutes") or 1) * 60
    timer = threading.Timer(interval, _tick, args=[monitor["id"]])
    timer.daemon = True
    with _lock:
        _timers[monitor["id"]] = timer
    timer.start()


def reschedule_one(monitor):
    clear_timer(monitor["id"])
    if monitor.get("enabled"):
        schedule_one(monitor)


def schedule_all():
    monitors = load_monitors()
    active = [m for m in monitors if m.get("enabled")]
    log_info(f"[Marketplace] Scheduling {len(active)} active monitor(s)")
    for i, monitor in enumerate(active):
        threading.Timer(i * 2, schedule_one, args=[monitor]).start()
