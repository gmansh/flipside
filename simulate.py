#!/usr/bin/env python3
"""Terminal simulator for the Vestaboard 6×22 display.

Usage:
    python simulate.py live               # read current board from device
    python simulate.py weather            # preview all weather icons
    python simulate.py board.json         # render a saved board JSON file
    echo '[[0,1,...], ...]' | python simulate.py -   # pipe board JSON from stdin

From Python:
    from simulate import render_board
    board = [[0]*22 for _ in range(6)]
    render_board(board, label="My Board")
"""
import json
import sys

from vesta.character_codes import CODE_TO_CHAR, COLOR_RGB

_BG = (10, 10, 10)
_FLAP_BG = (26, 26, 26)
_TEXT_FG = (232, 224, 208)
_RESET = "\033[0m"


def _ansi_bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


def _ansi_fg(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def _render_cell(code: int) -> str:
    """Render a single cell as 2 terminal characters wide."""
    if code in COLOR_RGB:
        r, g, b = COLOR_RGB[code]
        return f"{_ansi_bg(r, g, b)}  {_RESET}"
    ch = CODE_TO_CHAR.get(code, "?")
    return f"{_ansi_bg(*_FLAP_BG)}{_ansi_fg(*_TEXT_FG)} {ch}{_RESET}"


def render_board(board: list[list[int]], label: str | None = None) -> None:
    """Print a 6×22 board to the terminal with ANSI colors."""
    if label:
        print(f"\n  {label}")
    border_w = len(board[0]) * 2 + 2 if board else 46
    print(f"  {_ansi_bg(*_BG)}{' ' * border_w}{_RESET}")
    for row in board:
        cells = "".join(_render_cell(code) for code in row)
        print(f"  {_ansi_bg(*_BG)} {_RESET}{cells}{_ansi_bg(*_BG)} {_RESET}")
    print(f"  {_ansi_bg(*_BG)}{' ' * border_w}{_RESET}")


def _unwrap_board(data) -> list[list[int]]:
    """Extract board array from JSON data, supporting raw arrays and {"message": [...]} wrappers."""
    return data if isinstance(data, list) else data.get("message", data)


def _cmd_live() -> None:
    """Read and display the current board from the Vestaboard."""
    from vesta.client import read
    board = read()
    if board is None:
        print("Error: could not read board state. Is the Vestaboard reachable?",
              file=sys.stderr)
        sys.exit(1)
    render_board(board, label="LIVE BOARD")


def _cmd_weather() -> None:
    """Cycle through all weather icons."""
    from automations.weather import (
        _compose_board, ICON_SUN, ICON_PARTLY_CLOUDY, ICON_CLOUD,
        ICON_RAIN, ICON_SNOW, ICON_THUNDERSTORM,
    )
    icons = [
        ("CLEAR", ICON_SUN),
        ("PARTLY CLOUDY", ICON_PARTLY_CLOUDY),
        ("OVERCAST", ICON_CLOUD),
        ("RAIN", ICON_RAIN),
        ("SNOW", ICON_SNOW),
        ("THUNDERSTORM", ICON_THUNDERSTORM),
    ]
    for name, icon in icons:
        board = _compose_board([name, "72\u00b0F", "HI 78  LO 65"], icon)
        render_board(board, label=name)


def _cmd_file(path: str) -> None:
    """Render a board from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    render_board(_unwrap_board(data), label=path)


def _cmd_stdin() -> None:
    """Render a board from JSON on stdin."""
    data = json.load(sys.stdin)
    render_board(_unwrap_board(data))


_USAGE = """\
Usage:
  python simulate.py live               read and display current board
  python simulate.py weather            preview all weather icons
  python simulate.py <file.json>        render a board from a JSON file
  echo '<json>' | python simulate.py -  render board JSON from stdin"""


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "live":
            _cmd_live()
        elif sys.argv[1] == "weather":
            _cmd_weather()
        elif sys.argv[1] == "-":
            _cmd_stdin()
        else:
            _cmd_file(sys.argv[1])
    else:
        print(_USAGE)
