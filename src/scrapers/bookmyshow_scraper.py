"""
BookMyShow Scraper
Scrapes event data from BookMyShow platform
"""

from typing import List, Optional
from datetime import datetime
import re
import time

from src.scrapers.base_scraper import BaseScraper
from src.models.event import Event


class BookMyShowScraper(BaseScraper):
    """BookMyShow event scraper"""
    
    def get_platform_name(self) -> str:
        """Return platform name"""
        return "BookMyShow"
    
    def get_base_url(self) -> str:
        """Get BookMyShow URL for city"""
        city_urls = self.config.get_city_url_mapping('bookmyshow')
        return city_urls.get(self.city, '')
    
    def parse_events(self, html_content: str) -> List[Event]:
        """
        Parse events from BookMyShow HTML
        
        Args:
            html_content: HTML content
        
        Returns:
            List of Event objects
        """
        events = []
        soup = self.get_soup(html_content)
        
        # Note: BookMyShow's structure changes frequently
        # This is a generic implementation that may need updates
        try:
            # Try to find event containers
            # BookMyShow uses various class names, adjust as needed
            event_containers = soup.find_all('div', class_=re.compile(r'.*event.*|.*card.*'))
            
            if not event_containers:
                # Fallback: try alternative selectors
                event_containers = soup.find_all('a', href=re.compile(r'/events/'))
            
            for container in event_containers[:50]:  # Limit to 50 events per scrape
                try:
                    event = self._extract_event_data(container)
                    if event and self.validate_event(event):
                        events.append(event)
                except Exception as e:
                    self.logger.debug(f"Error parsing event container: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing BookMyShow events: {e}")
        
        return events

    def scrape(self) -> List[Event]:
        """
        Override scrape to add Selenium fallback for 403 blocks
        """
        try:
            self.logger.info(f"Starting scrape for {self.city} on {self.get_platform_name()}")

            url = self.get_base_url()
            if not url:
                self.logger.warning(f"No URL configured for {self.city}")
                return []

            try:
                html_content = self.fetch_page(url)
            except Exception:
                self.logger.warning("Requests blocked, trying Selenium fallback")
                html_content = self._fetch_with_selenium(url)

            if not html_content:
                self.logger.warning(f"Failed to fetch content from {url}")
                return []

            self.events = self.parse_events(html_content)
            self.logger.info(f"Scraped {len(self.events)} events from {self.get_platform_name()}")

            return self.events

        except Exception as e:
            self.logger.error(f"Scraping failed for {self.get_platform_name()}: {e}")
            return []
    
    def _extract_event_data(self, container) -> Optional[Event]:
        """
        Extract event data from container
        
        Args:
            container: BeautifulSoup element containing event data
        
        Returns:
            Event object or None
        """
        try:
            # Extract event name
            name_elem = container.find(['h3', 'h4', 'h5'], class_=re.compile(r'.*title.*|.*name.*'))
            if not name_elem:
                name_elem = container.find('a')
            event_name = name_elem.get_text(strip=True) if name_elem else "Unknown Event"
            
            # Extract URL
            url_elem = container.find('a', href=True)
            event_url = url_elem['href'] if url_elem else ""
            if event_url and not event_url.startswith('http'):
                event_url = f"https://in.bookmyshow.com{event_url}"
            
            # Extract date (various formats possible)
            date_elem = container.find(['span', 'div', 'p'], class_=re.compile(r'.*date.*|.*time.*'))
            event_date = date_elem.get_text(strip=True) if date_elem else "TBA"
            
            # Extract venue
            venue_elem = container.find(['span', 'div', 'p'], class_=re.compile(r'.*venue.*|.*location.*'))
            venue = venue_elem.get_text(strip=True) if venue_elem else "TBA"
            
            # Extract category
            category_elem = container.find(['span', 'div'], class_=re.compile(r'.*category.*|.*genre.*'))
            category = category_elem.get_text(strip=True) if category_elem else "General"
            
            # Create Event object
            event = Event(
                event_name=event_name,
                date=event_date,
                venue=venue,
                city=self.city,
                category=category,
                url=event_url,
                source=self.get_platform_name(),
                status="Active",
                last_updated=datetime.now()
            )
            
            return event
            
        except Exception as e:
            self.logger.debug(f"Error extracting event data: {e}")
            return None

    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """Fetch page content using Selenium (headless Chrome)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            try:
                driver.get(url)
                time.sleep(5)
                return driver.page_source
            finally:
                driver.quit()
        except Exception as e:
            self.logger.error(f"Selenium fetch failed: {e}")
            return None
