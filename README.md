# AStar GreedyBestFirstSearch Pathfinder with GUI
This was part of a college assignment where we implemented AStar and GreedyBestFirstSearch algorithms.

This is the program looks like with a grid drawn in it:

![image](https://user-images.githubusercontent.com/25244950/159969473-fbc51d19-85b1-44b1-97da-52a02eccc6cd.png)

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
- **Run** - Runs the selected algorithm, and draws the path (also saves path instructions into "output.txt"):

![image](https://user-images.githubusercontent.com/25244950/159971623-3b8db65e-17d7-41d6-a682-f975f0610d9b.png)
