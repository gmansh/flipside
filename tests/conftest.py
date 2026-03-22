import pytest
from unittest.mock import patch

import quiet_time


@pytest.fixture(autouse=True)
def _reset_quiet_time():
    """Ensure quiet time is disabled for every test unless explicitly configured."""
    quiet_time._settings.update({"enabled": False, "start_hour": 22, "end_hour": 7})
    yield
    quiet_time._settings.update({"enabled": False, "start_hour": 22, "end_hour": 7})


@pytest.fixture
def board_4x10():
    """Patch board dimensions to 4 rows x 10 cols for testing configurability."""
    with (
        patch("config.BOARD_ROWS", 4),
        patch("config.BOARD_COLS", 10),
    ):
        # Re-import so modules pick up patched values
        import importlib
        import vesta.formatter as fmt
        import image.pixelmap as pm

        old_fmt_rows, old_fmt_cols = fmt.ROWS, fmt.COLS
        old_pm_rows, old_pm_cols = pm.ROWS, pm.COLS

        fmt.ROWS, fmt.COLS = 4, 10
        pm.ROWS, pm.COLS = 4, 10

        yield (4, 10)

        fmt.ROWS, fmt.COLS = old_fmt_rows, old_fmt_cols
        pm.ROWS, pm.COLS = old_pm_rows, old_pm_cols
