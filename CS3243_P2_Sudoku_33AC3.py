import sys
from copy import deepcopy
from Queue import Queue
from time import time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt
FAILURE = -1
knownValues = {}
fileIn = None


# Class containing csp model i.e. variables, domains, edges btw variables, backupForReassignment
class Csp(object):
    def __init__(self, puzzle):
        self.varList = list()
        self.domain = dict()
        self.neighbours = dict()
        self.restore = dict()
        self.initialise(self.transformTo1D(puzzle), puzzle)

    def transformTo1D(self, puzzle):
        output = []
        for i in puzzle:
            for j in i:
                output.append(j)
        return output

    # puzzle1 is 1D puzzle, puzzle2 is 2D puzzle
    def initialise(self, puzzle1, puzzle2):
        # Init var to PAIR of coordinates from puzzle, varList[index]=var
        for i in range(9):
            for j in range(9):
                self.varList.append((i, j))
        # Init domains for each var, var:list()
        idx = 0
        for v in self.varList:
            self.domain[v] = set()
            if puzzle1[idx] == 0:
                for j in range(1, 10):
                    self.domain[v].add(j)
            else:
                self.domain[v].add(puzzle1[idx])
            idx += 1
        # self.domain = {v: set([range(1, 10)]) if puzzle1[i] == 0 else set([puzzle1[i]]) for \
        #                i, v in enumerate(self.varList)}

        # KnownValues
        for i in range(len(puzzle2)):
            for j in range(len(puzzle2)):
                if puzzle2[i][j] != 0:
                    knownValues[(i, j)] = puzzle2[i][j]

        # form neighbour dict for each var
        for var in self.varList:
            self.neighbours[var] = set()
            for i in range(len(puzzle2)):
                # Check same row
                if (var[0], i) != var:
                    self.neighbours[var].add((var[0], i))
                # Check same col
                if (i, var[1]) != var:
                    self.neighbours[var].add((i, var[1]))
            # Check same box
            boxRow = (var[0] // 3) * 3
            boxCol = (var[1] // 3) * 3
            for i in range(boxRow, boxRow + 3):
                for j in range(boxCol, boxCol + 3):
                    if (i, j) != var and (i, j) not in self.neighbours[var]:
                        self.neighbours[var].add((i, j))

        # Init restore for each var, var:list()
        # self.restore = {v: set() for v in self.varList}
        # fix for sunfire:
        for v in self.varList:
            self.restore[v] = set()

    def isSolved(self):
        for var in self.varList:
            if len(self.domain[var]) > 1:
                return False
        return True

    # DEPRECATED
    def isConsistent(self, assignment, var, value):
        for xI, x in assignment.iteritems():
            if x == value and xI in self.neighbours[var]:
                return False
        return True

    # DEPRECATED
    def assign(self, var, value, assignment):
        assignment[var] = value

        # do forward checking
        for nCell in self.neighbours[var]:
            if nCell not in assignment and value in self.domain[nCell]:
                self.domain[nCell].remove(value)
                self.restore[var].add((nCell, value))

    # DEPRECATED
    def unassign(self, var, assignment):
        if var in assignment:
            for (cell, value) in self.restore[var]:
                self.domain[cell].append(value)
            self.restore[var] = set()
            del assignment[var]


# Class containing Sudoku solving methods: AC3 and Backtrack
class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = self.copy(puzzle)  # self.ans is a list of lists
        self.csp = Csp(puzzle)
        self.constraints = self.getConstraints(self.csp)
        self.steps = 0
        self.timeTaken = 0
        self.hiddenSingleFlag = True # Flag for finding HiddenSingles, set to True initially

    def copy(self, puzzle):
        new_puzzle = [[x for x in row] for row in puzzle]
        return new_puzzle

    def runAC3(self, csp, var=None, assignment=None):
        if var is None or assignment is None:
            qu = self.getConstraints(csp)
        else:
            qu = Queue()
            for nCell in self.csp.neighbours[var]:
                if nCell not in assignment:
                    qu.put((nCell, var))
        while True:
            if qu.empty():
                break
            xI, xJ = qu.get()
            if self.revise(csp, xI, xJ, var):
                if len(csp.domain[xI]) == 0:
                    return False
                # Don't need propagate xI if it doesnt contain 1 value only
                if var is not None and len(csp.domain[xI]) != 1:
                    continue
                for xK in csp.neighbours[xI]:
                    if assignment is not None:
                        if xK != xJ and xK not in assignment:
                            qu.put((xK, xI))
                    elif xK != xJ:
                        qu.put((xK, xI))
        return True

    def revise(self, csp, xI, xJ, var=None):
        revised = False
        cop = csp.domain[xI].copy()
        for dI in csp.domain[xI]:
            if dI in csp.domain[xJ] and len(csp.domain[xJ]) == 1:
                cop.remove(dI)
                if var is not None:
                    csp.restore[var].add((xI, dI))
                revised = True
        csp.domain[xI] = cop
        return revised

    def getConstraints(self, csp):
        qu = Queue()  # Contains a pair of pairs xD
        for cell in csp.neighbours:  # sorted(csp.neighbours, key=csp.neighbours.get):
            for nCell in csp.neighbours[cell]:
                qu.put((cell, nCell))
        return qu

    def isConsistent(self, var, value):
        for nCell in self.csp.neighbours[var]:
            if value in self.csp.domain[nCell] and len(self.csp.domain[nCell]) == 1:
                return False
        return True

    def assign(self, assignment, var, value):
        assignment[var] = value
        cop = self.csp.domain[var].copy()
        for val in self.csp.domain[var]:
            if val != value:
                cop.remove(val)
                self.csp.restore[var].add((var, val))
        self.csp.domain[var] = cop

    def unassign(self, var, assignment):
        if var in assignment:
            for (cell, value) in self.csp.restore[var]:
                self.csp.domain[cell].add(value)
            self.csp.restore[var] = set()
            del assignment[var]

    def forwardCheck(self, assignment, var, value):
        for nCell in self.csp.neighbours[var]:
            if nCell not in assignment and value in self.csp.domain[nCell]:
                self.csp.domain[nCell].remove(value)
                self.csp.restore[var].add((nCell, value))
        return True

    def runInference(self, assignment, var, value):
        return self.runAC3(self.csp, var, assignment)
        # return self.forwardCheck(assignment, var, value)

    # Bulk of solve is here
    def backtrackSearch(self, assignment):
        if len(assignment) == len(self.csp.varList):
            return assignment

        # Select from 3 criteria (SEE function for more info)
        var = self.selectUnassignedVariable(assignment)
        # Stop finding HiddenSingles if first occurrence of MRV has started
        if not isinstance(var, list) and not len(self.csp.domain[var]) == 1 and self.hiddenSingleFlag:
            self.hiddenSingleFlag = False

        # Gives preference of value for HiddenSingle if found
        prefVal = None
        if isinstance(var, list):
            prefVal = var[1]
            var = var[0]

        # Least Constraining Value heuristic
        for value in self.orderDomainValues(var, prefVal):
            if self.isConsistent(var, value):
                self.assign(assignment, var, value)
                # Do inference i.e. forward checking or ac-3 here
                if self.runInference(assignment, var, value) != FAILURE:
                    result = self.backtrackSearch(assignment)
                    if result is not None:
                        return result
                    self.steps += 1
                self.unassign(var, assignment)
        return None

    # Function to decide which variable to select for backtracking
    # 3 criteria: size-1-domain var, HiddenSingles, MRV
    def selectUnassignedVariable(self, assignment):
        unassigned = [v for v in self.csp.varList if v not in assignment]
        minV = min(unassigned, key=lambda var: len(self.csp.domain[var]))
        # Return early if minV is confirmed to have only 1 value
        if len(self.csp.domain[minV]) == 1:
            return minV

        # Only find HiddenSingles if MRV isn't implemented yet [Idk why but it only works this way]
        if self.hiddenSingleFlag:
            for i in range(0, 9):
                # rowList = {v: [] for v in range(1, 10)}  # Checks for HiddenSingles by row
                # fix for sunfire:
                rowList = {}
                for v in range(1, 10):
                    rowList[v] = []
                # colList = {v: [] for v in range(1, 10)}  # Checks for HiddenSingles by col
                # fix for sunfire
                colList = {}
                for v in range(1, 10):
                    colList[v] = []
                for j in range(0, 9):
                    for v in self.csp.domain[(i, j)]:
                        if len(self.csp.domain[(i, j)]) != 1:
                            rowList[v].append((i, j))
                    for v in self.csp.domain[(j, i)]:
                        if len(self.csp.domain[(j, i)]) != 1:
                            colList[v].append((j, i))
                for v in rowList:
                    if len(rowList[v]) == 1:
                        return [rowList[v][0], v]
                for v in colList:
                    if len(colList[v]) == 1:
                        return [colList[v][0], v]

            # Checks for HiddenSingles by box
            bxLs = [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]
            for i in range(0, 9):
                # boxList = {v: [] for v in range(1, 10)}
                # fix for sunfire:
                boxList = {}
                for v in range(1, 10):
                    boxList[v] = []
                rowCount = bxLs[i][0]
                for y in range(rowCount, rowCount + 3):
                    colCount = bxLs[i][1]
                    for x in range(colCount, colCount + 3):
                        if len(self.csp.domain[(y, x)]) == 1:
                            continue
                        for v in self.csp.domain[(y, x)]:
                            boxList[v].append((y, x))
                for v in boxList:
                    if len(boxList[v]) == 1:
                        return [boxList[v][0], v]

        # MRV implemented if cannot find HiddenSingles
        return min(unassigned, key=lambda var: len(self.csp.domain[var]))

    # Firstly, tries to return domain with preferential value for HiddenSingle at the front, if present
    # Else, return normal domain of var
    def orderDomainValues(self, var, prefVal=None):
        # Return value which gives least count of conflicts btw cells
        if prefVal is not None:
            prefList = []
            for v in self.csp.domain[var]:
                prefList.append(v)
            prefList.insert(0, prefVal)
            return prefList
        # return sorted(self.csp.domain[var], key=lambda val: self.getConflictingCount(var, val))
        return self.csp.domain[var]

    def getConflictingCount(self, var, val):
        count = 0
        for nCell in self.csp.neighbours[var]:
            if len(self.csp.domain[nCell]) > 1 and val in self.csp.domain[nCell]:
                count += 1
        return count

    def getOutput(self, csp):
        for var in csp.domain:
            self.ans[var[0]][var[1]] = csp.domain[var][0]

    def solve(self):
        # TODO: Write your code here
        newPuzzle = self.csp
        # pP(self.puzzle)
        startTime = time()

        # RUN BACKTRACKING
        assignment = {}
        # assignment.update(knownValues)
        # self.runAC3(newPuzzle)
        # for key in sorted(newPuzzle.domain):
        #     print key, newPuzzle.domain[key]
        assignment = self.backtrackSearch(assignment)
        if assignment is not None:
            print self.steps
            for var in newPuzzle.domain:
                newPuzzle.domain[var] = [assignment[var]] if len(var) > 1 else newPuzzle.domain[var]
            for k in newPuzzle.domain:
                pass
            # print k, newPuzzle.domain[k]
        if assignment is not None:
            # TODO ASSIGN
            self.timeTaken = time() - startTime
            self.getOutput(newPuzzle)
            # print 'Backtrack SUCCESS'
            # pP(self.ans)
            print self.timeTaken
            # self.checkResult()
        else:
            # NO solution, returning original sudoku
            print 'Backtrack FAILED'

        # self.ans is a list of lists
        return self.ans

    def checkResult(self):
        try:
            fileOut = fileIn
            if fileIn is not None:
                if 'input' in fileIn and 'new' not in fileIn:
                    fileOut = fileOut.replace('input', 'output')
                else:
                    fileOut = fileOut.replace('.txt', 'OUT.txt')
            f = open(fileOut, 'r')
        except IOError:
            print("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
            raise IOError("Result file not found!")

        puzzle = [[0 for i in range(9)] for j in range(9)]
        lines = f.readlines()

        i, j = 0, 0
        for line in lines:
            for number in line:
                if '0' <= number <= '9':
                    puzzle[i][j] = int(number)
                    j += 1
                    if j == 9:
                        i += 1
                        j = 0

        if puzzle == self.ans:
            print 'PASS'
        else:
            print 'FAIL'


def pP(puzzle):
    for i in range(len(puzzle)):
        for j in range(len(puzzle)):
            print puzzle[i][j],
        print ""


def returnPuzzle(f):
    lines = f.readlines()
    puzzle = [[0 for i in range(9)] for j in range(9)]
    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0
    return puzzle


TIME_UB = 3


# Code for testing range of inputs
# Will find hardest inputs that the algorithm is trying to solve
def startTest(numRange):
    numRange = numRange.split(',')
    assert len(numRange) == 2
    fileStart = 'sudoku/batchtest/new_input'

    # Start the experiment to find top TIME_UB hardest puzzles
    hardest = []
    for i in range(int(numRange[0]), int(numRange[1]) + 1):
        try:
            fileName = fileStart + str(i) + '.txt'
            f = open(fileName, 'r')
        except:
            print 'Whoops'
            raise 'Input File ' + fileName + 'not found!'
        puz = returnPuzzle(f)
        sud = Sudoku(puz)
        sud.solve()
        if sud.timeTaken > TIME_UB:
            tup = (sud.timeTaken, puz, fileName.replace('sudoku/batchtest/', ''))
            hardest.append(tup)

    hardest.sort(reverse=True)
    for i in range(len(hardest)):
        print hardest[i][0], hardest[i][2]
        pP(hardest[i][1])
        print '@' * 15

    # if len(sys.argv) == 2: #Code for start of __main__, to run experiment
    #     print 'COMMENCING TEST'
    #     startTest(sys.argv[1])
    #     print 'END TEST'
    #     sys.exit(0)

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.


if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
        fileIn = str(sys.argv[1])
    except IOError:
        print("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
