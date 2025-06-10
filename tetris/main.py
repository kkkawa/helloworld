import curses
import random
import time

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1],
     [1, 1]],  # O
    [[0, 1, 0],
     [1, 1, 1]],  # T
    [[1, 0, 0],
     [1, 1, 1]],  # J
    [[0, 0, 1],
     [1, 1, 1]],  # L
    [[1, 1, 0],
     [0, 1, 1]],  # S
    [[0, 1, 1],
     [1, 1, 0]],  # Z
]


def rotate(shape):
    """Rotate a shape clockwise."""
    return [list(row) for row in zip(*shape[::-1])]


class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.x = BOARD_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self, board):
        new_shape = rotate(self.shape)
        if not collision(board, self.x, self.y, new_shape):
            self.shape = new_shape


def collision(board, x, y, shape):
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                px = x + cx
                py = y + cy
                if px < 0 or px >= BOARD_WIDTH or py >= BOARD_HEIGHT:
                    return True
                if py >= 0 and board[py][px]:
                    return True
    return False


def merge(board, piece):
    for cy, row in enumerate(piece.shape):
        for cx, cell in enumerate(row):
            if cell:
                px = piece.x + cx
                py = piece.y + cy
                if py >= 0:
                    board[py][px] = 1


def clear_lines(board):
    new_board = [row for row in board if any(v == 0 for v in row)]
    cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, cleared


def draw_board(stdscr, board, piece, score):
    stdscr.clear()
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            cell = board[y][x]
            stdscr.addstr(y, x * 2, "[]" if cell else "  ")
    for cy, row in enumerate(piece.shape):
        for cx, cell in enumerate(row):
            if cell:
                y = piece.y + cy
                x = piece.x + cx
                if y >= 0:
                    stdscr.addstr(y, x * 2, "[]")
    stdscr.addstr(0, BOARD_WIDTH * 2 + 2, f"Score: {score}")
    stdscr.refresh()


def game(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    piece = Piece()
    score = 0
    last_fall = time.time()

    while True:
        # handle input
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1
        if key == curses.KEY_LEFT and not collision(board, piece.x - 1, piece.y, piece.shape):
            piece.x -= 1
        elif key == curses.KEY_RIGHT and not collision(board, piece.x + 1, piece.y, piece.shape):
            piece.x += 1
        elif key == curses.KEY_DOWN and not collision(board, piece.x, piece.y + 1, piece.shape):
            piece.y += 1
        elif key in (curses.KEY_UP, ord(' ')):
            piece.rotate(board)
        elif key == ord('q'):
            break

        # gravity
        if time.time() - last_fall > 0.5:
            if not collision(board, piece.x, piece.y + 1, piece.shape):
                piece.y += 1
            else:
                merge(board, piece)
                board, cleared = clear_lines(board)
                score += cleared
                piece = Piece()
                if collision(board, piece.x, piece.y, piece.shape):
                    break  # game over
            last_fall = time.time()

        draw_board(stdscr, board, piece, score)

    stdscr.nodelay(False)
    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH - 4, "GAME OVER")
    stdscr.getch()


def main():
    curses.wrapper(game)


if __name__ == "__main__":
    main()
