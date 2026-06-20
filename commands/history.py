from history import get_city_history, get_recent_history


def _row_to_dict(row):
    return {
        "timestamp": row[1],
        "club_id": row[2],
        "city": row[3],
        "country": row[4],
        "manager": row[5],
        "wallet": row[6],
        "club_name": row[7],
    }


def history_command(city):
    rows = get_city_history(city)
    return [_row_to_dict(row) for row in rows]


def recent_command(limit=10):
    rows = get_recent_history(limit)
    return [_row_to_dict(row) for row in rows]
