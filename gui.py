import tkinter as tk
from tkinter import messagebox
import alogs
from alogs import AStar, GreedyBestFirstSearch, MAP_DICT, Node
import os
import time
from threading import Thread
from multiprocessing import Queue

COLOR_DICT = {
    'R': 'Yellow',  # paved road
    'D': 'Orange',  # non paved road
    'W': 'Blue',  # water
    'A': 'Green',  # start
    'B': 'Red',  # end
    'V': 'Black',  # visited
    'S': 'White',  # successors
    'P': 'Magenta',  # path
}

VISU_DICT = {
    "VISITED": 'V',
    "SUCCESSOR": 'S',
    "PATH": 'P',
}

COLOR_ID = ['R', 'W', 'D', 'A', 'B']  # order of cycling clicks

class Frame():
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
            label="A*", command=lambda: self.set_algorithm("A*"))
        algo_menu.add_command(label="Greedy Best First Search",
                              command=lambda: self.set_algorithm("greedyBestFirst"))
        self.menu.add_cascade(label="Algorithm", menu=algo_menu)
        self.menu.add_command(label="Run", command=self.run)
        root.config(menu=self.menu)

        self.grid = []  # actual grid
        self.display_grid = []  # grid to display on canvas

        self.queue = Queue()
        self.visu_speed = 2 # higher = faster. deteremines how fast the visualization runs
        self.is_running = False  # is the algorithm currently running
        self.is_dirty = False  # is the grid dirty (path is shown)

        # add label
        # self.label = tk.Label(root, text="Speed:", font=("Helvetica", 16))
        # self.label.pack(side=tk.TOP)
        # # add input box
        # self.input_box = tk.Entry(root)
        # self.input_box.pack(side=tk.TOP, fill=tk.X)


        # Setup Canvas
        self.c = tk.Canvas(root, height=600, width=600, bg='white')
        self.c.pack(fill=tk.BOTH, expand=True)
        self.c.bind('<Configure>', self.init_grid)
        self.pixel_width = 20
        self.pixel_height = 20

        self.algorithm = "A*"  # default is astar
        self.cost = None

        self.statusbar = tk.Label(
            root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status_bar()

        # Setup binds
        self.c.bind("<ButtonPress-1>", self.left_click)
        self.c.bind("<ButtonPress-3>", self.right_click)
        self.c.bind("<B1-Motion>", self.left_click_drag)

        self.root.after(0, self.refresh_grid)

    def update_status_bar(self):
        value = f"Algorithm: {self.algorithm}"
        value += f"\tCost: {self.cost}" if self.cost else ""
        self.statusbar.config(text=value)

    def set_algorithm(self, algo):
        self.algorithm = algo
        self.cost = None
        self.update_status_bar()

        if algo == "A*":
            self.visu_speed = 2
        elif algo == "greedyBestFirst":
            self.visu_speed = 1

    def get_pos_in_grid(self, item):
        item = item[0] - 1
        x = int(item % self.num_of_cols)
        y = int(item / self.num_of_cols)
        return x, y

    def update_cell(self, items, drag=False):
        x, y = self.get_pos_in_grid(items)

        if drag:
            if self.last_dragged == (x, y):
                return
        self.last_dragged = (x, y)

        next_tile = COLOR_ID[(COLOR_ID.index(
            self.grid[y][x]) + 1) % len(COLOR_ID)]
        next_color = COLOR_DICT[next_tile]
        self.grid[y][x] = next_tile
        self.display_grid[y][x] = next_tile

        rect_id = items[0]
        self.c.itemconfigure(rect_id, fill=next_color)

    def right_click(self, event):
        if self.is_running:
            return

        if self.is_dirty:
            self.reset_display_grid()
            self.color_grid()
            self.is_dirty = False

    def left_click(self, event):
        if self.is_running:
            return

        if self.is_dirty:
            self.reset_display_grid()
            self.color_grid()
            self.is_dirty = False

        items = self.c.find_closest(event.x, event.y)
        if items:
            self.update_cell(items)

    def left_click_drag(self, event):
        if self.is_running:
            return

        if self.is_dirty:
            self.reset_display_grid()
            self.color_grid()
            self.is_dirty = False

        items = self.c.find_closest(event.x, event.y)
        if items:
            self.update_cell(items, True)

    def display_path(self, node):
        path = []
        while node is not None:
            path.append(node)
            node = node.parent

        path = path[::-1]

        for node in path:
            if self.grid[node.y][node.x] == MAP_DICT["ENDING_POINT"]:
                self.display_grid[node.y][node.x] = MAP_DICT["ENDING_POINT"]
            elif self.grid[node.y][node.x] == MAP_DICT["STARTING_POINT"]:
                self.display_grid[node.y][node.x] = MAP_DICT["STARTING_POINT"]
            else:
                self.display_grid[node.y][node.x] = VISU_DICT["PATH"]


    def refresh_grid(self):
        '''Checks if there are any new items to be added to the canvas,
         and colors the grid if so'''
        items = []

        for _ in range(self.visu_speed):
            try:
                items.append(self.queue.get_nowait())
            except:
                pass

        for item in items:
            if item[0] == "end":
                node, cost = item[1], item[2]
                self.display_path(node)
                self.is_running = False
                self.cost = cost
                self.update_status_bar()
            else:
                node, successors = item
                self.update_grid_by_algo_run(successors)

        if len(items) > 0:
            self.color_grid()

        self.root.after(10, self.refresh_grid)

    def color_grid(self):
        '''Color the grid according to display_grid'''
        num_of_items = self.num_of_rows * self.num_of_cols
        for i in range(num_of_items):
            x = int(i % self.num_of_cols)
            y = int(i / self.num_of_cols)
            self.c.itemconfigure(i+1, fill=COLOR_DICT[self.display_grid[y][x]])

    def create_grid(self):
        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                x1 = (x * self.pixel_width)
                x2 = (x1 + self.pixel_width)
                y1 = (y * self.pixel_height)
                y2 = (y1 + self.pixel_height)
                self.c.create_rectangle(
                    x1, y1, x2, y2, fill=COLOR_DICT[self.grid[y][x]])
        self.c.update()

    def init_grid(self, event=None):
        '''Initialize the grid with yellow paved roads'''
        self.num_of_rows = int(self.c.winfo_height() / self.pixel_height)
        self.num_of_cols = int(self.c.winfo_width() / self.pixel_width)
        print("Rows: " + str(self.num_of_rows))
        print("Cols: " + str(self.num_of_cols))
        self.grid = [[MAP_DICT["PAVED_ROAD"] for _ in range(
            self.num_of_cols)] for _ in range(self.num_of_rows)]

        self.display_grid = [row[:] for row in self.grid]

        self.create_grid()

    def reset_display_grid(self):
        self.display_grid = [row[:] for row in self.grid]

    def load(self):
        if self.is_running:
            return
        
        self.algorithm, size, self.grid = alogs.read_file("input.txt")
        self.display_grid = [row[:] for row in self.grid]
        self.num_of_rows = size
        self.num_of_cols = size
        self.color_grid()
        self.cost = None
        self.update_status_bar()

    def save(self):
        with(open("input.txt", "w+")) as f:
            f.write(f"{self.algorithm}\n")
            f.write(str(self.num_of_rows) + "\n")

            for row in self.grid:
                f.write("".join(row) + "\n")
            # remove last charachter
            f.truncate(f.tell()-len(os.linesep))

    def run(self):
        if self.is_running:
            return
        
        if alogs.find_start_and_end(self.grid)[0] is None or alogs.find_start_and_end(self.grid)[1] is None:
            tk.messagebox.showerror(
                "Error", "Missing starting and/or ending point(s)")
            return
        
        self.is_running = True
        self.is_dirty = True

        self.cost = None
        self.update_status_bar()
        self.reset_display_grid()
        self.color_grid()

        algo = None
        if self.algorithm == "A*":
            algo = AStar(self.grid, self.num_of_rows)
        elif self.algorithm == "greedyBestFirst":
            algo = GreedyBestFirstSearch(self.grid, self.num_of_rows)

        algo_thread = Thread(target=algo.run, args=(self.queue,))
        algo_thread.start()

    def reset(self):
        if self.is_running:
            return
        
        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                self.grid[y][x] = MAP_DICT["PAVED_ROAD"]
                self.display_grid[y][x] = MAP_DICT["PAVED_ROAD"]
        self.color_grid()

        self.cost = None
        self.update_status_bar()

    def update_grid_by_algo_run(self, successors):
        # set node color
        # self.grid[node[1]][node[0]] = VISU_DICT["VISITED"]

        successors = [
            s for s in successors]

        for s in successors:
            self.display_grid[s[1]][s[0]] = VISU_DICT["SUCCESSOR"]


def main():
    root = tk.Tk()
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    gui = Frame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
