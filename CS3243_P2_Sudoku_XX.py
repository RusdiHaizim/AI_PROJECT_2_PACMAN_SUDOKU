import sys
import copy
from Queue import Queue
from time import time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

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

    #puzzle1 is 1D puzzle, puzzle2 is 2D puzzle
    def initialise(self, puzzle1, puzzle2):
        #Init var to PAIR of coordinates from puzzle, varList[index]=var
        for i in range(9):
            for j in range(9):
                self.varList.append( (i, j) )
        #Init domains for each var, var:list()
        self.domain = {v: list(range(1,10)) if puzzle1[i] == 0 else [puzzle1[i]] for \
                       i, v in enumerate(self.varList)}
        
        #form neighbour dict for each var
        for var in self.varList:
            self.neighbours[var] = list()
            for i in range(len(puzzle2)):
                #Check same row
                if (var[0], i) != var:
                    self.neighbours[var].append( (var[0], i) )
                #Check same col
                if (i, var[1]) != var:
                    self.neighbours[var].append( (i, var[1]) )
            #Check same box
            boxRow = (var[0] // 3) * 3
            boxCol = (var[1] // 3) * 3
            for i in range(boxRow, boxRow+3):
                for j in range(boxCol, boxCol+3):
                    if (i, j) != var and (i, j) not in self.neighbours[var]:
                        self.neighbours[var].append( (i, j) )
        
        #Init restore for each var, var:list()
        self.restore = {v: list() if puzzle1[i] == 0 else [puzzle1[i]] for \
                       i, v in enumerate(self.varList)}

    def isSolved(self):
        for var in self.varList:
            if len(self.domain[var]) > 1:
                return False
        return True

    def isConsistent(self, assignment, var, value):
        for xI, x in assignment.iteritems():
            if x == value and xI in self.neighbours[var]:
                return False
        return True

    def assign(self, var, value, assignment):
        assignment[var] = value

        #do forward checking
        for nCell in self.neighbours[var]:
            if nCell not in assignment and value in self.domain[nCell]:
                self.domain[nCell].remove(value)
                self.restore[var].append( (nCell, value) )
                
        
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
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = self.copy(puzzle) # self.ans is a list of lists
        self.csp = Csp(puzzle)
        self.constraints = self.getConstraints(self.csp)
        self.steps = 0

    def copy(self, puzzle):
        new_puzzle = [[x for x in row] for row in puzzle]
        return new_puzzle

    def runAC3(self, csp, var=None):
        qu = self.getConstraints(csp)
        #print 'len', qu.qsize()
        count = 0
        while True:
            if qu.empty():
                break
            count += 1
            xI, xJ = qu.get()
            if self.revise(csp, xI, xJ, var):
                #print 'lenQ', qu.qsize(), 'count', count
                if len(csp.domain[xI]) == 0:
                    #print 'xI is ZERO', xI
                    return False
                for xK in csp.neighbours[xI]:
                    #print 'xI', xI
                    #print 'xK', xK
                    if xK != xJ:
                        #print 'putting', xK, xI
                        qu.put( (xK, xI) )
        return True

    def revise(self, csp, xI, xJ, var=None):
        revised = False
        for i in csp.domain[xI]:
            removeFlag = True
            for j in csp.domain[xJ]:
                if j != i:
                    removeFlag = False
            if removeFlag:
                csp.domain[xI].remove(i)
                if var is not None:
                    csp.restore[var].append( (xI, i) )
                #print xI
                #print 'd removed', i
                #print xI, 'left with', csp.domain[xI]
                revised = True
        return revised

    def getConstraints(self, csp):
        qu = Queue() #Contains a pair of pairs xD
        for cell in csp.neighbours:#sorted(csp.neighbours, key=csp.neighbours.get):
            #print 'cell', cell
            #print 'nCell', csp.neighbours[cell], '\nlen', len(csp.neighbours[cell])
            for nCell in csp.neighbours[cell]:
                qu.put( (cell, nCell) )
                #print cell, nCell
        return qu

    #Bulk of solve is here
    def backtrackSearch(self, assignment):
        
        if len(assignment) == len(self.csp.varList):
            print 'ASSIGNED ALL'
            #print assignment
            #print self.csp.domain
            return assignment
        #Most constrained variable heuristic
        var = self.selectUnassignedVariable(assignment)
        #Least Constraining Value heuristic
        for value in self.orderDomainValues(var):
            if self.csp.isConsistent(assignment, var, value):
                #self.csp.assign(var, value, assignment)
                localAssignment = assignment.copy()
                localAssignment[var] = value

                #do forward checking
                for nCell in self.csp.neighbours[var]:
                    if nCell not in localAssignment and value in self.csp.domain[nCell]:
                        self.csp.domain[nCell].remove(value)
                        self.csp.restore[var].append( (nCell, value) )

                #self.runAC3(self.csp, var)
                
                #Do inference i.e. forward checking or ac-3 here
                result = self.backtrackSearch(localAssignment)
                if result is not None:
                    return result
                self.steps += 1

                self.csp.unassign(var, localAssignment)
                
        return None

    #Function to return var with min number of domain values
    def selectUnassignedVariable(self, assignment):
        unassigned = [v for v in self.csp.varList if v not in assignment]
        return min(unassigned, key=lambda var: len(self.csp.domain[var]))

    ##For now, return domain list of a variable
    #Return value which gives least count of conflicts btw cells
    def orderDomainValues(self, var):
        #return sorted(self.csp.domain[var], key=lambda val: self.getConflictingCount(var, val))
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
        print 'Trying AC3'
        if self.runAC3(newPuzzle):
            if newPuzzle.isSolved():
                #TODO ASSIGN
                timeTaken = time() - startTime
                self.getOutput(newPuzzle)
                print 'AC3 SUCCESS'
                pP(self.ans)
            else:
                print 'Starting backtrack'
                
                #RUN BACKTRACKING
                assignment = {}
                assignment = self.backtrackSearch(assignment)
                if assignment is not None:
                    print 'STEPS:', self.steps
                    for var in newPuzzle.domain:
                        newPuzzle.domain[var] = [assignment[var]] if len(var) > 1 else newPuzzle.domain[var]
                    for k in newPuzzle.domain:
                        pass
                    #print k, newPuzzle.domain[k]
                if assignment is not None:
                    #TODO ASSIGN
                    timeTaken = time() - startTime
                    self.getOutput(newPuzzle)
                    print 'Backtrack SUCCESS'
                    pP(self.ans)
                    print 'Result is', self.checkResult()
                    
                else:
                    #NO solution, returning original sudoku
                    print 'Backtrack FAILED'
                    
        print 'Time:', timeTaken
        # self.ans is a list of lists
        return self.ans

    def checkResult(self):
        try:
            f = open('sudoku/hard5OUT.txt', 'r')
        except IOError:
            print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
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
            return 'PASS'
        return 'FAIL'

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
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
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
