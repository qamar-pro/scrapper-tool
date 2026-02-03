from datetime import datetime, timedelta

from src.utils.helpers import parse_date, is_date_expired


def test_parse_date_returns_datetime():
    dt = parse_date("2026-01-15 10:00")
    assert dt is not None


def test_is_date_expired_true_for_past_date():
    past_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    assert is_date_expired(past_date) is True
