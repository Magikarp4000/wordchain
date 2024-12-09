"""Config file."""

# ---------------- Model config ----------------
MODEL_NAME = 'word2vec-google-news-300'
FILE_NAME = 'googlenews'
# ----------------------------------------------

FPS = 60

WIDTH = 600
HEIGHT = 450

WORLD_WIDTH = 1000
WORLD_HEIGHT = 1000

VALID = 0
INVALID = 1
GUESSED = 2
UNSIMILAR = 3
WON = 4

NODE_SIZE = 75
NODE_COLOUR = (110, 146, 245, 255)

MAX_LINE_LENGTH = 200
MIN_LINE_LENGTH = 25
MIN_SIM = 0.35
MAX_SIM = 1
MAX_SIM_POS = 0.55
MIN_SIM_FEEDBACK = 0.2
MAX_TRIES = 5000

DISPLAY_TEXT_PAD = 20

TOLERANCE = 0.25

LOGO_SIZE = 125
TITLE_SIZE = 40
LOADING_TEXT_SIZE = 20
