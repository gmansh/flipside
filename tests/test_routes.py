import io
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from PIL import Image

from main import app
from config import BOARD_ROWS, BOARD_COLS
from automations.base import BaseAutomation
import quiet_time


def _blank_board():
    return [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]


class DummyAutomation(BaseAutomation):
    name = "test_auto"
    schedule = "0 8 * * *"

    async def run(self):
        return _blank_board()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_send():
    with patch("api.routes.client.send", return_value=True) as m:
        yield m


@pytest.fixture
def mock_send_fail():
    with patch("api.routes.client.send", return_value=False):
        yield


@pytest.fixture
def mock_send_animated():
    with patch("api.routes.client.send_animated", return_value=True) as m:
        yield m


@pytest.fixture
def mock_read():
    with patch("api.routes.client.read", return_value=_blank_board()) as m:
        yield m


@pytest.fixture
def tmp_templates(tmp_path):
    with patch("api.routes.TEMPLATES_DIR", tmp_path):
        yield tmp_path


@pytest.fixture
def mock_automations():
    auto = DummyAutomation()
    with (
        patch("api.routes.scheduler.get_automations", return_value={"test_auto": auto}),
        patch("api.routes.scheduler.get_jobs", return_value=[
            {"name": "test_auto", "next_run": "2026-01-01T08:00:00", "schedule": "0 8 * * *"}
        ]),
    ):
        yield


# --- Preview routes ---

class TestGetPreview:
    def test_returns_html(self, client, mock_read):
        resp = client.get("/api/preview")
        assert resp.status_code == 200
        data = resp.json()
        assert "html" in data
        assert "message" in data
        assert '<div class="sim-board">' in data["html"]

    def test_502_on_read_failure(self, client):
        with patch("api.routes.client.read", return_value=None):
            resp = client.get("/api/preview")
            assert resp.status_code == 502

    def test_color_block_rendered(self, client):
        board = _blank_board()
        board[0][0] = 63  # RED
        with patch("api.routes.client.read", return_value=board):
            resp = client.get("/api/preview")
            assert resp.status_code == 200
            assert "190" in resp.json()["html"]  # RED rgb component

    def test_character_rendered(self, client):
        board = _blank_board()
        board[0][0] = 1  # A
        with patch("api.routes.client.read", return_value=board):
            resp = client.get("/api/preview")
            assert resp.status_code == 200
            assert ">A</div>" in resp.json()["html"]


class TestPostPreview:
    def test_returns_html_without_sending(self, client):
        board = _blank_board()
        board[0][0] = 1  # A
        resp = client.post("/api/preview", json={"message": board})
        assert resp.status_code == 200
        data = resp.json()
        assert "html" in data
        assert ">A</div>" in data["html"]
        # Should NOT have a "message" key (not reading from device)
        assert "message" not in data

    def test_color_block(self, client):
        board = _blank_board()
        board[0][0] = 65  # YELLOW
        resp = client.post("/api/preview", json={"message": board})
        assert resp.status_code == 200
        assert "220" in resp.json()["html"]  # YELLOW rgb component


# --- Message routes ---

class TestGetMessage:
    def test_returns_board(self, client, mock_read):
        resp = client.get("/api/message")
        assert resp.status_code == 200
        assert resp.json()["message"] == _blank_board()

    def test_502_on_read_failure(self, client):
        with patch("api.routes.client.read", return_value=None):
            resp = client.get("/api/message")
            assert resp.status_code == 502


class TestPostMessage:
    def test_send_raw(self, client, mock_send):
        board = _blank_board()
        resp = client.post("/api/message", json={"message": board})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        mock_send.assert_called_once_with(board)

    def test_502_on_send_failure(self, client, mock_send_fail):
        resp = client.post("/api/message", json={"message": _blank_board()})
        assert resp.status_code == 502


class TestPostText:
    def test_send_text(self, client, mock_send):
        resp = client.post("/api/message/text", json={"text": "HELLO"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        board = data["board"]
        assert len(board) == BOARD_ROWS
        assert all(len(row) == BOARD_COLS for row in board)

    def test_send_text_with_valign(self, client, mock_send):
        resp = client.post("/api/message/text", json={"text": "HI", "valign": "top"})
        assert resp.status_code == 200
        board = resp.json()["board"]
        # First row should have content
        assert any(c != 0 for c in board[0])

    def test_502_on_failure(self, client, mock_send_fail):
        resp = client.post("/api/message/text", json={"text": "FAIL"})
        assert resp.status_code == 502


class TestPostImage:
    def _make_image_bytes(self):
        img = Image.new("RGB", (100, 50), (0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    def test_upload_image(self, client, mock_send):
        buf = self._make_image_bytes()
        resp = client.post("/api/message/image", files={"file": ("test.png", buf, "image/png")})
        assert resp.status_code == 200
        board = resp.json()["board"]
        assert len(board) == BOARD_ROWS
        assert all(len(row) == BOARD_COLS for row in board)

    def test_502_on_failure(self, client, mock_send_fail):
        buf = self._make_image_bytes()
        resp = client.post("/api/message/image", files={"file": ("test.png", buf, "image/png")})
        assert resp.status_code == 502


class TestPostAnimated:
    def test_send_animated(self, client, mock_send_animated):
        board = _blank_board()
        resp = client.post("/api/message/animated", json={
            "message": board,
            "strategy": "row",
            "step_interval_ms": 50,
            "step_size": 2,
        })
        assert resp.status_code == 200
        mock_send_animated.assert_called_once_with(
            board, strategy="row", step_interval_ms=50, step_size=2,
        )


# --- Automation routes ---

class TestAutomations:
    def test_list(self, client, mock_automations):
        resp = client.get("/api/automations")
        assert resp.status_code == 200
        jobs = resp.json()["automations"]
        assert len(jobs) == 1
        assert jobs[0]["name"] == "test_auto"

    def test_trigger(self, client, mock_automations, mock_send):
        resp = client.post("/api/automations/test_auto/trigger")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_trigger_404(self, client, mock_automations, mock_send):
        resp = client.post("/api/automations/nonexistent/trigger")
        assert resp.status_code == 404


# --- Template routes ---

class TestTemplates:
    def test_save_and_list(self, client, tmp_templates):
        board = _blank_board()
        resp = client.post("/api/templates", json={"name": "test1", "message": board})
        assert resp.status_code == 200

        resp = client.get("/api/templates")
        assert resp.status_code == 200
        templates = resp.json()["templates"]
        assert any(t["name"] == "test1" for t in templates)

    def test_delete(self, client, tmp_templates):
        board = _blank_board()
        client.post("/api/templates", json={"name": "todelete", "message": board})

        resp = client.delete("/api/templates/todelete")
        assert resp.status_code == 200

        resp = client.get("/api/templates")
        assert not any(t["name"] == "todelete" for t in resp.json()["templates"])

    def test_delete_404(self, client, tmp_templates):
        resp = client.delete("/api/templates/nonexistent")
        assert resp.status_code == 404

    def test_list_empty(self, client, tmp_templates):
        resp = client.get("/api/templates")
        assert resp.status_code == 200
        assert resp.json()["templates"] == []


# --- Quiet time routes ---

class TestQuietTime:
    def test_get_defaults(self, client):
        resp = client.get("/api/quiet-time")
        assert resp.status_code == 200
        data = resp.json()
        assert data["enabled"] is False
        assert data["start_hour"] == 22
        assert data["end_hour"] == 7

    def test_put_enable(self, client):
        resp = client.put("/api/quiet-time", json={"enabled": True})
        assert resp.status_code == 200
        assert resp.json()["enabled"] is True

    def test_put_hours(self, client):
        resp = client.put("/api/quiet-time", json={"start_hour": 23, "end_hour": 6})
        assert resp.status_code == 200
        assert resp.json()["start_hour"] == 23
        assert resp.json()["end_hour"] == 6

    def test_put_partial(self, client):
        resp = client.put("/api/quiet-time", json={"enabled": True})
        assert resp.status_code == 200
        # Hours should remain at defaults
        assert resp.json()["start_hour"] == 22

    def test_get_reflects_put(self, client):
        client.put("/api/quiet-time", json={"enabled": True, "start_hour": 20, "end_hour": 5})
        resp = client.get("/api/quiet-time")
        data = resp.json()
        assert data["enabled"] is True
        assert data["start_hour"] == 20
        assert data["end_hour"] == 5

    def test_trigger_blocked_during_quiet_time(self, client, mock_automations):
        with patch("api.routes.quiet_time.is_quiet", return_value=True):
            resp = client.post("/api/automations/test_auto/trigger")
            assert resp.status_code == 409

    def test_put_rejects_invalid_hours(self, client):
        resp = client.put("/api/quiet-time", json={"start_hour": 24})
        assert resp.status_code == 422
        resp = client.put("/api/quiet-time", json={"end_hour": -1})
        assert resp.status_code == 422

    def test_message_returns_409_during_quiet_time(self, client):
        with patch("api.routes.client.send", return_value=False), \
             patch("api.routes.quiet_time.is_quiet", return_value=True):
            resp = client.post("/api/message", json={"message": _blank_board()})
            assert resp.status_code == 409
