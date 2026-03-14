from vesta.character_codes import (
    encode, BLANK, A, Z, ZERO, ONE, NINE,
    RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET, WHITE, BLACK,
    EXCLAMATION, PERIOD, QUESTION, DEGREE,
)


class TestConstants:
    def test_letter_range(self):
        assert A == 1
        assert Z == 26

    def test_digit_codes(self):
        assert ONE == 27
        assert NINE == 35
        assert ZERO == 36

    def test_color_codes(self):
        assert RED == 63
        assert BLACK == 70

    def test_blank(self):
        assert BLANK == 0


class TestEncode:
    def test_uppercase(self):
        assert encode("AB") == [A, A + 1]

    def test_lowercase_converts(self):
        assert encode("ab") == [A, A + 1]

    def test_mixed_case(self):
        assert encode("Hi") == [8, 9]

    def test_digits(self):
        assert encode("10") == [ONE, ZERO]

    def test_space_is_blank(self):
        assert encode(" ") == [BLANK]

    def test_unknown_char_is_blank(self):
        assert encode("~") == [BLANK]
        assert encode("€") == [BLANK]

    def test_empty_string(self):
        assert encode("") == []

    def test_punctuation(self):
        assert encode("!.?") == [EXCLAMATION, PERIOD, QUESTION]

    def test_degree_symbol(self):
        assert encode("°") == [DEGREE]

    def test_full_sentence(self):
        codes = encode("HI 5!")
        assert codes == [8, 9, BLANK, FIVE, EXCLAMATION]


# Use the constant directly
FIVE = 31
