import httpx
from automations.base import BaseAutomation
from vesta.formatter import make_board
from config import WEATHER_LAT, WEATHER_LON, WEATHER_SCHEDULE

# WMO weather interpretation codes → display string
_WMO_CONDITIONS = {
    0: "CLEAR",
    1: "CLEAR", 2: "PARTLY CLOUDY", 3: "OVERCAST",
    45: "FOGGY", 48: "FOGGY",
    51: "DRIZZLE", 53: "DRIZZLE", 55: "DRIZZLE",
    61: "RAIN", 63: "RAIN", 65: "HEAVY RAIN",
    71: "SNOW", 73: "SNOW", 75: "HEAVY SNOW",
    77: "SNOW",
    80: "SHOWERS", 81: "SHOWERS", 82: "HEAVY SHOWERS",
    85: "SNOW SHOWERS", 86: "SNOW SHOWERS",
    95: "THUNDERSTORM", 96: "THUNDERSTORM", 99: "THUNDERSTORM",
}


class WeatherAutomation(BaseAutomation):
    name = "weather"
    schedule = WEATHER_SCHEDULE

    async def run(self) -> list[list[int]]:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={WEATHER_LAT}&longitude={WEATHER_LON}"
            "&current=temperature_2m,weathercode"
            "&daily=temperature_2m_max,temperature_2m_min"
            "&temperature_unit=fahrenheit"
            "&forecast_days=1"
            "&timezone=auto"
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

        current = data["current"]
        daily = data["daily"]

        temp = round(current["temperature_2m"])
        code = current.get("weathercode", current.get("weather_code", 0))
        condition = _WMO_CONDITIONS.get(code, "UNKNOWN")
        hi = round(daily["temperature_2m_max"][0])
        lo = round(daily["temperature_2m_min"][0])

        lines = [
            condition,
            f"{temp}°F",
            f"HI {hi}  LO {lo}",
        ]
        return make_board(lines, valign="center")
