import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from automations.weather import WeatherAutomation, _WMO_CONDITIONS
from config import BOARD_ROWS, BOARD_COLS


def _make_api_response(temp=72.3, weather_code=0, hi=80.1, lo=60.9):
    return {
        "current": {
            "temperature_2m": temp,
            "weathercode": weather_code,
        },
        "daily": {
            "temperature_2m_max": [hi],
            "temperature_2m_min": [lo],
        },
    }


@pytest.fixture
def mock_httpx():
    """Mock httpx.AsyncClient to return a weather response."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = _make_api_response()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("automations.weather.httpx.AsyncClient", return_value=mock_client) as m:
        yield mock_resp


class TestWeatherAutomation:
    def test_name_and_schedule(self):
        w = WeatherAutomation()
        assert w.name == "weather"
        assert w.schedule  # has a schedule

    @pytest.mark.asyncio
    async def test_run_returns_valid_board(self, mock_httpx):
        w = WeatherAutomation()
        board = await w.run()
        assert len(board) == BOARD_ROWS
        assert all(len(row) == BOARD_COLS for row in board)

    @pytest.mark.asyncio
    async def test_run_with_clear_weather(self, mock_httpx):
        mock_httpx.json.return_value = _make_api_response(weather_code=0)
        w = WeatherAutomation()
        board = await w.run()
        assert len(board) == BOARD_ROWS

    @pytest.mark.asyncio
    async def test_run_with_rain(self, mock_httpx):
        mock_httpx.json.return_value = _make_api_response(weather_code=61)
        w = WeatherAutomation()
        board = await w.run()
        assert len(board) == BOARD_ROWS

    @pytest.mark.asyncio
    async def test_run_with_unknown_code(self, mock_httpx):
        mock_httpx.json.return_value = _make_api_response(weather_code=999)
        w = WeatherAutomation()
        board = await w.run()
        assert len(board) == BOARD_ROWS

    @pytest.mark.asyncio
    async def test_alternate_weather_code_key(self, mock_httpx):
        """API sometimes uses weather_code instead of weathercode."""
        mock_httpx.json.return_value = {
            "current": {
                "temperature_2m": 68.0,
                "weather_code": 3,
            },
            "daily": {
                "temperature_2m_max": [75.0],
                "temperature_2m_min": [55.0],
            },
        }
        w = WeatherAutomation()
        board = await w.run()
        assert len(board) == BOARD_ROWS


class TestWMOConditions:
    def test_clear(self):
        assert _WMO_CONDITIONS[0] == "CLEAR"

    def test_rain(self):
        assert _WMO_CONDITIONS[61] == "RAIN"

    def test_snow(self):
        assert _WMO_CONDITIONS[71] == "SNOW"

    def test_thunderstorm(self):
        assert _WMO_CONDITIONS[95] == "THUNDERSTORM"
