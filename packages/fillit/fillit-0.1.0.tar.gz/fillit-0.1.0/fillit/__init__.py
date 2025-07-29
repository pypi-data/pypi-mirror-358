from random import randint

TETRIMINO_SIZE = 4
DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def print_tetrimino(tetrimino):
    for line in tetrimino:
        print("".join(line))


def generate_tetrimino(tetrimino, x, y):
    tetrimino[y][x] = "#"
    i = 1
    while i < TETRIMINO_SIZE:
        while True:
            d = randint(0, TETRIMINO_SIZE - 1)
            if (
                (y + DIRECTIONS[d][0] >= 0) and (y + DIRECTIONS[d][0] < TETRIMINO_SIZE)
            ) and (
                (x + DIRECTIONS[d][1] >= 0) and (x + DIRECTIONS[d][1] < TETRIMINO_SIZE)
            ):
                if tetrimino[y + DIRECTIONS[d][0]][x + DIRECTIONS[d][1]] == "#":
                    i -= 1
                i += 1
                tetrimino[y + DIRECTIONS[d][0]][x + DIRECTIONS[d][1]] = "#"
                y += DIRECTIONS[d][0]
                x += DIRECTIONS[d][1]
                break


def create_tetrimino():
    tetrimino = [["." for x in range(TETRIMINO_SIZE)] for x in range(TETRIMINO_SIZE)]
    generate_tetrimino(
        tetrimino, randint(0, TETRIMINO_SIZE - 1), randint(0, TETRIMINO_SIZE - 1)
    )
    print_tetrimino(tetrimino)


def run():
    from sys import argv

    try:
        tetrimino_nbr = abs(int(argv[1]))
        while tetrimino_nbr:
            create_tetrimino()
            tetrimino_nbr -= 1
            if tetrimino_nbr:
                print()
    except Exception:
        print(f"Usage: {argv[0].split('/')[-1]} [tetrimino_nbr]")


__all__ = ["run"]
