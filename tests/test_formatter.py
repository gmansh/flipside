import pytest
from vesta.character_codes import BLANK, A, H, E, L, O
from vesta.formatter import blank_board, center_line, make_board, render_template
from config import BOARD_ROWS, BOARD_COLS


class TestBlankBoard:
    def test_dimensions(self):
        board = blank_board()
        assert len(board) == BOARD_ROWS
        assert all(len(row) == BOARD_COLS for row in board)

    def test_all_blank(self):
        board = blank_board()
        assert all(cell == BLANK for row in board for cell in row)

    def test_custom_dimensions(self, board_4x10):
        board = blank_board()
        assert len(board) == 4
        assert all(len(row) == 10 for row in board)


class TestCenterLine:
    def test_short_text_centered(self):
        row = center_line("HI")
        assert len(row) == BOARD_COLS
        # "HI" is 2 chars, padded to 22 → 10 blanks on each side
        pad = (BOARD_COLS - 2) // 2
        assert row[pad] == H
        assert row[pad + 1] == 9  # I

    def test_truncates_long_text(self):
        text = "A" * 30
        row = center_line(text)
        assert len(row) == BOARD_COLS
        assert all(c == A for c in row)

    def test_exact_width(self):
        text = "A" * BOARD_COLS
        row = center_line(text)
        assert len(row) == BOARD_COLS
        assert all(c == A for c in row)

    def test_empty_text(self):
        row = center_line("")
        assert len(row) == BOARD_COLS
        assert all(c == BLANK for c in row)

    def test_custom_dimensions(self, board_4x10):
        row = center_line("HI")
        assert len(row) == 10
        pad = (10 - 2) // 2
        assert row[pad] == H


class TestMakeBoard:
    def test_single_line_centered(self):
        board = make_board(["HI"])
        assert len(board) == BOARD_ROWS
        # With center valign, single line goes to middle row
        mid = (BOARD_ROWS - 1) // 2
        assert any(c != BLANK for c in board[mid])
        # Other rows are blank
        for i, row in enumerate(board):
            if i != mid:
                assert all(c == BLANK for c in row)

    def test_valign_top(self):
        board = make_board(["A", "B"], valign="top")
        assert any(c != BLANK for c in board[0])
        assert any(c != BLANK for c in board[1])

    def test_valign_bottom(self):
        board = make_board(["A", "B"], valign="bottom")
        assert any(c != BLANK for c in board[BOARD_ROWS - 2])
        assert any(c != BLANK for c in board[BOARD_ROWS - 1])

    def test_empty_lines(self):
        board = make_board([])
        assert board == blank_board()

    def test_truncates_excess_lines(self):
        lines = [f"LINE {i}" for i in range(20)]
        board = make_board(lines)
        assert len(board) == BOARD_ROWS

    def test_all_rows_correct_width(self):
        board = make_board(["HELLO", "WORLD"])
        assert all(len(row) == BOARD_COLS for row in board)

    def test_custom_dimensions(self, board_4x10):
        board = make_board(["HI"])
        assert len(board) == 4
        assert all(len(row) == 10 for row in board)
        mid = (4 - 1) // 2
        assert any(c != BLANK for c in board[mid])

    def test_custom_dimensions_truncates(self, board_4x10):
        lines = ["A", "B", "C", "D", "E", "F"]
        board = make_board(lines)
        assert len(board) == 4


class TestRenderTemplate:
    def test_substitution(self):
        board = render_template("HELLO {{name}}", {"name": "WORLD"})
        assert len(board) == BOARD_ROWS
        assert all(len(row) == BOARD_COLS for row in board)

    def test_multiple_keys(self):
        board = render_template("{{a}} {{b}}", {"a": "HI", "b": "BYE"})
        assert len(board) == BOARD_ROWS

    def test_missing_key_untouched(self):
        # Missing keys are left as-is (become encoded chars)
        board = render_template("{{missing}}", {})
        assert len(board) == BOARD_ROWS

    def test_multiline_template(self):
        board = render_template("LINE1\nLINE2", {})
        assert len(board) == BOARD_ROWS
