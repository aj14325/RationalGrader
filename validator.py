import glob
import difflib
import os.path
import re

def validator(cases):

    correct = 0
    score = []
    diff_list = []
    error_list = []
    reference_files = glob.glob(".\\reference_output_*.txt")
    student_files = glob.glob(".\\output_*.txt")

    for x in student_files:

        student_grid = []
        reference_grid = []

        tmp = re.split("[_\.]", x)
        num = tmp[-2]
        reference_file_path = ".\\reference_output_" + num + ".txt"
        try:
            with open(x,'r') as student_file:
                student_grid = student_file.readlines()
                student_file.close()
        except:
            error_list.append("Something went wrong with the file: " + x)

        if student_grid is []:
            error_list.append("Something went wrong with the file: " + x)
            continue;

        if reference_file_path not in reference_files:
            error_list.append("Something went wrong with the file \"" + x +
                              "\". No matching reference file, check that you've formatted the name correctly")
            continue

        try:
            with open(reference_file_path,'r') as reference_file:
                reference_grid = reference_file.readlines()
                reference_file.close()
        except:
            error_list.append("Something went wrong with the file: " + reference_file_path)
            continue

        if reference_grid is []:
            error_list.append("Something went wrong with the file: " + reference_file_path)
            continue

        student_grid = [x.strip() for x in student_grid]
        reference_grid = [x.strip() for x in reference_grid]

        result = list(difflib.Differ().compare(student_grid,reference_grid))
        thing = re.findall("[\+\-\?]+",str(result))
        if len(thing) == 0:
            correct += 1
        else:

            with open("diff_" + num+".lr", 'w') as diff_file:

                reading_guide ="Reading guide: Each line has a leading character, '+',' ','-', or '?'. A - indicates that there is something missing from a line that is present in the other, likewise a plus indicates that there is something present that was not in the other. A ? indicates that this line was not present in either file, and was therefore used to show where differences were. A ' ' means that there is no difference between the two files for that line"

                diff_file.write(pretty_print_string_to_list(reading_guide, len(result[0])))
                diff_file.writelines(result)
                diff_file.close()

            diff_list.append("Difference found on case " + num +
                             "check the diff_" + num + ".lr file for additional information");

    return [correct / cases], diff_list, error_list


def pretty_print_string_to_list(string, chars):
    string:str
    ans = []
    while True:
        space = string.rfind(' ', 0, chars)
        ans.append(string[:space])
        string = string[space:]
        if string == "":
            break

    return ans

