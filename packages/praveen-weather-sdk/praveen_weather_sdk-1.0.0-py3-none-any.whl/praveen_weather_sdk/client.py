import requests

class WeatherClient:
    def __init__(self, api_key, base_url="https://api.openweathermap.org/data/2.5"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get_current_weather(self, city, units="metric"):
        """
        Get current weather data for a city.
        """
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        resp = self.session.get(url, params=params)
        self._handle_response(resp)
        return resp.json()

    def get_forecast(self, city, units="metric"):
        """
        Get 5-day / 3-hour forecast data for a city.
        """
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        resp = self.session.get(url, params=params)
        self._handle_response(resp)
        return resp.json()

    def _handle_response(self, resp):
        if not resp.ok:
            raise Exception(f"API Error {resp.status_code}: {resp.text}")
