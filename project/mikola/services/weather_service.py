from __future__ import annotations

import os
from typing import Any, Dict
import requests
from flask import current_app


class WeatherService:
    def __init__(self) -> None:
        self._api = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str, country: str) -> Dict[str, Any]:
        api_key = current_app.config.get("OPENWEATHER_API_KEY", "")
        if not api_key:
            return self._mock(city, country)
        params = {"q": f"{city},{country}", "appid": api_key, "units": "metric", "lang": "ru"}
        try:
            r = requests.get(self._api, params=params, timeout=6)
            r.raise_for_status()
            data = r.json()
            return {
                "temp": data.get("main", {}).get("temp"),
                "description": (data.get("weather") or [{}])[0].get("description", ""),
                "icon": (data.get("weather") or [{}])[0].get("icon", "01d"),
            }
        except Exception:
            return self._mock(city, country)

    @staticmethod
    def is_ok_for_elderly_mountain(weather: Dict[str, Any]) -> bool:
        temp = weather.get("temp")
        description = weather.get("description", "")
        if temp is None:
            return False
        return temp >= 10 and all(word not in description.lower() for word in ["дожд", "снег", "бур"])

    @staticmethod
    def _mock(city: str, country: str) -> Dict[str, Any]:
        return {"temp": 15, "description": "ясно", "icon": "01d"}


weather_service = WeatherService()

