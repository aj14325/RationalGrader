def validator(student_output, reference_output, cases):

    correct = 0
    score = []
    diff_list = []
    error_list = []

    for i,val in enumerate(student_output):

        if i > len(reference_output):
            print("Additional output detected, appending the rest as diffs")
            diff_list.append(student_output[i:])

            return [correct / cases], diff_list, error_list

        if val == reference_output[i]:
            correct += 1
        else:
            diff_list.append("Your output: " + val)
            diff_list.append("Reference output: " + reference_output[i])