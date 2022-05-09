import os.path
import random
import string


def generate_input(cases,r):

    letters = []
    input = []
    for i in range(10):
        letter = random.choice(string.ascii_letters)
        if letter not in letters:
            letters.append(letter)

        numerator = r.randint(-100000, 100000)
        denominator = r.randint(-100000, 100000)
        input.append("input " + letter + " " + str(numerator) + " " + str(denominator))

    for i in range(cases):
        arg1 = random.choice(letters)
        arg2 = random.choice(letters)
        input.append("+ " + arg1 + " " + arg2)
    for i in range(cases):
        arg1 = random.choice(letters)
        arg2 = random.choice(letters)
        input.append("- " + arg1 + " " + arg2)
    for i in range(cases):
        arg1 = random.choice(letters)
        arg2 = random.choice(letters)
        input.append("* " + arg1 + " " + arg2)
    for i in range(cases):
        arg1 = random.choice(letters)
        arg2 = random.choice(letters)
        input.append("/ " + arg1 + " " + arg2)
    for i in range(cases):
        arg1 = random.choice(letters)
        arg2 = random.choice(letters)
        input.append("cmp " + arg1 + " " + arg2)
    input.append("exit")
    return input