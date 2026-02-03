from datetime import datetime

from src.storage.excel_storage import ExcelStorage
from src.models.event import Event


def _make_event(name: str, date: str):
    return Event(
        event_name=name,
        date=date,
        venue="Test Venue",
        city="Mumbai",
        category="Music",
        url="https://example.com",
        source="BookMyShow",
        status="Active",
        last_updated=datetime.now(),
    )


def test_excel_storage_save_and_load(tmp_path):
    file_path = tmp_path / "events.xlsx"
    storage = ExcelStorage(str(file_path))

    events = [_make_event("Event A", "2026-01-01")]
    assert storage.save_events(events) is True

    loaded = storage.load_events()
    assert len(loaded) == 1
    assert loaded[0].event_name == "Event A"


def test_excel_storage_merge_updates(tmp_path):
    file_path = tmp_path / "events.xlsx"
    storage = ExcelStorage(str(file_path))

    event = _make_event("Event A", "2026-01-01")
    assert storage.save_events([event]) is True

    event.status = "Updated"
    assert storage.save_events([event]) is True

    loaded = storage.load_events()
    assert len(loaded) == 1
