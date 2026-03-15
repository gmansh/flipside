import httpx
from automations.base import BaseAutomation
from vesta.formatter import blank_board, center_line
from vesta.character_codes import BLANK, YELLOW, WHITE, BLUE
from config import BOARD_ROWS, WEATHER_LAT, WEATHER_LON, WEATHER_SCHEDULE

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

# --- Weather icons (5 wide × 4 tall, using character codes) ---
_ = BLANK
Y = YELLOW
W = WHITE
B = BLUE

ICON_SUN = (
    (Y, _, _, Y, _, _, Y),
    (_, Y, Y, Y, Y, Y, _),
    (Y, Y, Y, Y, Y, Y, Y),
    (Y, Y, Y, Y, Y, Y, Y),
    (_, Y, Y, Y, Y, Y, _),
    (Y, _, _, Y, _, _, Y),
)

ICON_CLOUD = (
    (_, _, W, W, W, _, _),
    (_, W, W, W, W, W, _),
    (W, W, W, W, W, W, W),
    (_, _, _, _, _, _, _),
)

ICON_PARTLY_CLOUDY = (
    (_, Y, Y, Y, _, _, _),
    (Y, Y, Y, W, W, _, _),
    (_, _, W, W, W, W, W),
    (_, _, _, _, _, _, _),
)

ICON_RAIN = (
    (_, _, W, W, W, _, _),
    (_, W, W, W, W, W, _),
    (W, _, B, _, B, _, B),
    (_, B, _, B, _, B, _),
)

ICON_SNOW = (
    (_, _, W, W, W, _, _),
    (_, W, W, W, W, W, _),
    (W, _, W, _, W, _, W),
    (_, W, _, W, _, W, _),
)

ICON_THUNDERSTORM = (
    (_, _, W, W, W, _, _),
    (_, W, W, W, W, W, _),
    (W, _, _, Y, Y, _, _),
    (_, _, Y, Y, _, _, _),
)

# Map condition strings to icons
_CONDITION_ICONS = {
    "CLEAR": ICON_SUN,
    "PARTLY CLOUDY": ICON_PARTLY_CLOUDY,
    "OVERCAST": ICON_CLOUD,
    "FOGGY": ICON_CLOUD,
    "DRIZZLE": ICON_RAIN,
    "RAIN": ICON_RAIN,
    "HEAVY RAIN": ICON_RAIN,
    "SHOWERS": ICON_RAIN,
    "HEAVY SHOWERS": ICON_RAIN,
    "SNOW": ICON_SNOW,
    "HEAVY SNOW": ICON_SNOW,
    "SNOW SHOWERS": ICON_SNOW,
    "THUNDERSTORM": ICON_THUNDERSTORM,
}

# Layout constants
_TEXT_COLS = 14   # columns 0-13 for text
_ICON_COL = 15   # icon starts at column 15 (7 wide → cols 15-21)


class WeatherAutomation(BaseAutomation):
    name = "weather"

    def __init__(self):
        self.schedule = WEATHER_SCHEDULE
        self.latitude = WEATHER_LAT
        self.longitude = WEATHER_LON

    def get_param_schema(self) -> list[dict]:
        return [
            {"key": "schedule", "label": "Schedule (cron)", "type": "cron", "value": self.schedule},
            {"key": "latitude", "label": "Latitude", "type": "number", "value": self.latitude},
            {"key": "longitude", "label": "Longitude", "type": "number", "value": self.longitude},
        ]

    def get_params(self) -> dict:
        return {
            "schedule": self.schedule,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def set_params(self, params: dict) -> None:
        if "schedule" in params:
            self.schedule = str(params["schedule"])
        if "latitude" in params:
            self.latitude = float(params["latitude"])
        if "longitude" in params:
            self.longitude = float(params["longitude"])

    async def run(self) -> list[list[int]]:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.latitude}&longitude={self.longitude}"
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
        icon = _CONDITION_ICONS.get(condition, ICON_SUN)

        return _compose_board(lines, icon)


def _compose_board(lines: list[str], icon: list[list[int]]) -> list[list[int]]:
    """Build a board with text centered on the left and an icon on the right."""
    board = blank_board()

    # Place text lines (vertically centered, horizontally centered within left region)
    n = min(len(lines), BOARD_ROWS)
    text_start_row = (BOARD_ROWS - n) // 2
    for i, line in enumerate(lines):
        row_codes = center_line(line, width=_TEXT_COLS)
        board[text_start_row + i][:_TEXT_COLS] = row_codes

    # Place icon (vertically centered)
    icon_rows = len(icon)
    icon_start_row = (BOARD_ROWS - icon_rows) // 2
    for i, icon_row in enumerate(icon):
        for j, val in enumerate(icon_row):
            board[icon_start_row + i][_ICON_COL + j] = val

    return board
