# AStar GreedyBestFirstSearch Pathfinder with GUI
This was part of a college assignment where we implemented AStar and GreedyBestFirstSearch algorithms.

This is the program looks like with a grid drawn in it:

![image](https://user-images.githubusercontent.com/25244950/160116919-ec7ea1b4-1c47-4a83-a381-f8588294f56a.png)

## Tiles
There are 5 different tiles that can be used:
1. **Start tile** - Green
2. **End tile** - Red
3. **Water tile (acts like a wall)** - Blue
4. **Fast road tile (costs 1 to travel through)** - Yellow
5. **Slow road tile (costs 4 to travel through)** - Orange

You can switch between the different tiles by clicking/dragging across the grid.

There can only be 1 start tile and 1 end tile.

## Menu Options:
- **Load** - Loads a saved grid (from "input.txt").
- **Save** - Saves the currently displayed grid and its algorithm (into "input.txt").
- **Reset** - Resets the board, changing all the tiles to Fast road tiles (yellow).
- **Algorithm** - A drop down menu that allows you to choose what algorithm you want to use (default is A*).
- **Run** - Runs the selected algorithm, and draws the path):

![image](https://user-images.githubusercontent.com/25244950/160116995-e4b8162f-907f-4ed2-9f02-2b09c3e5588d.png)

## Usage Demo:
![demo](https://user-images.githubusercontent.com/25244950/160117436-95d0cdb9-517a-4260-9fa1-1e7b04df7de3.gif)

