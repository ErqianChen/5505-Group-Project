import random

NUM_COLS = NUM_ROWS = 4
BACKGROUND_COLOUR = '#bbada0'
LIGHT = '#f5ebe4'
DARK = '#615b56'
COLOURS = {
    None: '#ccc0b3',
    2: "#fcefe6",
    4: "#f2e8cb",
    8: "#f5b682",
    16: "#f29446",
    32: "#ff775c",
    64: "#e64c2e",
    128: "#ede291",
    256: "#fce130",
    512: "#ffdb4a",
    1024: "#f0b922",
    2048: "#fad74d"
}
FG_COLOURS = {
    2: DARK,
    4: DARK,
    8: LIGHT,
    16: LIGHT,
    32: LIGHT,
    64: LIGHT,
    128: LIGHT,
    256: LIGHT,
    512: LIGHT,
    1024: LIGHT,
    2048: LIGHT,
}

TITLE_FONT = ('Arial bold', 50)
TILE_FONT = ('Arial bold', 30)

LEFT = 'a'
UP = 'w'
DOWN = 's'
RIGHT = 'd'

NEW_TILE_DELAY = 150
MAX_UNDOS = 3

WIN_MESSAGE = 'You won! Would you like to play again?'
LOSS_MESSAGE = 'You lost :( Play again?'

BOARD_WIDTH = 400
BOARD_HEIGHT = 400
BUFFER = 10

def generate_tile(current_tiles):
    candidate_positions = []
    for i, row in enumerate(current_tiles):
        for j, tile in enumerate(row):
            if tile is None:
                candidate_positions.append((i, j))
    return random.choice(candidate_positions), random.choice([2] * 5 + [4])

def stack_left(tiles):
    stacked_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
    for i in range(NUM_ROWS):
        to_fill = 0
        for j in range(NUM_COLS):
            if tiles[i][j] is not None:
                stacked_tiles[i][to_fill] = tiles[i][j]
                to_fill += 1
    return stacked_tiles

def combine_left(tiles):
    combined_tiles = [row[:] for row in tiles]
    score_added = 0
    for i in range(NUM_ROWS):
        for j in range(NUM_COLS - 1):
            if combined_tiles[i][j] is not None and combined_tiles[i][j] == combined_tiles[i][j + 1]:
                combined_tiles[i][j] *= 2
                combined_tiles[i][j + 1] = None
                score_added += combined_tiles[i][j]
    return combined_tiles, score_added

def reverse(tiles):
    reversed_tiles = []
    for i in range(NUM_ROWS):
        reversed_tiles.append([])
        for j in range(NUM_COLS):
            reversed_tiles[i].append(tiles[i][3-j])
    return reversed_tiles

def transpose(tiles):
    transposed_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
    for i in range(NUM_ROWS):
        for j in range(NUM_COLS):
            transposed_tiles[i][j] = tiles[j][i]
    return transposed_tiles
