"""
District Scraper
Scrapes event data from District platform
"""

from typing import List, Optional
from datetime import datetime
import re
import json

from src.scrapers.base_scraper import BaseScraper
from src.models.event import Event


class DistrictScraper(BaseScraper):
    """District event scraper"""
    
    def get_platform_name(self) -> str:
        """Return platform name"""
        return "District"
    
    def get_base_url(self) -> str:
        """Get District URL for city"""
        city_urls = self.config.get_city_url_mapping('district')
        return city_urls.get(self.city, '')
    
    def parse_events(self, html_content: str) -> List[Event]:
        """
        Parse events from District HTML
        
        Args:
            html_content: HTML content
        
        Returns:
            List of Event objects
        """
        events = []
        soup = self.get_soup(html_content)
        
        try:
            # District homepage lists event links; extract and visit each event page
            event_links = self._extract_event_links(soup)
            if not event_links:
                self.logger.warning("No event links found on District homepage")
                return []

            for link in event_links[:25]:  # Limit to 25 events
                try:
                    event_html = self.fetch_page(link)
                    if not event_html:
                        continue
                    event = self._parse_event_page(event_html, link)
                    if event and self.validate_event(event):
                        events.append(event)
                except Exception as e:
                    self.logger.debug(f"Error parsing District event page: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error parsing District events: {e}")
        
        return events
    
    def _extract_event_links(self, soup) -> List[str]:
        """Extract event page links from District homepage"""
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/events/' in href or '/event/' in href:
                if '/artist' in href:
                    continue
                if href.startswith('/'):
                    href = f"https://www.district.in{href}"
                if href.startswith('http'):
                    links.add(href.split('?')[0])
        return list(links)

    def _parse_event_page(self, html_content: str, url: str) -> Optional[Event]:
        """
        Extract event data from an event page
        
        Args:
            html_content: HTML content of event page
            url: Event URL
        
        Returns:
            Event object or None
        """
        try:
            soup = self.get_soup(html_content)
            event_name = "Unknown Event"
            event_date = "TBA"
            venue = "TBA"
            category = "General"

            # Prefer JSON-LD structured data if available
            json_ld = soup.find_all("script", type="application/ld+json")
            for script in json_ld:
                try:
                    data = json.loads(script.string or "{}")
                except Exception:
                    continue
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") == "Event":
                        event_name = item.get("name", event_name)
                        event_date = item.get("startDate", event_date)
                        category = item.get("eventType") or item.get("genre") or category
                        location = item.get("location", {})
                        if isinstance(location, dict):
                            venue = location.get("name") or venue
                            address = location.get("address", {})
                            if isinstance(address, dict):
                                city = address.get("addressLocality")
                                if city:
                                    venue = f"{venue} - {city}"
                        break

            if event_name == "Unknown Event":
                name_elem = soup.find('h1')
                event_name = name_elem.get_text(strip=True) if name_elem else event_name

            if event_date == "TBA":
                meta_date = soup.find("meta", property="event:start_date")
                if meta_date and meta_date.get("content"):
                    event_date = meta_date["content"]

            if venue == "TBA":
                meta_loc = soup.find("meta", property="event:location")
                if meta_loc and meta_loc.get("content"):
                    venue = meta_loc["content"]

            # Create Event object
            event = Event(
                event_name=event_name,
                date=event_date,
                venue=venue,
                city=self.city,
                category=category,
                url=url,
                source=self.get_platform_name(),
                status="Active",
                last_updated=datetime.now()
            )
            
            return event
            
        except Exception as e:
            self.logger.debug(f"Error extracting event data: {e}")
            return None
