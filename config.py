from dotenv import load_dotenv
import os

load_dotenv()

VESTABOARD_LOCAL_IP = os.getenv("VESTABOARD_LOCAL_IP", "192.168.50.199")
VESTABOARD_LOCAL_API_KEY = os.getenv("VESTABOARD_LOCAL_API_KEY", "")
VESTABOARD_PORT = int(os.getenv("VESTABOARD_PORT", "7000"))
VESTABOARD_BASE_URL = f"http://{VESTABOARD_LOCAL_IP}:{VESTABOARD_PORT}"

BOARD_ROWS = int(os.getenv("BOARD_ROWS", "6"))
BOARD_COLS = int(os.getenv("BOARD_COLS", "22"))

WEATHER_LAT = float(os.getenv("WEATHER_LAT", "37.7749"))
WEATHER_LON = float(os.getenv("WEATHER_LON", "-122.4194"))
WEATHER_SCHEDULE = os.getenv("WEATHER_SCHEDULE", "0 7 * * *")
