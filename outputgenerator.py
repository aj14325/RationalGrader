import math
from fractions import Fraction


def generate_output(lines):
    variables = {"ans": Fraction(0, 1)}
    output = []
    for x in lines:

        cmd = x.split(' ')
        try:
            if cmd[0] == "input":
                variables[cmd[1]] = Fraction(int(cmd[2]), int(cmd[3]))
                output.append("Added " + cmd[1] + " to the dictionary")
            elif cmd[0] == "+":
                ans = variables[cmd[1]] + variables[cmd[2]]
                output.append(str(ans))
            if cmd[0] == "-":
                ans = variables[cmd[1]] - variables[cmd[2]]
                output.append(str(ans))
            if cmd[0] == "*":
                ans = variables[cmd[1]] * variables[cmd[2]]
                output.append(str(ans))
            if cmd[0] == "/":
                ans = variables[cmd[1]] / variables[cmd[2]]
                output.append(str(ans))
            if cmd[0] == "cmp":
                ans = variables[cmd[1]] - variables[cmd[2]]
                if(ans != 0):
                    output.append(str(math.copysign(1, ans)))
                else:
                    output.append("0")
            if cmd[0] == "exit":
                return output
        except:
            pass
        return output