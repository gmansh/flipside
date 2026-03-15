import socket
import threading
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

import uvicorn
from config import BOARD_ROWS, BOARD_COLS


def pytest_collection_modifyitems(items):
    """Auto-mark all tests in this directory as e2e."""
    for item in items:
        if "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


def _free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _blank_board():
    return [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]


@pytest.fixture(scope="session")
def live_server():
    """Start the FastAPI app on a random port with mocked Vestaboard client."""
    port = _free_port()
    board_state = _blank_board()

    def mock_send(chars):
        nonlocal board_state
        board_state = chars
        return True

    def mock_send_animated(chars, **kwargs):
        nonlocal board_state
        board_state = chars
        return True

    def mock_read():
        return board_state

    # Mock weather API response so E2E tests don't hit the network
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "current": {"temperature_2m": 72.3, "weathercode": 0},
        "daily": {"temperature_2m_max": [80.1], "temperature_2m_min": [60.9]},
    }
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_resp
    mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
    mock_http_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("vesta.client.send", side_effect=mock_send),
        patch("vesta.client.send_animated", side_effect=mock_send_animated),
        patch("vesta.client.read", side_effect=mock_read),
        patch("automations.weather.httpx.AsyncClient", return_value=mock_http_client),
    ):
        config = uvicorn.Config("main:app", host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()

        # Wait for server to be ready
        import httpx
        for _ in range(50):
            try:
                resp = httpx.get(f"http://127.0.0.1:{port}/")
                if resp.status_code == 200:
                    break
            except httpx.ConnectError:
                import time
                time.sleep(0.1)

        yield type("Server", (), {"url": f"http://127.0.0.1:{port}", "port": port})()

        server.should_exit = True
        thread.join(timeout=3)


@pytest.fixture
def console_errors(page):
    """Collect JS console errors during a test."""
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    yield errors
