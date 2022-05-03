import os
import sys
from glob import glob
import argparse
import random
import subprocess
import validator
import outputgenerator
import inputgenerator
import psutil
import traceback
from subprocess import PIPE as PIPE

# List of "compiler" locations, VsDevCmd should be used to call the cpp compiler, as the MS cpp compiler needs
# certain things setup and it's just easier to let MS do it
CSPATH = "C:\Windows\Microsoft.NET\Framework\\v4.0.30319\csc.exe"
CPPPATH2022x86 = "C:\Program Files (x86)\Microsoft Visual Studio\\2022\Community\Common7\Tools\VsDevCmd.bat"
CPPPATH2022x64 = "C:\Program Files\Microsoft Visual Studio\\2022\Community\Common7\Tools\VsDevCmd.bat"
CPPPATH2019x86 = "C:\Program Files (x86)\Microsoft Visual Studio\\2019\Community\Common7\Tools\VsDevCmd.bat"
CPPPATH2019x64 = "C:\Program Files\Microsoft Visual Studio\\2019\Community\Common7\Tools\VsDevCmd.bat"
ECPPPATH2022x86 = "C:\Program Files (x86)\Microsoft Visual Studio\\2022\Enterprise\Common7\Tools\VsDevCmd.bat"
ECPPPATH2022x64 = "C:\Program Files\Microsoft Visual Studio\\2022\Enterprise\Common7\Tools\VsDevCmd.bat"
ECPPPATH2019x86 = "C:\Program Files (x86)\Microsoft Visual Studio\\2019\Enterprise\Common7\Tools\VsDevCmd.bat"
ECPPPATH2019x64 = "C:\Program Files\Microsoft Visual Studio\\2019\Enterprise\Common7\Tools\VsDevCmd.bat"


def main():
    # Setup commandline argument parsing
    parser = argparse.ArgumentParser(description='Autograding script')
    parser.add_argument('-v', '-V', '--verbose', help='Print all output to the screen, not just diffs',
                        action='store_true')
    parser.add_argument('-f', '-F', '--file', help='Path to the file to be compiled and tested', type=ascii)
    parser.add_argument('-c', '-C', '--cases', default=10, help='The number of cases to be ran against', type=int)
    parser.add_argument('-s', '-S', '--seed', default=-1, help="The seed value for the random number generator",
                        type=int)
    parser.add_argument('--compiler_location', default='default', help='Path to the compiler')
    parser.add_argument('-r', '-R', '--reuse', default=False, help="Reuse the last generated input",
                        action='store_true')
    parser.add_argument('-l', '-L', '--language', default='default', help='Language to grade in: cs or cpp')
    parser.add_argument('-d','-D','--debug',help='Print debug information',action='store_true')
    parser.add_argument('-np', '--no_prompt',help= "Don't prompt with warning", action= 'store_true')
    args = parser.parse_args()

    # Get current working directory
    cwd = str(os.getcwd())

    # Turn compiler locations into a list, so we can iterate over them in case we need to
    compiler_locations = [CSPATH, CPPPATH2022x64, CPPPATH2019x64, CPPPATH2022x86, CPPPATH2019x86, ECPPPATH2022x64,
                          ECPPPATH2019x64, ECPPPATH2022x86, ECPPPATH2019x86]
    # Get a list of the cpp compiler locations
    cpp_compiler_locations = compiler_locations[1:]

    print("Line Divisions AutoGrading Script: ")
    if not args.no_prompt:
        print("************************************")
        print("Warning, this script temporarily renames all \".txt\" files in this directory to \".Restore\" files.\n"
              "They should be restored when this finishes running, however in the event of a crash this may not happen.\n"
              "If you have anything in this directory you cannot afford to lose, I recommend making a copy \n."
              "Running this with the command line argument -np, will bypass this warning. Press enter to continue. ")
        print("************************************")
        input()
        args.no_prompt = True

    # Get a list of the cs and cpp files in the cwd
    cs_file_list = glob(str(cwd) + "\\*.cs")
    cpp_file_list = glob(str(cwd) + "\\*.cpp")
    target_file = None
    compiler = None


    if args.debug:
        print("Just after init")
        print("args.file: " + str(args.file))
        print("args.cases: " + str(args.cases))
        print("args.seed: " + str(args.seed))
        print("args.compiler_location: " + str(args.compiler_location))
        print("args.reuse: " + str(args.reuse))
        print("args.language: " + str(args.language))
        print("cwd: " + str(cwd))
        print("compiler locations: " + str(compiler_locations))
        print("cpp_file_list: " + str(cpp_file_list))
        print("cs_file_list: " + str(cs_file_list))
        print("target_file: " + str(target_file))
        print("compiler: " + str(compiler))

    # If we don't know what to do exit
    if args.compiler_location != 'default' and args.language == 'default':
        print("When using the compiler location you must specify a language")
        exit()
        input()

    if args.file is not None:
        # If the user provided a specific file path
        target_file = str(args.file)
        if not os.path.exists(target_file):
            # Does that file exist? If not exit
            print("Specified file not found, Exiting")
            input()
            exit()

        # Is the user making us decide which compiler to use?
        if args.language == 'default' and target_file.endswith(".cpp"):
            # Find the cpp compiler if appropriate
            compiler = find_cpp_compiler(cpp_compiler_locations)

        elif args.language == 'default' and target_file.endswith(".cs"):
            # Find the cs if appropriate
            if os.path.exists(CSPATH):
                compiler = CSPATH

        # The user told us which language to use
        elif args.language == 'cpp':
            # If the user told us it was cpp
            if args.compiler_location != 'default':
                # and the user told us the exact compiler location
                if os.path.exists(args.compiler_location):
                    compiler = args.compiler_location
            # otherwise, attempt to find the compiler in the standard locations
            else:
                compiler = find_cpp_compiler(cpp_compiler_locations)

        elif args.language == 'cs':
            # It was CS
            if args.compiler_location != 'default':
                # and they told us which compiler to use
                if os.path.exists(args.compiler_location):
                    compiler = args.compiler_location
            # otherwise, try the default
            elif os.path.exists(CSPATH):
                compiler = CSPATH
        else:
            # We couldn't figure out which language we needed to use, so we're exiting
            print("Unknown language, exiting")
            input()
            exit()

    else:
        # File location not specified
        if args.language == 'default':
            # Language was also not specified, this is designed to be the default case
            if len(cs_file_list) == 1 and len(cpp_file_list) == 0:
                # If there's exactly one cs file and no other options, that must be it
                if os.path.exists(CSPATH):
                    # Confirm our compiler exists and set the target of the compiler
                    compiler = CSPATH
                    target_file = str(cs_file_list[0])

            elif len(cs_file_list) == 0 and len(cpp_file_list) == 1:
                # If there's exactly one cpp file and no other options, that must be it
                # Find our compiler exists and set the target of the compiler
                compiler = find_cpp_compiler(cpp_compiler_locations)
                target_file =str(cpp_file_list[0])

            else:
                # We don't know enough to select a file, exit
                print("Couldn't find file or there are too many in this directory. Exiting")
                input()
                exit()

        elif args.language != 'cs' and args.language != 'cpp':
            # The language provided isn't default and isn't something we know how to deal with exit
            print("Unknown language, exiting")
            input()
            exit()

        if len(cs_file_list) != 1 and args.language == 'cs':
            # We don't know enough to select a file, exit
            print("Couldn't find file or there are too many in this directory. Exiting")
            input()
            exit()
        elif args.language == 'cs':
            # We know can select a file, if the user told us exactly what compiler to use, do that
            if os.path.exists(args.compiler_location):
                compiler = args.compiler_location
            else:
                # Otherwise, here's the default
                compiler = CSPATH
                target_file = str(cs_file_list[0])

        if len(cpp_file_list) != 1 and args.language == 'cpp':
            # We don't know enough to select a file, exit
            print("Couldn't find file or there are too many in this directory. Exiting")
            input()
            exit()

        elif args.language == 'cpp':
            # We know can select a file, if the user told us exactly what compiler to use, do that
            if args.compiler_location != 'default':
                if os.path.exists(args.compiler_location):
                    compiler = args.compiler_location
            else:
                # Otherwise, here's find the default
                compiler = find_cpp_compiler(cpp_compiler_locations)

    if args.debug:
        print("After compiler/file selection:")
        print("args.file: " + str(args.file))
        print("args.cases: " + str(args.cases))
        print("args.seed: " + str(args.seed))
        print("args.compiler_location: " + str(args.compiler_location))
        print("args.reuse: " + str(args.reuse))
        print("args.language: " + str(args.language))
        print("cwd: " + str(cwd))
        print("compiler locations: " + str(compiler_locations))
        print("cpp_file_list: " + str(cpp_file_list))
        print("cs_file_list: " + str(cs_file_list))
        print("target_file: " + str(target_file))
        print("compiler: " + str(compiler))

    # We went through and failed to find a compiler, we should exit.
    if compiler is None:
        print("Compiler not found, Exiting")
        input()
        exit()
    # Additional redundant check to make sure that we've got everything we need. This shouldn't ever evaluate to true
    if target_file is None:
        print("Let me know if you see this, the target file seems to both exist and not")
        input()
        exit()

    # Get a seed number either from the user provided seed or from the system.
    seed = random.randrange(sys.maxsize)
    if args.seed != -1:
        seed = args.seed
    r = random.Random(seed)

    textfiles = glob(".\\*.lr")
    for file in textfiles:
        if "temp.lr" == str(file):
            continue
        if "out.lr" == str(file):
            continue
        os.remove(file)

    textfiles = glob(".\\*.txt")
    for file in textfiles:
        filename = file.split(".")[-2]
        os.rename(str(file), ".\\" + str(filename) + ".Restore")


    # If the reuse flag is set reuse the last run by reading the input file back in
    var = cwd + "\\temp.lr"
    if args.reuse and os.path.exists(var):
        print("Reusing the last run")
        with open('temp.lr','r') as file:
            program_input = file.readlines()
            file.close()

    else:
        # Alternatively, generate a new input file
        print("About to generate input, this may take a moment")
        program_input = inputgenerator.generate_input(args.cases, r)
        with open('temp.lr','w') as file:
            file.writelines(program_input)
            file.close()

    if args.verbose:
        print("Input:")
        for line in program_input:
            print(line)

    print("About to generate the reference output, this may take a moment...")
    reference_output = outputgenerator.generate_output(program_input)

    if args.verbose:
        print("Reference Output:")
        for line in reference_output:
            print(line)

    compiler_result = None
    # Compile the program
    if compiler in cpp_compiler_locations or (args.language == 'cpp' and compiler is not None):
        # CPP is kinda a pain, note that we don't directly call the compiler, we call the batch file VsDevCmd
        # We then call the compiler "cl" due to the need for certain environment variables to be set
        cmd_string = 'call "' + compiler + '"' + '&& cl /Fe:out "' + target_file + '"'
        compiler_result = subprocess.run(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                         shell=True)
        if args.debug:
            print("cmd_string: " + cmd_string)

        filelist = glob(str(cwd) + "\*.obj")
        for x in filelist:
            os.remove(x)
        filelist = glob(str(cwd) + "\*.pdb")
        for x in filelist:
            os.remove(x)

    elif compiler == CSPATH or (compiler is not None and args.language == 'cs'):
        # The CS compiler is easy and works exactly the way I think it should
        cmd_string = '"' + str(compiler) + ' " -out:"' + str(cwd) + '\\out.exe" "' + str(target_file) + '"'
        if args.debug:
            print("cmd_string: " + cmd_string)
        compiler_result = subprocess.run(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    student_output = []
    var = cwd + "\\out.exe"

    # Since we always name the file out.exe, if it doesn't exist something went wrong and we should exit
    if not os.path.exists(var):
        print("Something went wrong during compilation:")
        print(compiler_result)
        input()
        exit()

    p = None

    try:
        # Run the executable piping the input in and the output to a text file
        # Managing the buffers yourself is painful so we just let windows do it instead
        nvar = "\"" + str(var) + "\"" + " < temp.lr > out.lr"
        p = subprocess.Popen(nvar, shell=True, stderr=PIPE, stdout=PIPE)
        p.communicate(timeout=300)

    except subprocess.TimeoutExpired:
        # If they ran out of time, report it, but try to keep going anyway
        print("Error manually review: Time Limit Exceeded")
        if not p.poll():
            terminate_out_exe()

    # Attempt to delete the old executable, otherwise we might have issues with accidental reuse
    counter = 0
    while os.path.exists(var):
        try:
            os.remove(var)
        except Exception as e:
            counter += 1
            if (counter + 1) % 40000 == 0:
                print("Stuck trying to delete the old executable file. Wait please")
            if counter >= 200000:
                print("Failed to delete the old executable file. If you're reading this let me know!")
                input()
                exit()
            pass
    # Open the output file for reading and pull in the student output
    try:
        with open('out.lr', 'r') as output:
            for line in output:
                student_output.append(line)
    except Exception as e:
        #This shouldn't ever happen, but hey, expect the unexpected
        print("Something went wrong with the output file? "
              "Check output to ensure all chars are standard and check that the file is not in use")
        input()
        exit()

    #cleanup text files

    # Perform validation and report the score
    score, diff_list, error_list = validator.validator(args.cases)

    textfiles = glob(".\\*.txt")
    for file in textfiles:
        filename = file.split(".")[-2]
        os.rename(file, ".\\" + str(filename) + ".lr")

    restorefiles = glob(".\\*.Restore")
    for file in restorefiles:
        filename = file.split(".")[-2]
        os.rename(file, ".\\" + str(filename) + ".txt")

    for line in diff_list:
        print(line)
    if error_list is not []:
        for line in error_list:
            print(line)

    print("Score: " + str(score[0] * 100) + "%")
    print("The seed was  " + str(seed))

    input()


def find_cpp_compiler(cpp_compiler_locations):
    compiler = None
    for elem in cpp_compiler_locations:
        if os.path.exists(elem):
            compiler = elem
            break
    return compiler

def terminate_out_exe():
    pid = -1
    counter = 0
    stdout = ""
    stderr = ""
    while True:
        if counter + 1 % 100 == 0:
            print("Out.exe isn't dying correctly. If you're reading this let me know!")
        if counter > 500:
            print("Out.exe failed to die."
                  " Not sure what to do here so I'm going to just let it run and hope for the best")
            break
        try:
            proc = subprocess.Popen('wmic process where name="out.exe" delete', stderr=PIPE, stdout=PIPE,
                                    shell=True, text=True)
            stdout, stderr = proc.communicate()
            if "Instance deletion successful" in stdout:
                break
            elif "No Instance(s) Available" in stdout:
                break
            else:
                counter += 1
        except Exception as e:
            counter += 1
            print("Attempting to terminate the process resulted in an exception")
            traceback.print_exc()


    if "Instance deletion successful" in stdout:
        print("Process Successfully Terminated")
    elif "No Instance(s) Available" in stdout:
        pass
    else:
        print("Process NOT Terminated")
        input()
        exit()
    return


if __name__ == '__main__':
    main()