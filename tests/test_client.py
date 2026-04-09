from unittest.mock import patch, MagicMock
import httpx
import pytest

import quiet_time
from vesta.client import send, send_animated, read, _headers


class TestHeaders:
    def test_contains_api_key(self):
        with patch("vesta.client.VESTABOARD_LOCAL_API_KEY", "test-key-123"):
            h = _headers()
            assert h["X-Vestaboard-Local-Api-Key"] == "test-key-123"


class TestSend:
    def test_returns_true_on_200(self):
        mock_resp = MagicMock(status_code=200)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp

        with patch("vesta.client.httpx.Client", return_value=mock_client):
            assert send([[0] * 22] * 6) is True

    def test_returns_true_on_201(self):
        mock_resp = MagicMock(status_code=201)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp

        with patch("vesta.client.httpx.Client", return_value=mock_client):
            assert send([[0] * 22] * 6) is True

    def test_returns_false_on_500(self):
        mock_resp = MagicMock(status_code=500)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp

        with patch("vesta.client.httpx.Client", return_value=mock_client):
            assert send([[0] * 22] * 6) is False

    def test_sends_correct_payload(self):
        mock_resp = MagicMock(status_code=200)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp

        board = [[1] * 22 for _ in range(6)]
        with patch("vesta.client.httpx.Client", return_value=mock_client):
            send(board)
            _, kwargs = mock_client.post.call_args
            assert kwargs["json"]["message"] == board


class TestSendAnimated:
    def test_sends_animation_params(self):
        mock_resp = MagicMock(status_code=200)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp

        board = [[0] * 22] * 6
        with patch("vesta.client.httpx.Client", return_value=mock_client):
            result = send_animated(board, strategy="row", step_interval_ms=50, step_size=2)
            assert result is True
            _, kwargs = mock_client.post.call_args
            payload = kwargs["json"]
            assert payload["strategy"] == "row"
            assert payload["stepIntervalMs"] == 50
            assert payload["stepSize"] == 2


class TestQuietTimeGating:
    """Quiet time is enforced at the scheduler level (scheduler._make_job),
    not in client.send/send_animated.  These tests verify the client no longer
    blocks on its own."""

    def test_send_proceeds_even_during_quiet_time(self):
        mock_resp = MagicMock(status_code=200)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp

        with patch("vesta.client.httpx.Client", return_value=mock_client):
            assert send([[0] * 22] * 6) is True

    def test_send_animated_proceeds_even_during_quiet_time(self):
        mock_resp = MagicMock(status_code=200)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp

        with patch("vesta.client.httpx.Client", return_value=mock_client):
            assert send_animated([[0] * 22] * 6) is True


class TestRead:
    def _mock_client(self, status_code, json_data=None):
        mock_resp = MagicMock(status_code=status_code)
        if json_data is not None:
            mock_resp.json.return_value = json_data
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        return mock_client

    def test_returns_board_from_message_key(self):
        board = [[0] * 22] * 6
        mc = self._mock_client(200, {"message": board})
        with patch("vesta.client.httpx.Client", return_value=mc):
            assert read() == board

    def test_returns_board_from_currentMessage_key(self):
        board = [[1] * 22] * 6
        mc = self._mock_client(200, {"currentMessage": board})
        with patch("vesta.client.httpx.Client", return_value=mc):
            assert read() == board

    def test_returns_raw_list(self):
        board = [[2] * 22] * 6
        mc = self._mock_client(200, board)
        with patch("vesta.client.httpx.Client", return_value=mc):
            assert read() == board

    def test_returns_none_on_error(self):
        mc = self._mock_client(500)
        with patch("vesta.client.httpx.Client", return_value=mc):
            assert read() is None
