from datetime import date, timedelta

def get_next_saturday() -> date:
    """Get the coming Saturday's date."""
    today = date.today()
    days_ahead = 5 - today.weekday()  # Saturday = 5
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

def get_current_saturday() -> date:
    """Get the current week's Saturday (most recent Saturday)."""
    today = date.today()
    days_back = (today.weekday() - 5) % 7
    return today - timedelta(days=days_back)
