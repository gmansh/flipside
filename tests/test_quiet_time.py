from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

import quiet_time


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset quiet time state before each test."""
    quiet_time._settings.update({"enabled": False, "start_hour": 22, "end_hour": 7})
    yield


class TestGetSettings:
    def test_returns_defaults(self):
        s = quiet_time.get_settings()
        assert s == {"enabled": False, "start_hour": 22, "end_hour": 7}

    def test_returns_copy(self):
        s = quiet_time.get_settings()
        s["enabled"] = True
        assert quiet_time.get_settings()["enabled"] is False


class TestUpdateSettings:
    def test_update_enabled(self):
        result = quiet_time.update_settings(enabled=True)
        assert result["enabled"] is True
        assert quiet_time.get_settings()["enabled"] is True

    def test_update_hours(self):
        result = quiet_time.update_settings(start_hour=23, end_hour=6)
        assert result["start_hour"] == 23
        assert result["end_hour"] == 6

    def test_partial_update(self):
        quiet_time.update_settings(start_hour=20)
        s = quiet_time.get_settings()
        assert s["start_hour"] == 20
        assert s["end_hour"] == 7  # unchanged

    def test_returns_updated_settings(self):
        result = quiet_time.update_settings(enabled=True, start_hour=1, end_hour=5)
        assert result == {"enabled": True, "start_hour": 1, "end_hour": 5}

    def test_rejects_invalid_start_hour(self):
        with pytest.raises(ValueError):
            quiet_time.update_settings(start_hour=24)
        with pytest.raises(ValueError):
            quiet_time.update_settings(start_hour=-1)

    def test_rejects_invalid_end_hour(self):
        with pytest.raises(ValueError):
            quiet_time.update_settings(end_hour=25)
        with pytest.raises(ValueError):
            quiet_time.update_settings(end_hour=-1)


class TestIsQuiet:
    def _mock_hour(self, hour):
        return patch("quiet_time.datetime", wraps=datetime, **{
            "now.return_value": datetime(2026, 3, 21, hour, 30)
        })

    def test_disabled_is_never_quiet(self):
        quiet_time.update_settings(enabled=False, start_hour=0, end_hour=23)
        with self._mock_hour(12):
            assert quiet_time.is_quiet() is False

    # Overnight range: 22:00 - 07:00
    def test_overnight_during_quiet(self):
        quiet_time.update_settings(enabled=True, start_hour=22, end_hour=7)
        with self._mock_hour(23):
            assert quiet_time.is_quiet() is True

    def test_overnight_after_midnight(self):
        quiet_time.update_settings(enabled=True, start_hour=22, end_hour=7)
        with self._mock_hour(3):
            assert quiet_time.is_quiet() is True

    def test_overnight_at_start_boundary(self):
        quiet_time.update_settings(enabled=True, start_hour=22, end_hour=7)
        with self._mock_hour(22):
            assert quiet_time.is_quiet() is True

    def test_overnight_before_start(self):
        quiet_time.update_settings(enabled=True, start_hour=22, end_hour=7)
        with self._mock_hour(21):
            assert quiet_time.is_quiet() is False

    def test_overnight_at_end_boundary(self):
        quiet_time.update_settings(enabled=True, start_hour=22, end_hour=7)
        with self._mock_hour(7):
            assert quiet_time.is_quiet() is False

    def test_overnight_midday(self):
        quiet_time.update_settings(enabled=True, start_hour=22, end_hour=7)
        with self._mock_hour(12):
            assert quiet_time.is_quiet() is False

    # Daytime range: 9:00 - 17:00
    def test_daytime_during_quiet(self):
        quiet_time.update_settings(enabled=True, start_hour=9, end_hour=17)
        with self._mock_hour(12):
            assert quiet_time.is_quiet() is True

    def test_daytime_at_start_boundary(self):
        quiet_time.update_settings(enabled=True, start_hour=9, end_hour=17)
        with self._mock_hour(9):
            assert quiet_time.is_quiet() is True

    def test_daytime_at_end_boundary(self):
        quiet_time.update_settings(enabled=True, start_hour=9, end_hour=17)
        with self._mock_hour(17):
            assert quiet_time.is_quiet() is False

    def test_daytime_before_start(self):
        quiet_time.update_settings(enabled=True, start_hour=9, end_hour=17)
        with self._mock_hour(8):
            assert quiet_time.is_quiet() is False

    def test_daytime_after_end(self):
        quiet_time.update_settings(enabled=True, start_hour=9, end_hour=17)
        with self._mock_hour(20):
            assert quiet_time.is_quiet() is False

    # Midnight boundary
    def test_midnight_hour(self):
        quiet_time.update_settings(enabled=True, start_hour=22, end_hour=7)
        with self._mock_hour(0):
            assert quiet_time.is_quiet() is True
