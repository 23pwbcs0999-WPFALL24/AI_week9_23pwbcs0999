# Connect Four (12x12) - Minimax AI

## Overview
This project implements the Connect Four game using Python and the Minimax algorithm with Alpha-Beta Pruning.

### Features
- 12 x 12 game board
- Player A = Green
- Player B = Yellow
- Human vs Human mode
- Human vs AI mode
- Graphical User Interface using Tkinter
- Winning detection for horizontal, vertical, and diagonal lines of 4
- Draw detection
- AI powered by Minimax + Alpha-Beta Pruning

## How to Run
1. Make sure Python 3 is installed.
2. Save the source code as `connect_four_12x12.py`
3. Run:

```bash
python connect_four_12x12.py
```

## How to Play
- At the start, choose:
  - **Yes** for Human vs AI
  - **No** for Human vs Human
- Click a column number at the top to drop your disc.
- Green always starts first.
- The disc falls to the lowest available spot in the selected column.
- First player to make 4 in a row wins.

## AI Details
The board is large, so a full minimax search is too slow.
To keep the game playable, the AI uses:
- Depth-limited Minimax
- Alpha-Beta Pruning
- Heuristic board evaluation

You can make the AI stronger by increasing `AI_DEPTH`, but the AI will become slower.

## Create an Executable
Install PyInstaller:

```bash
pip install pyinstaller
```

Then build the executable:

```bash
pyinstaller --onefile --windowed connect_four_12x12.py
```

The final executable will appear in the `dist` folder.

## Notes
- The game uses Tkinter, which is included with most Python installations.
- If Tkinter is missing, install the Python distribution that includes it.
