from src.models.event import Event


def test_event_id_generation_is_stable():
    event = Event(
        event_name="Sample Event",
        date="2026-01-01",
        venue="Test Venue",
        city="Mumbai",
        category="Music",
        url="https://example.com",
        source="BookMyShow",
    )
    event2 = Event(
        event_name="Sample Event",
        date="2026-01-01",
        venue="Test Venue",
        city="Mumbai",
        category="Music",
        url="https://example.com",
        source="BookMyShow",
    )
    assert event.event_id == event2.event_id


def test_event_to_dict_contains_expected_keys():
    event = Event(
        event_name="Sample Event",
        date="2026-01-01",
        venue="Test Venue",
        city="Mumbai",
        category="Music",
        url="https://example.com",
        source="BookMyShow",
    )
    data = event.to_dict()
    assert "Event Name" in data
    assert data["Event Name"] == "Sample Event"
