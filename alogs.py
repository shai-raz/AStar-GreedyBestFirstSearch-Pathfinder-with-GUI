import sys
from heapq import heappush, heappop
from time import sleep
import threading
from multiprocessing import Queue


MAP_DICT = {
    "STARTING_POINT": 'A',
    "ENDING_POINT": 'B',
    "WATER": 'W',
    "PAVED_ROAD": 'R',
    "NON_PAVED_ROAD": 'D',
}

COST_DICT = {
    "A": 0,
    "B": 0,
    "R": 1,
    "D": 4,
}

PATH_DICT = {
    "UP": 'U',
    "DOWN": 'D',
    "LEFT": 'L',
    "RIGHT": 'R'
}


def find_start_and_end(grid):
    start, end = None, None
    for j, row in enumerate(grid):
        for i, cell in enumerate(row):
            if cell == MAP_DICT["STARTING_POINT"]:
                start = (i, j)
            elif cell == MAP_DICT["ENDING_POINT"]:
                end = (i, j)

    return start, end


def get_manhattan_distance(node, goal):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])


def get_successors(node, closed, grid, size):
    successors = []
    x, y = node[0], node[1]

    if (x + 1 < size) and (grid[y][x + 1] != MAP_DICT["WATER"]) and ((x+1, y) not in closed):
        successors.append((x + 1, y))

    if (x - 1 >= 0) and (grid[y][x - 1] != MAP_DICT["WATER"]) and ((x-1, y) not in closed):
        successors.append((x - 1, y))

    if (y + 1 < size) and (grid[y + 1][x] != MAP_DICT["WATER"]) and ((x, y+1) not in closed):
        successors.append((x, y + 1))

    if (y - 1 >= 0) and (grid[y - 1][x] != MAP_DICT["WATER"]) and ((x, y-1) not in closed):
        successors.append((x, y - 1))

    return successors


def is_ancestor(node, child, parents):
    """checks if the child is an ancestor of the node"""
    while node is not None:
        if node == child:
            return True
        node = parents[node]


class GreedyBestFirstSearch:
    closed = []

    def __init__(self, grid, size):
        self.grid = [row[:] for row in grid]  # deep copy
        self.size = size

        self.start, self.end = find_start_and_end(grid)

    def get_successors(self, node, closed):
        return get_successors(node, closed, self.grid, self.size)

    def get_heuristic(self, node):
        return get_manhattan_distance(node, self.end)

    def get_path(self, node, parents):
        path = []
        cost = 0
        while node is not None:
            path.append(node)
            node = parents[node]

        path = path[::-1]
        dir_path = []
        for i in range(len(path)-1):
            cost += COST_DICT[self.grid[path[i][1]][path[i][0]]]

            new_x = path[i+1][0] - path[i][0]
            new_y = path[i+1][1] - path[i][1]
            if new_x == 1:
                dir_path.append(PATH_DICT["RIGHT"])
            elif new_x == -1:
                dir_path.append(PATH_DICT["LEFT"])
            elif new_y == 1:
                dir_path.append(PATH_DICT["DOWN"])
            elif new_y == -1:
                dir_path.append(PATH_DICT["UP"])

        return '-'.join(dir_path), cost

    def run(self, q=None):
        opened = []
        closed = []

        # dictionary to store parents (to get the path), key = node, value = parent
        parents = {}
        parents[self.start] = None

        heappush(opened, (self.get_heuristic(self.start), self.start))

        while len(opened) > 0:
            # set current node
            node = heappop(opened)[1]
            closed.append(node)

            # if the current node is the end node, return the path
            if node == self.end:
                path, cost = self.get_path(node, parents)
                q.put(("end", node, parents, cost))
                return path, cost

            # get successors
            successors = self.get_successors(node, closed)

            if q is not None:
                q.put((node, parents, successors))

            for successor in successors:
                h = self.get_heuristic(successor)
                if (h, successor) not in opened:
                    heappush(opened, (h, successor))
                    parents[successor] = node

        return "no path", 0


class AStar:
    def __init__(self, grid, size):
        self.grid = [row[:] for row in grid]  # deep copy
        self.size = size
        self.start, self.end = find_start_and_end(grid)

    def get_successors(self, node):
        return get_successors(node, [], self.grid, self.size)

    def get_heuristic(self, node):
        return get_manhattan_distance(node, self.end)

    def get_g(self, node, parents):
        g = 0
        while node is not None:
            g += COST_DICT[self.grid[node[1]][node[0]]]
            node = parents[node]
        return g

    def get_path(self, node, parents):
        path = []
        cost = 0
        while node is not None:
            path.append(node)
            node = parents[node]

        path = path[::-1]
        dir_path = []
        for i in range(len(path)-1):
            cost += COST_DICT[self.grid[path[i][1]][path[i][0]]]

            new_x = path[i+1][0] - path[i][0]
            new_y = path[i+1][1] - path[i][1]
            if new_x == 1:
                dir_path.append(PATH_DICT["RIGHT"])
            elif new_x == -1:
                dir_path.append(PATH_DICT["LEFT"])
            elif new_y == 1:
                dir_path.append(PATH_DICT["DOWN"])
            elif new_y == -1:
                dir_path.append(PATH_DICT["UP"])

        return '-'.join(dir_path), cost

    def run(self, q=None):
        opened = []
        closed = []

        # dictionary to store parents (to get the path), key = node, value = parent
        parents = {}
        parents[self.start] = None

        heappush(opened, (self.get_heuristic(self.start), self.start))

        while len(opened) > 0:
            sleep(0.0001)
            # set current node
            node = heappop(opened)[1]
            closed.append(node)

            # if the current node is the end node, return the path
            if node == self.end:
                path, cost = self.get_path(node, parents)
                q.put(("end", node, parents, cost))
                return path, cost

            # get successors
            successors = self.get_successors(node)

            if q is not None:
                successors = [
                    successor for successor in successors
                    if successor not in closed
                    and successor not in opened]
                q.put((node, parents, successors))

            for successor in successors:
                # make sure the child isnt an ancestor of the node,
                # to avoid infinite looping
                if is_ancestor(node, successor, parents):
                    continue
                new_parents = parents.copy()
                new_parents[successor] = node
                g = self.get_g(successor, new_parents)
                h = self.get_heuristic(successor)
                f = g + h
                if (f, successor) not in opened and successor not in closed:
                    heappush(opened, (f, successor))
                    parents[successor] = node
                else:
                    # find the node in the opened list
                    for i in range(len(opened)):
                        if opened[i][1] == successor:
                            # if the new f value is smaller, update the node
                            if f < opened[i][0]:
                                opened[i] = (f, successor)
                                parents[successor] = node
                                break

        return "no path", 0


def read_file(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        algorithm, size, input_mat = lines[0].strip(
        ), lines[1].strip(), lines[2:]

    size = int(size)
    grid = [[letter for letter in row.strip()] for row in input_mat]

    return algorithm, size, grid


def main():
    if (len(sys.argv) != 2):
        print('Usage: py assignment1.py <input_file>')
        exit(1)

    file_name = sys.argv[1]

    algorithm, size, grid = read_file(file_name)

    # presenting the input
    print(f"Running {algorithm} on {size}x{size} matrix: ")
    for row in grid:
        for letter in row:
            print(f"{letter} ", end='')
        print()

    path = ""
    cost = 0

    # running the alogrithm
    if algorithm == 'A*':
        astar = AStar(grid, size)
        path, cost = astar.run()
    elif algorithm == 'greedyBestFirst':
        gbs = GreedyBestFirstSearch(grid, size)
        path, cost = gbs.run()

    print("path: ", path)
    print("cost: ", cost)

    with(open("output.txt", "w+")) as f:
        if path == "no path":
            f.write("no path")
        else:
            f.write(path + " " + str(cost))


if __name__ == '__main__':
    main()
