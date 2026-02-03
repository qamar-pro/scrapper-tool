"""
Event Discovery & Tracking Tool
Main entry point
"""

import argparse
from typing import List

from src.utils.config import config
from src.utils.logger import setup_logger
from src.scrapers.district_scraper import DistrictScraper
from src.storage.excel_storage import ExcelStorage


logger = setup_logger(
    "event_discovery",
    config.LOG_FILE,
    config.LOG_LEVEL,
    config.LOG_MAX_SIZE,
    config.LOG_BACKUP_COUNT,
)


def get_storage():
    """Return storage backend based on config"""
    storage_type = (config.STORAGE_TYPE or "excel").lower()
    if storage_type == "excel":
        return ExcelStorage()
    if storage_type == "google_sheets":
        from src.storage.google_sheets_storage import GoogleSheetsStorage
        return GoogleSheetsStorage()

    logger.warning(f"Unknown storage type '{storage_type}', defaulting to Excel")
    return ExcelStorage()


def get_scrapers(city: str, platforms: List[str]):
    """Create scrapers for the requested platforms"""
    mapping = {
        "district": DistrictScraper,
    }
    scrapers = []
    for platform in platforms:
        key = platform.strip().lower()
        scraper_cls = mapping.get(key)
        if not scraper_cls:
            logger.warning(f"Unsupported platform '{platform}' - skipping")
            continue
        scrapers.append(scraper_cls(city))
    return scrapers


def run_once(city: str, platforms: List[str] = None) -> int:
    """
    Run a single scrape + store cycle

    Returns:
        Number of events scraped
    """
    if platforms is None:
        platforms = config.PLATFORMS

    if not config.validate_city(city):
        logger.warning(f"City '{city}' not in supported list: {config.SUPPORTED_CITIES}")

    logger.info(f"Starting run for city={city}, platforms={platforms}")
    events = []

    for scraper in get_scrapers(city, platforms):
        events.extend(scraper.scrape())

    if not events:
        logger.warning("No events scraped")
        return 0

    storage = get_storage()
    if storage.save_events(events):
        storage.mark_expired_events()
        logger.info(f"Stored {len(events)} events")
        return len(events)

    logger.error("Failed to save events")
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Event Discovery & Tracking Tool")
    parser.add_argument("--city", help="City to scrape", default=config.DEFAULT_CITY)
    parser.add_argument(
        "--platforms",
        help="Comma-separated platforms to scrape (bookmyshow,district)",
        default=",".join(config.PLATFORMS),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    run_once(args.city, platforms)
