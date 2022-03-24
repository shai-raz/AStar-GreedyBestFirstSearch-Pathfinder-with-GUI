import tkinter as tk
import alogs
from alogs import AStar, GreedyBestFirstSearch, MAP_DICT
import os
import time

COLOR_DICT = {
    'R': 'Yellow',  # paved road
    'D': 'Orange',  # non paved road
    'W': 'Blue',  # water
    'A': 'Green',  # start
    'B': 'Red',  # end
}

COLOR_ID = ['R', 'W', 'D', 'A', 'B']  # order of cycling clicks


class Frame():
    grid = []
    num_of_rows = 0
    num_of_cols = 0
    last_dragged = None

    def __init__(self, root, *args, **kwargs):
        self.root = root
        self.menu = tk.Menu(root)
        self.menu.add_command(label="Load", command=self.load)
        self.menu.add_command(label="Save", command=self.save)
        self.menu.add_command(label="Reset", command=self.reset)

        algo_menu = tk.Menu(self.menu, tearoff=0)
        algo_menu.add_command(
            label="A*", command=lambda: self.setAlgorithm("A*"))
        algo_menu.add_command(label="Greedy Best First Search",
                              command=lambda: self.setAlgorithm("greedyBestFirst"))
        self.menu.add_cascade(label="Algorithm", menu=algo_menu)
        self.menu.add_command(label="Run", command=self.run)
        root.config(menu=self.menu)

        # Setup Canvas
        self.c = tk.Canvas(root, height=600, width=600, bg='white')
        self.c.pack(fill=tk.BOTH, expand=True)
        self.c.bind('<Configure>', self.initGrid)
        self.pixel_width = 20
        self.pixel_height = 20

        self.algorithm = "A*"  # default is astar

        self.statusbar = tk.Label(
            root, text=self.algorithm, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        # change statusbar text
        # self.statusbar.config(text="Ready")

        # Setup binds
        self.c.bind("<ButtonPress-1>", self.leftClick)
        self.c.bind("<B1-Motion>", self.leftClickDrag)
        # self.c.bind("<ButtonRelease-1>", lambda x: print("Release"))

    def updateStatusBar(self):
        self.statusbar.config(text=self.algorithm)

    def setAlgorithm(self, algo):
        self.algorithm = algo
        self.updateStatusBar()

    def getPosInGrid(self, item):
        item = item[0] - 1
        x = int(item % self.num_of_cols)
        y = int(item / self.num_of_cols)
        return x, y

    def updateCell(self, items, drag=False):
        x, y = self.getPosInGrid(items)
        # print(f"item: {items[0]-1}, x, y: {x}, {y}")

        if drag:
            if self.last_dragged == (x, y):
                return
        self.last_dragged = (x, y)

        next_tile = COLOR_ID[(COLOR_ID.index(
            self.grid[y][x]) + 1) % len(COLOR_ID)]
        next_color = COLOR_DICT[next_tile]
        self.grid[y][x] = next_tile
        # print(self.grid)

        rect_id = items[0]
        self.c.itemconfigure(rect_id, fill=next_color)

    def leftClick(self, event):
        items = self.c.find_closest(event.x, event.y)
        if items:
            self.updateCell(items)

    def leftClickDrag(self, event):
        items = self.c.find_closest(event.x, event.y)
        if items:
            self.updateCell(items, True)

    def displayPath(self, path):
        path = path.split("-")

        start = alogs.find_start_and_end(self.grid)[0]
        current = start

        for move in path:
            if move == "R":
                current = (current[0] + 1, current[1])
            elif move == "L":
                current = (current[0] - 1, current[1])
            elif move == "U":
                current = (current[0], current[1] - 1)
            elif move == "D":
                current = (current[0], current[1] + 1)

            if self.grid[current[1]][current[0]] == MAP_DICT["ENDING_POINT"]:
                break
            self.c.itemconfigure(
                current[0] + current[1] * self.num_of_cols + 1, fill="magenta")

    def updateGrid(self):
        num_of_items = self.num_of_rows * self.num_of_cols
        for i in range(num_of_items):
            x = int(i % self.num_of_cols)
            y = int(i / self.num_of_cols)
            self.c.itemconfigure(i+1, fill=COLOR_DICT[self.grid[y][x]])

    def createGrid(self):
        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                x1 = (x * self.pixel_width)
                x2 = (x1 + self.pixel_width)
                y1 = (y * self.pixel_height)
                y2 = (y1 + self.pixel_height)
                self.c.create_rectangle(
                    x1, y1, x2, y2, fill=COLOR_DICT[self.grid[y][x]])
        self.c.update()

    def initGrid(self, event=None):
        self.num_of_rows = int(self.c.winfo_height() / self.pixel_height)
        self.num_of_cols = int(self.c.winfo_width() / self.pixel_width)
        print("Rows: " + str(self.num_of_rows))
        print("Cols: " + str(self.num_of_cols))
        self.grid = [[MAP_DICT["PAVED_ROAD"] for _ in range(
            self.num_of_cols)] for _ in range(self.num_of_rows)]

        self.createGrid()

    def load(self):
        self.algorithm, size, self.grid = alogs.read_file("input.txt")
        self.num_of_rows = size
        self.num_of_cols = size
        self.updateStatusBar()
        self.updateGrid()

    def save(self):
        with(open("input.txt", "w+")) as f:
            f.write(f"{self.algorithm}\n")
            f.write(str(self.num_of_rows) + "\n")

            for row in self.grid:
                f.write("".join(row) + "\n")
            # remove last charachter
            f.truncate(f.tell()-len(os.linesep))

    def run(self):
        self.updateGrid()
        if self.algorithm == "A*":
            astar = AStar(self.grid, self.num_of_rows)
            start = time.time()
            path, cost = astar.run()
            end = time.time()
            print(f"Time to run: {end-start}")
        elif self.algorithm == "greedyBestFirst":
            greedy = GreedyBestFirstSearch(self.grid, self.num_of_rows)
            path, cost = greedy.run()
        print(path)
        print(cost)
        self.displayPath(path)

    def reset(self):
        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                self.grid[y][x] = MAP_DICT["PAVED_ROAD"]
        self.updateGrid()

def main():
    root = tk.Tk()
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    gui = Frame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
