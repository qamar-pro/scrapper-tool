"""
Configuration Management
Loads and manages application configuration from environment variables
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv


class Config:
    """Application configuration class"""
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        # Load .env file
        load_dotenv()
        
        # Project paths
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.LOGS_DIR = self.BASE_DIR / 'logs'
        
        # Ensure directories exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
        
        # City configuration
        self.DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'Mumbai')
        self.SUPPORTED_CITIES = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad',
            'Chennai', 'Pune', 'Kolkata', 'Ahmedabad',
            'Jaipur', 'Kochi'
        ]
        
        # Storage configuration
        self.STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'excel')
        self.EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'data/events.xlsx')
        if not Path(self.EXCEL_FILE_PATH).is_absolute():
            self.EXCEL_FILE_PATH = str(self.BASE_DIR / self.EXCEL_FILE_PATH)
        
        # Google Sheets configuration
        self.GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
        self.GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        
        # Scraping configuration
        self.SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 24))
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
        self.USER_AGENT = os.getenv(
            'USER_AGENT',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Platforms
        platforms_str = os.getenv('PLATFORMS', 'district')
        self.PLATFORMS = [p.strip() for p in platforms_str.split(',')]
        
        # Rate limiting
        self.RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', 2))
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 5))
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
        if not Path(self.LOG_FILE).is_absolute():
            self.LOG_FILE = str(self.BASE_DIR / self.LOG_FILE)
        self.LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
        
        # Event expiry
        self.MARK_EXPIRED_DAYS = int(os.getenv('MARK_EXPIRED_DAYS', 0))
        self.REMOVE_EXPIRED_DAYS = int(os.getenv('REMOVE_EXPIRED_DAYS', 30))
        
        # Email notifications
        self.ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        self.EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
        self.EMAIL_FROM = os.getenv('EMAIL_FROM', '')
        self.EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
        self.EMAIL_TO = os.getenv('EMAIL_TO', '')
    
    def get_city_url_mapping(self, platform: str) -> dict:
        """Get city URL mappings for different platforms"""
        mappings = {
            'district': {
                'Mumbai': 'https://www.district.in/',
                'Delhi': 'https://www.district.in/',
                'Bangalore': 'https://www.district.in/',
            }
        }
        return mappings.get(platform, {})
    
    def validate_city(self, city: str) -> bool:
        """Validate if city is supported"""
        return city in self.SUPPORTED_CITIES
    
    def get_storage_path(self) -> str:
        """Get appropriate storage path based on storage type"""
        if self.STORAGE_TYPE == 'excel':
            return self.EXCEL_FILE_PATH
        elif self.STORAGE_TYPE == 'google_sheets':
            return self.GOOGLE_SHEETS_ID
        return self.EXCEL_FILE_PATH
    
    def __str__(self) -> str:
        """String representation of config"""
        return f"Config(city={self.DEFAULT_CITY}, storage={self.STORAGE_TYPE})"


# Global config instance
config = Config()
