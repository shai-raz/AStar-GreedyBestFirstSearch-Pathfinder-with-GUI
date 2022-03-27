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


def get_manhattan_distance(pos, goal):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


def get_successors(node, grid, size):
    successors = []
    x, y = node.x, node.y

    if (x + 1 < size) and (grid[y][x + 1] != MAP_DICT["WATER"]):
        successors.append((x + 1, y))

    if (x - 1 >= 0) and (grid[y][x - 1] != MAP_DICT["WATER"]):
        successors.append((x - 1, y))

    if (y + 1 < size) and (grid[y + 1][x] != MAP_DICT["WATER"]):
        successors.append((x, y + 1))

    if (y - 1 >= 0) and (grid[y - 1][x] != MAP_DICT["WATER"]):
        successors.append((x, y - 1))

    return successors


def get_path(node, grid):
    path = []
    cost = 0
    while node is not None:
        path.append(node)
        node = node.parent

    path = path[::-1]
    dir_path = []
    for i in range(len(path)-1):
        cost += COST_DICT[grid[path[i].y][path[i].x]]

        new_x = path[i+1].x - path[i].x
        new_y = path[i+1].y - path[i].y
        if new_x == 1:
            dir_path.append(PATH_DICT["RIGHT"])
        elif new_x == -1:
            dir_path.append(PATH_DICT["LEFT"])
        elif new_y == 1:
            dir_path.append(PATH_DICT["DOWN"])
        elif new_y == -1:
            dir_path.append(PATH_DICT["UP"])

    return '-'.join(dir_path), cost


class Node:
    def __init__(self, x, y, h, cost=0, parent=None):
        self.x = x
        self.y = y
        self.h = h
        self.g = cost + parent.g if parent else 0
        self.f = h+self.g
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f


class GreedyBestFirstSearch:
    def __init__(self, grid, size):
        self.grid = [row[:] for row in grid]  # deep copy
        self.size = size

        self.start, self.end = find_start_and_end(grid)

    def get_successors(self, node):
        return get_successors(node, self.grid, self.size)

    def get_heuristic(self, pos):
        return get_manhattan_distance(pos, self.end)

    def get_path_cost(self, node):
        cost = 0
        while node is not None:
            cost += COST_DICT[self.grid[node.y][node.x]]
            node = node.parent

        return cost

    def run(self, q=None):
        opened = []
        closed = []

        h = self.get_heuristic(self.start)
        heappush(opened, Node(self.start[0], self.start[1], h))

        while len(opened) > 0:
            # set current node
            node = heappop(opened)
            closed.append(node)

            # if the current node is the end node, return the path
            if node.x == self.end[0] and node.y == self.end[1]:
                q.put(("end", node, self.get_path_cost(node)))
                return

            # get successors
            successors = self.get_successors(node)

            if q is not None:
                q.put((node, successors))

            for successor in successors:
                inOpened = False
                inClosed = False

                # check if in opened
                for i in range(len(opened)):
                    if opened[i].x == successor[0] and opened[i].y == successor[1]:
                        inOpened = True
                        break

                # check if in closed
                for i in range(len(closed)):
                    if closed[i].x == successor[0] and closed[i].y == successor[1]:
                        inClosed = True
                        break

                if not inOpened and not inClosed:
                    heappush(opened, Node(successor[0], successor[1],
                                          self.get_heuristic(successor), parent=node))

        return False


class AStar:
    def __init__(self, grid, size):
        self.grid = [row[:] for row in grid]  # deep copy
        self.size = size
        self.start, self.end = find_start_and_end(grid)

    def get_successors(self, node):
        return get_successors(node, self.grid, self.size)

    def get_heuristic(self, pos):
        return get_manhattan_distance(pos, self.end)

    def run(self, q=None):
        opened = []
        closed = []

        h = self.get_heuristic(self.start)
        node = Node(self.start[0], self.start[1], h)
        heappush(opened, node)

        while len(opened) > 0:
            # set current node
            node = heappop(opened)
            closed.append(node)

            # if the current node is the end node, return the path
            if node.x == self.end[0] and node.y == self.end[1]:
                q.put(("end", node, node.g))
                return True

            # get successors
            successors = self.get_successors(node)

            if q is not None:
                q.put((node, successors))

            for successor in successors:
                h = self.get_heuristic(successor)
                cost = COST_DICT[self.grid[successor[1]][successor[0]]]
                successor = Node(successor[0], successor[1], h, cost, node)

                inOpened = False
                inClosed = False

                for i in range(len(opened)):
                    if opened[i].x == successor.x and opened[i].y == successor.y:
                        inOpened = True
                        if opened[i].f > successor.f:
                            opened[i] = successor
                            break

                for i in range(len(closed)):
                    if closed[i].x == successor.x and closed[i].y == successor.y:
                        inClosed = True
                        if closed[i].f > successor.f:
                            closed[i] = successor
                            break

                if not inOpened and not inClosed:
                    heappush(opened, successor)

        return False


def read_file(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        algorithm, size, input_mat = lines[0].strip(
        ), lines[1].strip(), lines[2:]

    size = int(size)
    grid = [[letter for letter in row.strip()] for row in input_mat]

    return algorithm, size, grid