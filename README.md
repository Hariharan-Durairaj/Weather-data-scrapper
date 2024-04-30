# Weather-data-scrapper
This Python script retrieves weather data from a The weather channel, using BeautifulSoup and Selenium. By copying the URL of any place, and passing it to the function will retrieve all the weather data from that web page

## Prerequisites

- Python 3.x
- Selenium
- BeautifulSoup
- Chrome Web Browser
- ChromeDriver

## Installation

1. Install Python 3.x from the [official website](https://www.python.org/downloads/).
2. Install Selenium using pip:
   ```
   pip install selenium
   ```
3. Install BeautifulSoup using pip:
   ```
   pip install beautifulsoup4
   ```
4. Download ChromeDriver compatible with your Chrome browser version from the [official website](https://www.google.com.au/intl/en_au/chrome/).
5. Ensure ChromeDriver is in your system PATH or place it in the same directory as the script.

## Usage

1. Import the required libraries:
   ```python
   from bs4 import BeautifulSoup as BS
   from selenium import webdriver
   import pandas as pd
   import time
   import html
   import re
   from unicodedata import normalize
   import warnings
   ```

2. Run the script using Python:
   ```bash
   python weather_scraper.py
   ```

3. If you want to scrape weather data for a specific place:
   - Go to "The Weather Channel" website (https://weather.com).
   - Search for the desired place using the search bar.
   - Copy the URL of the search results page.
   - Pass the copied URL as an argument to the `collect_weather_data` function in the script.

## Configuration

- The default URL for weather data is set to "https://weather.com/en-IN/weather/today/l/ba484457443c15089496e4a694f025f897b92bdbad047a2a796d641205d69e10". You can change this URL in the `collect_weather_data` function to scrape data from different sources.

- Chrome options are configured for headless browsing. If you want to run the script in a visible browser window, remove the `--headless` option from `chrome_options`.

## Author

Hariharan Durairaj
