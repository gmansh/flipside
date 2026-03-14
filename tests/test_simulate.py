import json
import pytest
from unittest.mock import patch
from io import StringIO

from simulate import render_board, _render_cell
from vesta.character_codes import BLANK, A, RED, YELLOW, WHITE, CODE_TO_CHAR, COLOR_RGB
from config import BOARD_ROWS, BOARD_COLS


def _blank_board():
    return [[BLANK] * BOARD_COLS for _ in range(BOARD_ROWS)]


class TestCodeToChar:
    def test_blank_is_space(self):
        assert CODE_TO_CHAR[0] == " "

    def test_letter_a(self):
        assert CODE_TO_CHAR[A] == "A"

    def test_color_codes_not_in_char_map(self):
        # Color codes should not appear in the character map
        for code in range(63, 71):
            assert code in COLOR_RGB


class TestRenderCell:
    def test_blank_cell(self):
        result = _render_cell(BLANK)
        assert " " in result  # contains the space character
        assert "\033[" in result  # contains ANSI codes

    def test_letter_cell(self):
        result = _render_cell(A)
        assert "A" in result

    def test_color_block_cell(self):
        result = _render_cell(RED)
        # Color blocks render as two spaces with background color
        assert "190" in result or "40" in result  # RGB components of RED
        assert "  " in result  # two spaces for the block

    def test_unknown_code(self):
        result = _render_cell(999)
        assert "?" in result


class TestRenderBoard:
    def test_blank_board_prints(self, capsys):
        board = _blank_board()
        render_board(board)
        output = capsys.readouterr().out
        # Should have 8 lines: top border + 6 rows + bottom border
        lines = output.strip().split("\n")
        assert len(lines) == 8

    def test_label_printed(self, capsys):
        board = _blank_board()
        render_board(board, label="TEST LABEL")
        output = capsys.readouterr().out
        assert "TEST LABEL" in output

    def test_no_label(self, capsys):
        board = _blank_board()
        render_board(board)
        output = capsys.readouterr().out
        assert "TEST LABEL" not in output

    def test_color_blocks_rendered(self, capsys):
        board = _blank_board()
        board[0][0] = YELLOW
        render_board(board)
        output = capsys.readouterr().out
        # Yellow RGB (220, 204, 60) should appear in ANSI codes
        assert "220" in output

    def test_characters_rendered(self, capsys):
        board = _blank_board()
        board[0][0] = A
        render_board(board)
        output = capsys.readouterr().out
        assert "A" in output


class TestCmdFile:
    def test_loads_raw_array(self, tmp_path, capsys):
        board = _blank_board()
        board[0][0] = A
        path = tmp_path / "test.json"
        path.write_text(json.dumps(board))

        from simulate import _cmd_file
        _cmd_file(str(path))
        output = capsys.readouterr().out
        assert "A" in output

    def test_loads_message_wrapper(self, tmp_path, capsys):
        board = _blank_board()
        board[0][0] = A
        path = tmp_path / "test.json"
        path.write_text(json.dumps({"message": board}))

        from simulate import _cmd_file
        _cmd_file(str(path))
        output = capsys.readouterr().out
        assert "A" in output


class TestCmdStdin:
    def test_reads_from_stdin(self, capsys):
        board = _blank_board()
        board[0][0] = A
        stdin_data = json.dumps(board)

        from simulate import _cmd_stdin
        with patch("sys.stdin", StringIO(stdin_data)):
            _cmd_stdin()
        output = capsys.readouterr().out
        assert "A" in output

    def test_reads_message_wrapper(self, capsys):
        board = _blank_board()
        stdin_data = json.dumps({"message": board})

        from simulate import _cmd_stdin
        with patch("sys.stdin", StringIO(stdin_data)):
            _cmd_stdin()
        output = capsys.readouterr().out
        # Should render without error
        lines = output.strip().split("\n")
        assert len(lines) == 8


class TestCmdLive:
    def test_success(self, capsys):
        board = _blank_board()
        from simulate import _cmd_live
        with patch("vesta.client.read", return_value=board):
            _cmd_live()
        output = capsys.readouterr().out
        assert "LIVE BOARD" in output

    def test_failure_exits(self):
        from simulate import _cmd_live
        with patch("vesta.client.read", return_value=None):
            with pytest.raises(SystemExit):
                _cmd_live()
