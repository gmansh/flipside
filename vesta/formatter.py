import re
from vesta.character_codes import encode, BLANK

ROWS = 6
COLS = 22


def blank_board() -> list[list[int]]:
    return [[BLANK] * COLS for _ in range(ROWS)]


def center_line(text: str) -> list[int]:
    """Encode text and center it within COLS, truncating if too long."""
    codes = encode(text)
    if len(codes) >= COLS:
        return codes[:COLS]
    pad = (COLS - len(codes)) // 2
    row = [BLANK] * COLS
    row[pad:pad + len(codes)] = codes
    return row


def make_board(lines: list[str], valign: str = "center") -> list[list[int]]:
    """Place lines on a blank board with horizontal centering and vertical alignment."""
    board = blank_board()
    n = len(lines)
    if n == 0:
        return board
    n = min(n, ROWS)
    lines = lines[:n]

    if valign == "top":
        start = 0
    elif valign == "bottom":
        start = ROWS - n
    else:  # center
        start = (ROWS - n) // 2

    for i, line in enumerate(lines):
        board[start + i] = center_line(line)

    return board


def render_template(template: str, props: dict) -> list[list[int]]:
    """Substitute {{key}} placeholders in template text, then render as board."""
    for key, value in props.items():
        template = template.replace("{{" + key + "}}", str(value))
    lines = template.split("\n")
    return make_board(lines)
