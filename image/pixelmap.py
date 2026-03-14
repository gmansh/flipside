from PIL import Image
from vesta.character_codes import BLACK, WHITE, RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET

# Vestaboard color palette: code → RGB
_PALETTE: list[tuple[int, tuple[int, int, int]]] = [
    (BLACK,  (0,   0,   0)),
    (WHITE,  (255, 255, 255)),
    (RED,    (190, 40,  40)),
    (ORANGE, (210, 120, 40)),
    (YELLOW, (220, 200, 60)),
    (GREEN,  (50,  160, 50)),
    (BLUE,   (50,  80,  200)),
    (VIOLET, (130, 50,  180)),
]

ROWS = 6
COLS = 22


def _nearest_color(r: int, g: int, b: int) -> int:
    best_code, best_dist = BLACK, float("inf")
    for code, (pr, pg, pb) in _PALETTE:
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < best_dist:
            best_dist = dist
            best_code = code
    return best_code


def pixelmap(path: str) -> list[list[int]]:
    """Convert an image file to a 6x22 Vestaboard character code array."""
    img = Image.open(path).convert("RGB")
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    board = []
    for row in range(ROWS):
        line = []
        for col in range(COLS):
            r, g, b = img.getpixel((col, row))
            line.append(_nearest_color(r, g, b))
        board.append(line)
    return board


def pixelmap_bytes(data: bytes) -> list[list[int]]:
    """Convert image bytes to a 6x22 Vestaboard character code array."""
    import io
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    board = []
    for row in range(ROWS):
        line = []
        for col in range(COLS):
            r, g, b = img.getpixel((col, row))
            line.append(_nearest_color(r, g, b))
        board.append(line)
    return board
