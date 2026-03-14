import io
import pytest
from PIL import Image
from vesta.character_codes import BLACK, WHITE, RED, GREEN, BLUE, ORANGE, YELLOW, VIOLET
from image.pixelmap import _nearest_color, pixelmap, pixelmap_bytes
from config import BOARD_ROWS, BOARD_COLS


class TestNearestColor:
    def test_pure_black(self):
        assert _nearest_color(0, 0, 0) == BLACK

    def test_pure_white(self):
        assert _nearest_color(255, 255, 255) == WHITE

    def test_near_red(self):
        assert _nearest_color(200, 30, 30) == RED

    def test_near_green(self):
        assert _nearest_color(40, 170, 40) == GREEN

    def test_near_blue(self):
        assert _nearest_color(40, 70, 210) == BLUE

    def test_near_orange(self):
        assert _nearest_color(220, 130, 50) == ORANGE

    def test_near_yellow(self):
        assert _nearest_color(230, 210, 70) == YELLOW

    def test_near_violet(self):
        assert _nearest_color(140, 40, 190) == VIOLET


def _make_test_image(width, height, color):
    """Create a solid-color test image."""
    img = Image.new("RGB", (width, height), color)
    return img


def _image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestPixelmap:
    def test_returns_correct_dimensions(self, tmp_path):
        img = _make_test_image(100, 50, (0, 0, 0))
        path = tmp_path / "test.png"
        img.save(path)
        board = pixelmap(str(path))
        assert len(board) == BOARD_ROWS
        assert all(len(row) == BOARD_COLS for row in board)

    def test_solid_black_image(self, tmp_path):
        img = _make_test_image(100, 50, (0, 0, 0))
        path = tmp_path / "black.png"
        img.save(path)
        board = pixelmap(str(path))
        assert all(cell == BLACK for row in board for cell in row)

    def test_solid_white_image(self, tmp_path):
        img = _make_test_image(100, 50, (255, 255, 255))
        path = tmp_path / "white.png"
        img.save(path)
        board = pixelmap(str(path))
        assert all(cell == WHITE for row in board for cell in row)


class TestPixelmapBytes:
    def test_returns_correct_dimensions(self):
        img = _make_test_image(100, 50, (0, 0, 0))
        board = pixelmap_bytes(_image_to_bytes(img))
        assert len(board) == BOARD_ROWS
        assert all(len(row) == BOARD_COLS for row in board)

    def test_solid_red_image(self):
        img = _make_test_image(100, 50, (190, 40, 40))
        board = pixelmap_bytes(_image_to_bytes(img))
        assert all(cell == RED for row in board for cell in row)

    def test_custom_dimensions(self, board_4x10):
        img = _make_test_image(100, 50, (0, 0, 0))
        board = pixelmap_bytes(_image_to_bytes(img))
        assert len(board) == 4
        assert all(len(row) == 10 for row in board)
