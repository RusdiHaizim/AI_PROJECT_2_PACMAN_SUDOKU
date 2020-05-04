import sys
from copy import deepcopy
from Queue import Queue
from time import time


# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt
FAILURE = -1
knownValues = {}
fileIn = None
### Class containing csp model i.e. variables, domains, edges btw variables, backupForReassignment
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
        self.domain = {v: list(range(1, 10)) if puzzle1[i] == 0 else [puzzle1[i]] for \
                       i, v in enumerate(self.varList)}

        # KnownValues
        for i in range(len(puzzle2)):
            for j in range(len(puzzle2)):
                if puzzle2[i][j] != 0:
                    knownValues[(i, j)] = puzzle2[i][j]

        # form neighbour dict for each var
        for var in self.varList:
            self.neighbours[var] = list()
            for i in range(len(puzzle2)):
                # Check same row
                if (var[0], i) != var:
                    self.neighbours[var].append((var[0], i))
                # Check same col
                if (i, var[1]) != var:
                    self.neighbours[var].append((i, var[1]))
            # Check same box
            boxRow = (var[0] // 3) * 3
            boxCol = (var[1] // 3) * 3
            for i in range(boxRow, boxRow + 3):
                for j in range(boxCol, boxCol + 3):
                    if (i, j) != var and (i, j) not in self.neighbours[var]:
                        self.neighbours[var].append((i, j))

        # Init restore for each var, var:list()
        self.restore = {v: list() for v in self.varList}

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
                self.restore[var].append((nCell, value))

    # DEPRECATED
    def unassign(self, var, assignment):
        if var in assignment:
            for (cell, value) in self.restore[var]:
                self.domain[cell].append(value)
            self.restore[var] = []
            del assignment[var]


### Class containing Sudoku solving methods: AC3 and Backtrack
class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = self.copy(puzzle)  # self.ans is a list of lists
        self.csp = Csp(puzzle)
        self.constraints = self.getConstraints(self.csp)
        self.steps = 0

    def copy(self, puzzle):
        new_puzzle = [[x for x in row] for row in puzzle]
        return new_puzzle

    def runAC3(self, csp, var=None, assignment=None):
        qu = Queue()
        for nCell in self.csp.neighbours[var]:
            if nCell not in assignment:
                    qu.put((nCell, var))
        # qu = self.getConstraints(csp)
        while True:
            if qu.empty():
                break
            xI, xJ = qu.get()
            if self.revise(csp, xI, xJ, var):
                if len(csp.domain[xI]) == 0:
                    return False
                # Don't need propagate xI if it doesnt contain 1 value only
                if len(csp.domain[xI]) != 1:
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
        for dI in csp.domain[xI]:
            if dI in csp.domain[xJ] and len(csp.domain[xJ]) == 1:
                csp.domain[xI].remove(dI)
                if var is not None:
                    csp.restore[var].append( (xI, dI) )
                revised = True
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
        for val in self.csp.domain[var]:
            if val != value:
                self.csp.domain[var].remove(val)
                self.csp.restore[var].append((var, val))

    def unassign(self, var, assignment):
        if var in assignment:
            for (cell, value) in self.csp.restore[var]:
                self.csp.domain[cell].append(value)
            self.csp.restore[var] = []
            del assignment[var]

    def runInference(self, assignment, var, value):
        # return self.runAC3(self.csp, var, assignment)
        for nCell in self.csp.neighbours[var]:
            if nCell not in assignment and value in self.csp.domain[nCell]:
                self.csp.domain[nCell].remove(value)
                self.csp.restore[var].append((nCell, value))
        return True

    # Bulk of solve is here
    def backtrackSearch(self, assignment):
        if len(assignment) == len(self.csp.varList):
            return assignment
        # Most constrained variable heuristic
        var = self.selectUnassignedVariable(assignment)
        # Least Constraining Value heuristic
        for value in self.orderDomainValues(var):
            # if self.csp.isConsistent(assignment, var, value):
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

    # Function to return var with min number of domain values
    def selectUnassignedVariable(self, assignment):
        unassigned = [v for v in self.csp.varList if v not in assignment]
        return min(unassigned, key=lambda var: len(self.csp.domain[var]))

    ##For now, return domain list of a variable
    def orderDomainValues(self, var):
        # Return value which gives least count of conflicts btw cells
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
        pP(self.puzzle)
        startTime = time()
        timeTaken = 0
        print 'Starting backtrack'

        # RUN BACKTRACKING
        assignment = {}
        # assignment.update(knownValues)
        assignment = self.backtrackSearch(assignment)
        if assignment is not None:
            print 'STEPS:', self.steps
            for var in newPuzzle.domain:
                newPuzzle.domain[var] = [assignment[var]] if len(var) > 1 else newPuzzle.domain[var]
            for k in newPuzzle.domain:
                pass
            # print k, newPuzzle.domain[k]
        if assignment is not None:
            # TODO ASSIGN
            timeTaken = time() - startTime
            self.getOutput(newPuzzle)
            print 'Backtrack SUCCESS'
            pP(self.ans)
            self.checkResult()

        else:
            # NO solution, returning original sudoku
            print 'Backtrack FAILED'

        print 'Time:', timeTaken
        # self.ans is a list of lists
        return self.ans

    def checkResult(self):
        try:
            fileOut = fileIn
            if fileIn is not None:
                if 'input' in fileIn:
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