# Vestaboard character codes
BLANK = 0

# Letters A-Z: 1-26
A = 1; B = 2; C = 3; D = 4; E = 5; F = 6; G = 7; H = 8; I = 9; J = 10
K = 11; L = 12; M = 13; N = 14; O = 15; P = 16; Q = 17; R = 18; S = 19; T = 20
U = 21; V = 22; W = 23; X = 24; Y = 25; Z = 26

# Digits: 1-9 are 27-35, 0 is 36
ONE = 27; TWO = 28; THREE = 29; FOUR = 30; FIVE = 31
SIX = 32; SEVEN = 33; EIGHT = 34; NINE = 35; ZERO = 36

# Punctuation / symbols
EXCLAMATION = 37    # !
AT = 38             # @
HASH = 39           # #
DOLLAR = 40         # $
LPAREN = 41         # (
RPAREN = 42         # )
HYPHEN = 43         # -
PLUS = 44           # +
AMPERSAND = 45      # &
EQUALS = 46         # =
SEMICOLON = 47      # ;
COLON = 48          # :
APOSTROPHE = 49     # '
QUOTE = 50          # "
PERCENT = 51        # %
COMMA = 52          # ,
PERIOD = 53         # .
SLASH = 54          # /
QUESTION = 55       # ?
DEGREE = 56         # °
TRADEMARK = 57      # ™
REGISTERED = 58     # ®
COPYRIGHT = 59      # ©
HEART = 60          # ♥
STAR = 61           # ★
ARROW = 62          # →

# Color blocks
RED = 63
ORANGE = 64
YELLOW = 65
GREEN = 66
BLUE = 67
VIOLET = 68
WHITE = 69
BLACK = 70

# Character to code mapping
_CHAR_MAP: dict[str, int] = {
    " ": BLANK,
    "A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H,
    "I": I, "J": J, "K": K, "L": L, "M": M, "N": N, "O": O, "P": P,
    "Q": Q, "R": R, "S": S, "T": T, "U": U, "V": V, "W": W, "X": X,
    "Y": Y, "Z": Z,
    "1": ONE, "2": TWO, "3": THREE, "4": FOUR, "5": FIVE,
    "6": SIX, "7": SEVEN, "8": EIGHT, "9": NINE, "0": ZERO,
    "!": EXCLAMATION, "@": AT, "#": HASH, "$": DOLLAR,
    "(": LPAREN, ")": RPAREN, "-": HYPHEN, "+": PLUS,
    "&": AMPERSAND, "=": EQUALS, ";": SEMICOLON, ":": COLON,
    "'": APOSTROPHE, '"': QUOTE, "%": PERCENT, ",": COMMA,
    ".": PERIOD, "/": SLASH, "?": QUESTION, "°": DEGREE,
    "™": TRADEMARK, "®": REGISTERED, "©": COPYRIGHT,
    "♥": HEART, "★": STAR, "→": ARROW,
}


# Reverse map: code → display character
CODE_TO_CHAR: dict[int, str] = {v: k for k, v in _CHAR_MAP.items()}
CODE_TO_CHAR[BLANK] = " "

# Color block display RGB values (approximate on-screen rendering colors)
COLOR_RGB: dict[int, tuple[int, int, int]] = {
    RED:    (190, 40, 40),
    ORANGE: (210, 120, 40),
    YELLOW: (220, 204, 60),
    GREEN:  (50, 160, 50),
    BLUE:   (50, 80, 200),
    VIOLET: (130, 50, 180),
    WHITE:  (240, 240, 240),
    BLACK:  (17, 17, 17),
}


def encode(text: str) -> list[int]:
    """Convert a string to a list of Vestaboard character codes."""
    return [_CHAR_MAP.get(ch.upper(), BLANK) for ch in text]
