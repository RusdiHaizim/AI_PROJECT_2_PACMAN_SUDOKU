# AI_PROJECT_2_GROUP_33
Solving Sudoku and Pacman

## Sudoku
Planned to run AC-3 algorithm to solve easier puzzles first. For harder puzzles, program uses backtracking with 2 heuristics, MRV (MOST CONSTRAINED VARIABLE) and LCV (LEAST CONSTRAINT VALUE).

### Input Command to run Program (Uses Python 2)

Format: `python $PROGRAM_NAME $INPUT_TEST_CASE $OUTPUT_FILE`

E.g. `python CS3243_P2_Sudoku_XX.py sudoku/input1.txt out.txt`

## Pacman
Using Pacman AI projects were developed at UC Berkeley, because our module coordinators couldn't afford to make their own Pacman code template.

:warning: You must download an XServer for your WSL(Windows Subsystem for Linux) for it to run the GUI. :warning:

Download at https://sourceforge.net/projects/xming/

### Input Command to run Program (Uses Python 2)

There are different ways to run the program.
Firstly, go to the pacman directory via `cd reinforcement`.

**Manual Mode (For fun):**
`python pacman.py`

**AI Mode (For simulation):**
* For testing Q1: `python autograder.py -q q1`
* For testing Q2: `python autograder.py -q q2`
* For full tests (Q1 and Q2): `python autograder.py`
* For manual maze selection: 
```
python pacman.py 
-p ApproximateQAgent 
-a extractor=$CHOSEN_EXTRACTOR_HERE$ 
-x $NUM_TRAINING$ 
-n $NUM_TRAINING_PLUS_SHOW_ON_GUI$ 
-l $MAZE_LAYOUT(SEE MORE BELOW)$
```

E.g. `python pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -x 50 -n 60 -l mediumGrid`

#### Maze Layouts:
* capsuleClassic
* contestClassic
* mediumClassic
* mediumGrid
* minimaxClassic
* openClassic
* originalClassic
* smallClassic
* smallGrid
* testClassic
* trappedClassic
* trickyClassic

