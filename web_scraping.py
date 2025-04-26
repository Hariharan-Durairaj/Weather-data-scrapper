from WeatherScraper import WeatherScraper

# Initialize with one or more URLs
urls = [
    "https://weather.com/weather/today/l/Adelaide+South+Australia+Australia?canonicalCityId=68f2eea40d2687e6aab81cac850af9ae6c66f7fc05f4aa80726f72f72554c483"
]
scraper = WeatherScraper(urls)

# Scrape once
scraper.scrape()

# Or scrape continuously
scraper.start_scraping(interval=600, duration=1800)

# Export collected data
scraper.to_csv('weather_log.csv')