import os.path


def generate_input(cases,r):

    files =[]
    for i in range(cases):
        height = r.randint(5, 50)
        width = r.randint(5, 50)
        prob = r.randint(25, 75)
        sim = r.randint(10, 200)
        grid = []
        for j in range(height):
            line = []
            for k in range(width):
                if r.randint(0, 100) < prob:
                    line.append('X')
                else:
                    line.append('O')
            grid.append(line)
        filename = 'input'
        counterstr = "{counter:02d}"
        counter = 0
        extention = ".txt"
        while os.path.exists(filename + counterstr.format(counter=counter) + extention):
            counter += 1
        with open(filename + counterstr.format(counter=counter) + extention,'w') as f:
            for line in grid:
                for char in line:
                    f.write(char)
                f.write("\n")
        files.append(filename + counterstr.format(counter=counter) + extention + " " + str(10) + "\n")
    files.append("end 0")
    return files