import os


def generate_output(lines):
    for line in lines:
        tmp = line.split(' ')
        if tmp[0] == "end":
            return
        else:
            generate_one_case(tmp[0], int(tmp[1]))


def generate_one_case(filepath, iterations):
    lines = []
    with open(filepath, 'r') as f:
        lines = f.readlines()

    lines = [x.strip() for x in lines]
    grid = lines;

    for i in range(iterations):
        newgrid = []
        for x, line in enumerate(grid):
            newline = []
            for y, char in enumerate(line):
                newline.append(choose_char(grid, x, y))
            newgrid.append(newline)
        lg = grid
        grid = newgrid

    filename = 'reference_output_'
    counterstr = "{counter:02d}"
    counter = 0
    extention = ".txt"
    while os.path.exists(filename + counterstr.format(counter=counter) + extention):
        counter += 1
    with open(filename + counterstr.format(counter=counter) + extention, 'w') as f:
        for line in grid:
            for char in line:
                f.write(char)
            if not line[len(line) - 1] == '\n':
                f.write("\n")


def choose_char(l, x, y):
    tmp = live_neighbors(l, x, y)
    if l[x][y] == 'O':
        if tmp == 2 or tmp == 3:
            return 'O'
    if l[x][y] == 'X':
        if tmp == 3:
            return 'O'
    return 'X'


def live_neighbors(l, i, j):
    off = [-1, 0, 1]
    count = 0
    for x in off:
        for y in off:
            if y == 0 and x == 0:
                continue
            if j + y < 0 or x + i < 0:
                continue
            try:
                if l[x + i][j + y] == 'O':
                    count += 1
            except IndexError:
                pass
    return count
