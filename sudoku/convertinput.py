import os

# Set parameters
sourceFile = 'top2365.txt'
batchTestDirectoryPath = 'batchtest/'
testprefix = 'new_'
inputprefix = 'input'
fileTypeSuffix = '.txt'
maxCol = 9

startConvertingFromRow = 1
NumberToConvert = 2

# SCRIPT STARTS

if not os.path.exists(batchTestDirectoryPath):
    os.makedirs(batchTestDirectoryPath)

with open(sourceFile, 'r') as file: 
    puzzles = file.readlines()
    for i in range(startConvertingFromRow - 1, startConvertingFromRow - 1 + NumberToConvert):
        # print(puzzles[i])
        puzzle = [(num if num != '.' else '0') for num in puzzles[i]]
        # print (puzzle)
        convertedFileName = batchTestDirectoryPath + testprefix + inputprefix + str(i + 1) + fileTypeSuffix
        with open(convertedFileName, 'w') as convertedFile:
            output = ""
            
            colCount = 0
            for num in puzzle:
                if colCount == maxCol:
                    output = output[:len(output) - 1]
                    output += '\n'
                    colCount = 0

                output += num + " "
                colCount += 1
            
            convertedFile.write(output[:len(output) - 3])

print('CONVERSION COMPLETE')