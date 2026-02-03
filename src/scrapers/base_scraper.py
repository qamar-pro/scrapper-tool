"""
Base Scraper
Abstract base class for all event scrapers
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import time
from bs4 import BeautifulSoup

from src.models.event import Event
from src.utils.config import config
from src.utils.logger import setup_logger
from src.utils.helpers import retry_on_failure, make_request


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


class BaseScraper(ABC):
    """Abstract base scraper class"""
    
    def __init__(self, city: str):
        """
        Initialize scraper
        
        Args:
            city: City to scrape events for
        """
        self.city = city
        self.config = config
        self.logger = logger
        self.events: List[Event] = []
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name"""
        pass
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Return base URL for the city"""
        pass
    
    @abstractmethod
    def parse_events(self, html_content: str) -> List[Event]:
        """
        Parse events from HTML content
        
        Args:
            html_content: HTML content to parse
        
        Returns:
            List of Event objects
        """
        pass
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch page content with retry logic
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content or None
        """
        try:
            self.logger.info(f"Fetching: {url}")
            response = make_request(url, timeout=self.config.REQUEST_TIMEOUT)
            
            # Rate limiting
            time.sleep(self.config.RATE_LIMIT_DELAY)
            
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            raise
    
    def scrape(self) -> List[Event]:
        """
        Main scraping method
        
        Returns:
            List of scraped events
        """
        try:
            self.logger.info(f"Starting scrape for {self.city} on {self.get_platform_name()}")
            
            url = self.get_base_url()
            if not url:
                self.logger.warning(f"No URL configured for {self.city}")
                return []
            
            html_content = self.fetch_page(url)
            if not html_content:
                self.logger.warning(f"Failed to fetch content from {url}")
                return []
            
            self.events = self.parse_events(html_content)
            self.logger.info(f"Scraped {len(self.events)} events from {self.get_platform_name()}")
            
            return self.events
            
        except Exception as e:
            self.logger.error(f"Scraping failed for {self.get_platform_name()}: {e}")
            return []
    
    def get_soup(self, html_content: str) -> BeautifulSoup:
        """Create BeautifulSoup object from HTML"""
        return BeautifulSoup(html_content, 'lxml')
    
    def validate_event(self, event: Event) -> bool:
        """
        Validate event data
        
        Args:
            event: Event object to validate
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['event_name', 'date', 'venue', 'city', 'url']
        
        for field in required_fields:
            if not getattr(event, field, None):
                self.logger.warning(f"Event missing required field: {field}")
                return False
        
        return True
