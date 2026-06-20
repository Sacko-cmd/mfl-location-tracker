from transfer_detector import detect_transfers


def refresh_now():
    try:
        events = detect_transfers()
        count = len(events)
        return f"Transfer check completed. {count} new event(s) found."
    except Exception as e:
        return f"Refresh failed: {e}"
