# AI_PROJECT_2
Solving Sudoku and Pacman

## Sudoku
Utilises backtracking algorithm (DFS). Two different Inference Mechanisms were considered (Forward Checking and AC-3). Main file now uses Forward Checking due to better average timings (0.71s) compared to AC-3 (2.59s).

Choice of variable and values depend on 3 heuristics:
- Minimum Remaining Values (Choosing cell with smallest domain)
- Most Constraining Variable (Choose cell with highest degree with unassigned neighbours)
- Hidden Single (Human-like technique to distinguish the hidden 'correct' value in a cell)
LCV (Least constraining value) is scraped since it takes too long to process.

### Input Command to run Program (Uses Python 2)

Format: `python $PROGRAM_NAME $INPUT_TEST_CASE $OUTPUT_FILE`

E.g. `python CS3243_P2_Sudoku_26.py sudoku/input1.txt out.txt`

## Pacman
Using Pacman AI projects were developed at UC Berkeley, because our module coordinators couldn't afford to make their own Pacman code template.

Currently implemented NewExtractor as part of features, that allows Pacman to not be an idiot and needing over 100 training runs to solve some mazes.

**Highlights of NewExtractor:**
- It can distinguish activeGhost from scaredGhost
- It will try to find and eat capsules if activeGhost is present, conserve capsules otherwise
- It will play safe by prioritising finishing the maze instead of actively seeking out scaredGhost (HIGHLY USEFUL for trickyClassic and capsuleClassic)
- It's usually not retarded (stuttering up and down after eating capsules due to overdose)



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
E.g.
**Without ApproximateQAgent** [Q1]
`python pacman.py -p PacmanQAgent -x 50 -n 60 -l mediumGrid`
**With ApproximateQAgent and Features** [Q2 & Q3]
`python pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -x 50 -n 60 -l mediumGrid`

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

