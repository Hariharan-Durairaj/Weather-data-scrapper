from bs4 import BeautifulSoup as BS
import re
import requests
import pandas as pd
import time
from datetime import datetime

class WeatherScraper:
    def __init__(self, url):
        if isinstance(url, str):
            self.urls = [url]
        elif isinstance(url, list):
            self.urls = url
        else:
            raise ValueError("URLs should be a string or list of strings.")
        self.data = []

    def _match_degree(self, degree):
        if degree is None:
            return None
        if re.match(r'^[0-9.]+\°$', degree):
            return float(degree[:-1])
        if '--' in degree:
            return None
        return "dnm:" + degree

    def _extract_text(self, selector, attr_dict):
        el = selector.find("span", attrs=attr_dict)
        return el.get_text() if el else None

    def _location(self, soup):
        match = re.search(r'"(styles--locationName--.*?)"', str(soup))
        if match:
            return soup.find("span", attrs={'class': match[1]}).get_text()
        return None

    def _weather_time(self, soup):
        match = re.search(r'"CurrentConditions--timestamp.*?"', str(soup))
        if match:
            time_el = soup.find("span", attrs={'class': match[0][1:-1]})
            if time_el:
                time_text = time_el.get_text()
                time_match = re.search(r'[0-9]+:[0-9]+ ?(am|pm)? ?[A-Z]*', time_text)
                if time_match:
                    return time_match[0]
        return None

    def _temperature(self, section):
        match = re.search(r'"TodayDetailsCard--feelsLikeTempValue.*?"', str(section))
        if match:
            temp = section.find("span", attrs={'class': match[0][1:-1]})
            return self._match_degree(temp.get_text()) if temp else None
        return None

    def _high_low_dew(self, section):
        match = re.search(r'"WeatherDetailsListItem--wxData.*?"', str(section))
        weather_details = section.find_all("div", attrs={'class': match[0][1:-1]}) if match else []

        high, low, dew = None, None, None
        if weather_details:
            temps = weather_details[0].find_all("span", attrs={'data-testid': "TemperatureValue"})
            if temps and len(temps) >= 2:
                high = self._match_degree(temps[0].get_text())
                low = self._match_degree(temps[1].get_text())
            for detail in weather_details[1:]:
                temp = detail.find("span", attrs={'data-testid': "TemperatureValue"})
                if temp:
                    dew = self._match_degree(temp.get_text())
        return high, low, dew

    def _wind_speed(self, section):
        wind = self._extract_text(section, {'data-testid': "Wind"}).strip()
        if wind and re.match(r'.*[0-9.]+.*?(km\/h|mph)?', wind):
            match = re.search(r'([0-9.]+).*?(mph|km/h)', wind)
            if match:
                return match[1] + " " + match[2]
            else:
                return "dnm:" + wind
        return wind

    def _humidity(self, section):
        humidity = self._extract_text(section, {'data-testid': "PercentageValue"})
        if humidity and re.match(r'^[0-9.]+\%$', humidity):
            return float(humidity.strip('%'))
        return humidity

    def _pressure(self, section):
        pressure = self._extract_text(section, {'data-testid': "PressureValue"}).strip()
        if pressure and re.match(r'.*?[0-9.]+.*(mb|in).*', pressure):
            match = re.search(r'([0-9.]+).*?(mb|in)', pressure)
            if match:
                return match[1] + " " + match[2]
        return pressure

    def _uv_index(self, section):
        uv = self._extract_text(section, {'data-testid': "UVIndexValue"})
        if uv:
            if re.match(r'^[0-9.]+.*of.*[0-9.]+$', uv):
                m = re.search(r'([0-9.]+).*of.*?([0-9.]+)', uv)
                return float(m[1]), int(m[2])
            if uv.lower() == "extreme":
                return 11, 11
        return None, None

    def _visibility(self, section):
        vis = self._extract_text(section, {'data-testid': "VisibilityValue"})
        if vis and re.match(r'^[0-9.]+.*(km|mi)$', vis):
            match = re.search(r'([0-9.]+).*?(km|mi)', vis)
            if match:
                return match[1] + " " + match[2]
        return vis

    def _cloud(self, soup):
        cloud = soup.find("div", attrs={"data-testid": "wxPhrase"})
        return cloud.get_text() if cloud else None

    def _wind_direction(self, section):
        wind_dir = section.find("svg", attrs={'aria-label': 'arrow', 'name': 'arrow'})
        if wind_dir and 'style' in wind_dir.attrs:
            deg = int(re.search(r"[0-9.]+", wind_dir['style'])[0])
            directions = ["south", "south west", "west", "north west", "north", "north east", "east", "south east", "south"]
            return directions[int((deg + 22.5) % 360 // 45)]
        return None

    def scrape(self):
        all_weather = []
        for url in self.urls:
            if re.search(r'https://weather.com/.*?weather/today/', url) is None:
                raise ValueError(f"Invalid URL: {url}. Must be from the 'today' section of weather.com")
            try:
                response = requests.get(url)
            except Exception as e:
                raise ConnectionError(f"Request failed for {url}: {e}")

            if response.status_code != 200:
                raise ConnectionError(f"Failed to fetch {url}. Status code: {response.status_code}")

            soup = BS(response.text, 'html.parser')
            section = soup.find('section', attrs={'data-testid': 'TodaysDetailsModule'})
            if section is None:
                raise ValueError(f"Could not find Today's Details section for {url}")

            high, low, dew = self._high_low_dew(section)
            index, index_of = self._uv_index(section)

            weather = {
                "timestamp": datetime.now(),
                "location": self._location(soup),
                "weather_time": self._weather_time(soup),
                "temperature": self._temperature(section),
                "high": high,
                "low": low,
                "dew_point": dew,
                "wind_speed": self._wind_speed(section),
                "humidity(%)": self._humidity(section),
                "pressure": self._pressure(section),
                "uv_index": index,
                "uv_index_out_of": index_of,
                "visibility": self._visibility(section),
                "cloud_condition": self._cloud(soup),
                "wind_direction": self._wind_direction(section),
                "source_url": url
            }

            all_weather.append(weather)
        self.data.extend(all_weather)
        return all_weather

    def start_scraping(self, interval=300, duration=3600):
        start_time = time.time()
        while (time.time() - start_time) <= duration:
            self.scrape()
            time.sleep(interval)
        return pd.DataFrame(self.data)

    def get_data(self):
        return pd.DataFrame(self.data)

    def to_csv(self, filepath='weather_data.csv'):
        df = self.get_data()
        if df.empty:
            raise ValueError("No data collected to save.")
        df.to_csv(filepath, index=False)
        return filepath
