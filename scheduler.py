"""
Scheduler for periodic scraping
"""

import argparse
import time

import schedule

from src.utils.config import config
from src.utils.logger import setup_logger
from main import run_once


logger = setup_logger(
    "event_discovery_scheduler",
    config.LOG_FILE,
    config.LOG_LEVEL,
    config.LOG_MAX_SIZE,
    config.LOG_BACKUP_COUNT,
)


def run_job(city: str, platforms):
    logger.info("Running scheduled job")
    run_once(city, platforms)


def parse_args():
    parser = argparse.ArgumentParser(description="Event Discovery Scheduler")
    parser.add_argument("--city", help="City to scrape", default=config.DEFAULT_CITY)
    parser.add_argument(
        "--platforms",
        help="Comma-separated platforms to scrape (bookmyshow,district)",
        default=",".join(config.PLATFORMS),
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=config.SCRAPE_INTERVAL_HOURS,
        help="Interval in hours between runs",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    interval_hours = max(1, int(args.interval_hours))

    schedule.every(interval_hours).hours.do(run_job, args.city, platforms)
    logger.info(
        f"Scheduler started: city={args.city}, platforms={platforms}, interval_hours={interval_hours}"
    )

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
