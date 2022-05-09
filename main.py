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

# This is, without doubt, the most questionable thing I've ever done
CSMAIN = 'using System;\nusing System.Numerics;\nusing System.Collections.Generic;\nnamespace RationalClass\n{\n    public class driver\n    {\n        public static void Main()\n        {\n            Dictionary<string, Rational> rationals = new Dictionary<string, Rational>();\n            rationals.Add(\"ans\", new Rational(0, 1));\n            while (true)\n            {               \n                try\n                {\n                    string line = Console.ReadLine().Trim();\n\n                    while(line.Contains(\"  \"))\n                    {\n                        line = line.Replace(\"  \", \" \");\n                    }\n\n                    string[] cmd = line.ToLower().Split(\' \');\n                    // Create a variable named arg1 with value (arg2 / arg3)\n                    // Don\'t let them name it all\n                    if(cmd[0] == \"input\")\n                    {\n                        if(cmd[1] == \"all\")\n                        {\n                            Console.WriteLine(\"\\\"all\\\" is a reserved word\");\n                            continue;\n                        }\n                        rationals.Add(cmd[1], new Rational(BigInteger.Parse(cmd[2]), BigInteger.Parse(cmd[3])));\n                        Console.WriteLine(\"Added \" + cmd[1] + \" to the dictionary\");\n                    }\n                    // Create a copy of variable arg1 named arg2\n                    else if (cmd[0] == \"copy\")\n                    {\n                        rationals[cmd[2]] = new Rational(rationals[cmd[1]]);\n                        Console.WriteLine(\"Copied \"+ cmd[1] + \" as \" + cmd[2]);\n                    }\n                    // Add the variable arg1 to the variable arg2\n                    else if(cmd[0] == \"+\")\n                    {\n                        rationals[\"ans\"] = rationals[cmd[1]].Add(rationals[cmd[2]]);\n                        Console.WriteLine(rationals[\"ans\"]);\n                    }\n                    // Subtract the variable arg2 from the variable arg1\n                    else if (cmd[0] == \"-\")\n                    {\n                        rationals[\"ans\"] = rationals[cmd[1]].Subtract(rationals[cmd[2]]);\n                        Console.WriteLine(rationals[\"ans\"]);\n                    }\n                    // Multiply the variable arg1 with the variable arg2\n                    else if (cmd[0] == \"*\")\n                    {\n                        rationals[\"ans\"] = rationals[cmd[1]].Multiply(rationals[cmd[2]]);\n                        Console.WriteLine(rationals[\"ans\"]);\n                    }\n                    // Divide the variable arg1 by the variable arg2\n                    else if (cmd[0] == \"/\")\n                    {\n                        rationals[\"ans\"] = rationals[cmd[1]].Divide(rationals[cmd[2]]);\n                        Console.WriteLine(rationals[\"ans\"]);\n                    }\n                    // Get the reciprocal of the variable arg1\n                    else if (cmd[0] == \"inv\")\n                    {\n                        rationals[\"ans\"] = rationals[cmd[1]].Reciprocal();\n                        Console.WriteLine(rationals[\"ans\"]);\n                    }\n                    // Compare the variable arg1 to the variable arg2\n                    else if(cmd[0] == \"cmp\")\n                    {\n                        Console.WriteLine(rationals[cmd[1]].CompareTo(rationals[cmd[2]]));\n                    }\n                    // Print the variable arg1, or all variables \n                    else if (cmd[0] == \"print\")\n                    {\n                        if (cmd[1] == \"all\")\n                        {\n                            foreach(KeyValuePair<string,Rational> kvp in rationals)\n                            {\n                                Console.WriteLine(kvp.Key + \": \" + kvp.Value.ToString());\n                            }\n                        }\n                        else\n                        {\n                            Console.WriteLine(cmd[1] + \": \" + rationals[cmd[1]]);\n                        }\n                    }else if (cmd[0] == \"exit\")\n                    {\n                        return;\n                    }\n                    // Inform the user the command was wrong\n                    else\n                    {\n                        Console.WriteLine(\"Enter a valid command\");\n                    }\n                }\n                // Inform the user the command raised an exception\n                catch (Exception e)\n                {\n                    Console.WriteLine(\"Enter a valid command, you raised an exception\");\n                }\n            }\n        }\n    }\n}'
CPPMAIN = '// Rational.cpp : This file contains the \'main\' function. Program execution begins and ends there.\n//\n\n#include <iostream>\n#include <vector>\n#include <map>\n#include \"Rational.h\"\nusing namespace std;\n\nint main()\n{\n\tmap<string, rational> variables;\n\tvariables[\"ans\"] = new rational(0, 1);\n\tbool broke = false;\n\twhile (true) {\n\t\ttry {\n\n\t\t\tif (broke) {\n\t\t\t\tbroke = false;\n\t\t\t\tcout << \"please enter a valid command\" << endl;\n\t\t\t}\n\n\t\t\tstring line;\n\t\t\tgetline(cin, line);\n\n\t\t\twhile (line.find(\"  \") != string::npos) {\n\t\t\t\tline.replace(line.find(\"  \"), 2, \" \");\n\t\t\t}\n\n\t\t\tchar seps[] = \" \\t\\n\";\n\t\t\tchar* complete_file_c_str = (char*)line.c_str();\n\t\t\tchar* next_token = NULL;\n\t\t\tchar* token = strtok_s(complete_file_c_str, seps, &next_token);\n\t\t\tvector<string> cmd;\n\n\t\t\twhile (token != NULL)\n\t\t\t{\n\t\t\t\tcmd.push_back(token);\n\t\t\t\ttoken = strtok_s(NULL, seps, &next_token);\n\t\t\t}\n\n\t\t\tif (cmd[0] == \"input\") {\n\t\t\t\tif (cmd.size() != 4) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tif (cmd[1] == \"all\") {\n\t\t\t\t\tcout << \"\\\"all\\\" is a reserved word\" << endl;\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tvariables[cmd[1]] = new rational(stoll(cmd[2]), stoll(cmd[3]));\n\t\t\t\tcout << \"Added \" + cmd[1] + \" to the map\" << endl;\n\t\t\t}\n\t\t\telse if (cmd[0] == \"copy\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 3) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tif (variables.find(cmd[2]) != variables.end()) {\n\t\t\t\t\trational* tmp = &variables[cmd[2]];\n\t\t\t\t\tdelete(tmp);\n\t\t\t\t}\n\t\t\t\tvariables[cmd[2]] = new rational(variables[cmd[1]]);\n\t\t\t\tcout << (\"Copied \" + cmd[1] + \" as \" + cmd[2]);\n\t\t\t}\n\t\t\t// Add the variable arg1 to the variable arg2\n\t\t\telse if (cmd[0] == \"+\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 3) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tvariables[\"ans\"] = variables[cmd[1]].add(variables[cmd[2]]);\n\t\t\t\tcout << variables[\"ans\"].toString() << endl;\n\t\t\t}\n\t\t\t// Subtract the variable arg2 from the variable arg1\n\t\t\telse if (cmd[0] == \"-\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 3) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tvariables[\"ans\"] = variables[cmd[1]].subtract(variables[cmd[2]]);\n\t\t\t\tcout << variables[\"ans\"].toString() << endl;\n\t\t\t}\n\t\t\t// Multiply the variable arg1 with the variable arg2\n\t\t\telse if (cmd[0] == \"*\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 3) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tvariables[\"ans\"] = variables[cmd[1]].multiply(variables[cmd[2]]);\n\t\t\t\tcout << variables[\"ans\"].toString() << endl;\n\t\t\t}\n\t\t\t// Divide the variable arg1 by the variable arg2\n\t\t\telse if (cmd[0] == \"/\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 3) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tvariables[\"ans\"] = variables[cmd[1]].divide(variables[cmd[2]]);\n\t\t\t\tcout << variables[\"ans\"].toString() << endl;\n\t\t\t}\n\t\t\t// Get the reciprocal of the variable arg1\n\t\t\telse if (cmd[0] == \"inv\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 2) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tvariables[\"ans\"] = variables[cmd[1]].reciprocal();\n\t\t\t\tcout << variables[\"ans\"].toString() << endl;\n\t\t\t}\n\t\t\t// Compare the variable arg1 to the variable arg2\n\t\t\telse if (cmd[0] == \"cmp\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 3) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tcout << (variables[cmd[1]].compareTo(variables[cmd[2]]));\n\t\t\t}\n\t\t\t// Print the variable arg1, or all variables\n\t\t\telse if (cmd[0] == \"print\")\n\t\t\t{\n\t\t\t\tif (cmd.size() != 2) {\n\t\t\t\t\tbroke = true;\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\t\t\t\tif (cmd[1] == \"all\")\n\t\t\t\t{\n\t\t\t\t\tfor (map<string, rational>::iterator it = variables.begin(); it != variables.end(); ++it)\n\t\t\t\t\t{\n\t\t\t\t\t\tcout << it->first + \": \" + it->second.toString() << endl;\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t\telse\n\t\t\t\t{\n\t\t\t\t\tcout << (cmd[1] + \": \" + variables[cmd[1]].toString());\n\t\t\t\t}\n\t\t\t}\n\t\t\telse if (cmd[0] == \"exit\")\n\t\t\t{\n\t\t\t\treturn 0;\n\t\t\t}\n\t\t\telse {\n\t\t\t\tcout << \"please enter a valid command\" << endl;\n\t\t\t}\n\n\t\t}\n\t\tcatch (exception& e) {\n\t\t\tcout << \"please enter a valid command\" << endl;\n\t\t}\n\n\t}\n\treturn 0;\n}'
CPPH = '#pragma once\n#include <string>\nusing namespace std;\nclass rational {\nprivate:\n\tlong long numerator{};\n\tlong long denominator{};\npublic:\n\trational() {};\n\t~rational() {};\n\trational(long long numerator, long long denominator);\n\trational(rational* r);\n\trational add(rational r);\n\trational subtract(rational r);\n\trational multiply(rational r);\n\trational divide(rational r);\n\trational reciprocal();\n\tint compareTo(rational r);\n\tlong long getNumerator();\n\tlong long getDenominator();\n\tstring toString();\n\tlong double toLongDouble();\n};\nstatic rational tmp;\nstatic rational negOne(-1, 1);\nlong long gcd(long long a, long long b);'


def main():
    # Setup commandline argument parsing
    parser = argparse.ArgumentParser(description='Autograding script')
    parser.add_argument('-v', '-V', '--verbose', help='Print all output to the screen, not just diffs',
                        action='store_true')
    parser.add_argument('-f', '-F', '--file', help='Path to the file to be compiled and tested', type=ascii)
    parser.add_argument('-c', '-C', '--cases', default=100, help='The number of cases to be ran against', type=int)
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

    print("Rational AutoGrading Script: ")

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
            if cwd + '\\Rational.cs' in cs_file_list and not cwd + '\\Rational.cpp' in cpp_file_list:
                # If there's exactly one cs file and no other options, that must be it
                if os.path.exists(CSPATH):
                    # Confirm our compiler exists and set the target of the compiler
                    compiler = CSPATH
                    target_file = cwd + '\\Rational.cs'

            if not cwd + '\\Rational.cs' in cs_file_list and cwd + '\\Rational.cpp' in cpp_file_list:
                # If there's exactly one cpp file and no other options, that must be it
                # Find our compiler exists and set the target of the compiler
                compiler = find_cpp_compiler(cpp_compiler_locations)
                target_file = cwd + '\\Rational.cpp'

            if target_file is None:
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
                target_file = cwd + '\\Rational.cs'
            else:
                # Otherwise, here's the default
                compiler = CSPATH
                target_file = str('Rational.cs')

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
                    target_file = cwd + '\\Rational.cpp'
                else:
                # Otherwise, here's find the default
                    compiler = find_cpp_compiler(cpp_compiler_locations)
                    target_file = cwd + '\\Rational.cpp'

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

    # If the reuse flag is set reuse the last run by reading the input file back in
    var = cwd + "\\temp.txt"
    if args.reuse and os.path.exists(var):
        print("Reusing the last run")
        with open('temp.txt','r') as file:
            program_input = file.readlines()
            file.close()

    else:
        # Alternatively, generate a new input file
        print("About to generate input, this may take a moment")
        program_input = inputgenerator.generate_input(args.cases, r)
        with open('temp.txt','w') as file:
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

        with open("DriverFile.cpp",'w') as file:
            file.write(CPPMAIN)
            file.close()
        if os.path.exists("Rational.h"):
            pass
        else:
            with open("Rational.h",'w') as file:
                file.write(CPPH)
            file.close()

        # CPP is kinda a pain, note that we don't directly call the compiler, we call the batch file VsDevCmd
        # We then call the compiler "cl" due to the need for certain environment variables to be set
        cmd_string = 'call "' + compiler + '"' + '&& cl /Fe:out Rational.cpp "'  + target_file + '"'
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

        os.remove("DriverFile.cpp")

    elif compiler == CSPATH or (compiler is not None and args.language == 'cs'):
        with open("Driver.cs",'w') as file:
            file.write(CSMAIN)
            file.close()

        # The CS compiler is easy and works exactly the way I think it should
        cmd_string = '"' + str(compiler) + ' " -out:"' + str(cwd) + '\\out.exe" Driver.cs "' + str(target_file) + '"'
        if args.debug:
            print("cmd_string: " + cmd_string)
        compiler_result = subprocess.run(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        os.remove("Driver.cs")
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
        nvar = "\"" + str(var) + "\"" + " < temp.txt > out.txt"
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
        with open('out.txt', 'r') as output:
            for line in output:
                student_output.append(line)
    except Exception as e:
        #This shouldn't ever happen, but hey, expect the unexpected
        print("Something went wrong with the output file? "
              "Check output to ensure all chars are standard and check that the file is not in use")
        input()
        exit()

    # Perform validation and report the score
    score, diff_list, error_list = validator.validator(student_output,reference_output,args.cases)

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