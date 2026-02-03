# Event Discovery & Tracking Tool

A production-ready Python application for discovering and tracking events from the District platform for photobooth installation opportunities.

## 🎯 Features

- **Platform Scraping**: Extract event data from District
- **City Selection**: Filter events by specific cities
- **Automated Scheduling**: Run at regular intervals using cron/scheduler
- **Excel/Google Sheets Integration**: Store and update data seamlessly
- **Smart Deduplication**: Prevent duplicate entries
- **Event Status Tracking**: Automatically mark expired/past events
- **Error Handling**: Robust error handling and logging
- **Scalable Architecture**: Modular design for easy maintenance

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Google Cloud Account (for Google Sheets integration - optional)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/event-discovery-tool.git
cd event-discovery-tool
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# City Configuration
DEFAULT_CITY=Mumbai

# Storage Configuration
STORAGE_TYPE=excel  # Options: excel, google_sheets
EXCEL_FILE_PATH=data/events.xlsx

# Google Sheets Configuration (if using Google Sheets)
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json

# Scraping Configuration
SCRAPE_INTERVAL_HOURS=24
MAX_RETRIES=3
REQUEST_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 5. Run the Application

```bash
# One-time execution
python main.py

# With specific city
python main.py --city Mumbai

# Run scheduler (continuous mode)
python scheduler.py
```

## 📁 Project Structure

```
event-discovery-tool/
│
├── src/
│   ├── __init__.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── bookmyshow_scraper.py
│   │   └── district_scraper.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── base_storage.py
│   │   ├── excel_storage.py
│   │   └── google_sheets_storage.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── event.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── config.py
│       └── helpers.py
│
├── data/
│   ├── .gitkeep
│   └── events.xlsx (generated)
│
├── logs/
│   ├── .gitkeep
│   └── app.log (generated)
│
├── tests/
│   ├── __init__.py
│   ├── test_scrapers.py
│   └── test_storage.py
│
├── .env.example
├── .env (create this)
├── .gitignore
├── requirements.txt
├── main.py
├── scheduler.py
├── README.md
├── GITHUB_SETUP.md
└── setup.py
```

## 🔧 Configuration Options

### City Selection

Supported cities:
- Mumbai
- Delhi
- Bangalore
- Hyderabad
- Chennai
- Pune
- Kolkata

Add cities in `src/utils/config.py`

### Storage Types

**Excel (Default)**
- Simple setup
- No external dependencies
- File-based storage

**Google Sheets**
- Real-time collaboration
- Cloud-based
- Requires Google Cloud setup

## 📊 Data Fields Collected

| Field | Description |
|-------|-------------|
| Event Name | Name of the event |
| Date | Event date and time |
| Venue | Event location/venue |
| City | City where event is held |
| Category | Event category (Music, Comedy, etc.) |
| URL | Link to event page |
| Status | Active/Expired/Updated |
| Last Updated | Timestamp of last update |
| Source | Platform (District) |

## ⚙️ Automation

### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 2 AM)
4. Action: Start a program
5. Program: `C:\Users\Dell\Music\intern_project\venv\Scripts\python.exe`
6. Arguments: `C:\Users\Dell\Music\intern_project\main.py`

### Using Cron (Linux/Mac)

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/event-discovery-tool && /path/to/venv/bin/python main.py

# Run every 6 hours
0 */6 * * * cd /path/to/event-discovery-tool && /path/to/venv/bin/python main.py
```

### Using Built-in Scheduler

```bash
python scheduler.py
```

The scheduler runs continuously and executes scraping at configured intervals.

## 🛡️ Error Handling

The application includes:
- Retry mechanism for failed requests
- Graceful handling of site structure changes
- Comprehensive logging
- Exception handling for network issues
- Data validation before storage

## 📈 Scalability Features

- **Modular Design**: Easy to add new scrapers
- **Configurable**: All settings in config files
- **Extensible**: Plugin architecture for storage backends
- **Rate Limiting**: Prevents overwhelming target sites
- **Async Support**: Ready for concurrent scraping

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test
python -m pytest tests/test_scrapers.py
```

## 📝 Logging

Logs are stored in `logs/app.log` with the following levels:
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- DEBUG: Detailed debugging information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For issues or questions:
- Create an issue on GitHub
- Email: your-email@example.com

## 🎯 Roadmap

- [ ] Add more event platforms
- [ ] Implement email notifications
- [ ] Add web dashboard
- [ ] Mobile app integration
- [ ] ML-based event recommendations
- [ ] API endpoints for integration

## 📚 Documentation

For detailed documentation, see:
- [GitHub Setup Guide](GITHUB_SETUP.md)
- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

---

**Built with ❤️ for Pixie - Making photobooth placement smarter**
