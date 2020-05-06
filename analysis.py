import os
import sys
import time
import subprocess

repetitions = 3
folder_prefix = 'sudoku/'
output_suffix = 'OUT'
pythonCommand = 'python'
# pythonCommand = 'py -2'
analysis_file = 'analysisOUT.txt'
redirect = ' >> ' + analysis_file
input_list = [
    'input1',
    'input2',
    'input3',
    'input4',
    # 'x0',
    # 'x1',
    # 'x2',
    # 'x3',
    # 'hard1',
    # 'hard2',
    # 'hard3',
    # 'hard4',
    # 'hard5'
]

with open('analysis.txt', 'w') as file:
    print ""

for inputName in input_list:
    for i in range(0, repetitions):
        os.system("python CS3243_P2_Sudoku_33AC3.py" + " " + \
            folder_prefix + inputName + ".txt" + " " + \
            folder_prefix + inputName + output_suffix + ".txt" + redirect)
    for i in range(0, repetitions):
        os.system("python CS3243_P2_Sudoku_33FC.py" + " " + \
            folder_prefix + inputName + ".txt" + " " + \
            folder_prefix + inputName + output_suffix + ".txt" + redirect)

with open(analysis_file, 'r') as file:
    lines = file.readlines()
    # for each input times 2
    for x in range(0, len(input_list) * 2):
        remainder = x % 2
        if (remainder == 0):
            print('========================== ' + input_list[x // 2] + " AC3")
        else:
            print('========================== ' + input_list[x // 2] + " FC")
        
        # mark out starting line number
        startLine =  x * 2 * repetitions
        sum = 0
        for steps in range(startLine, startLine + 2 * repetitions, 2):
            sum += int(lines[steps])
        print(sum / repetitions) # should be the same
        sum = 0
        for time in range(startLine + 1, startLine + 2 * repetitions, 2):
            sum += float(lines[time])
        print(sum / float(repetitions))