import heapq
import threading
import time
import random
from collections import deque

class Ghost(threading.Thread):
    def __init__(self, maze, start, goal, algorithm, color, ghosts=None):
        super().__init__()
        self.maze = maze
        self.position = start
        self.goal = goal
        self.algorithm = algorithm
        self.color = color
        self.ghosts = ghosts
        self.path = []
        self.running = True
        self.daemon = True
        self.last_goal = None
        self.lock = threading.Lock()

    def is_position_occupied(self, position):
        if self.ghosts is None:
            return False
        for other_ghost in self.ghosts:
            if other_ghost != self:
                with other_ghost.lock:
                    if other_ghost.position == position:
                        print(f"Ghost {self.color}: Position {position} occupied by {other_ghost.color}")
                        return True
        return False

    def run(self):
        while self.running:
            with self.lock:
                if self.goal != self.last_goal or not self.path:
                    self.last_goal = self.goal
                    if self.goal != self.position:
                        path, expanded = self.algorithm(self.maze, self.position, self.goal)
                        if path and len(path) > 1:
                            self.path = path
                            print(f"Ghost {self.color}: New path to {self.goal}, nodes expanded: {expanded}")
                        else:
                            self.path = []
                            print(f"Ghost {self.color}: No valid path to {self.goal}")
                    else:
                        self.path = []
                        print(f"Ghost {self.color}: Already at goal {self.goal}")

            moved = False
            if self.path and len(self.path) > 1:
                next_pos = self.path[1]
                if not self.maze.is_wall(next_pos) and not self.is_position_occupied(next_pos):
                    with self.lock:
                        self.position = next_pos
                        self.path = self.path[1:]
                        moved = True
                        print(f"Ghost {self.color}: Moved to {self.position}")
                else:
                    print(f"Ghost {self.color}: Cannot move to {next_pos} (wall or occupied)")
                    if len(self.path) > 2:
                        for i in range(2, min(len(self.path), 4)):
                            alt_pos = self.path[i]
                            if not self.maze.is_wall(alt_pos) and not self.is_position_occupied(alt_pos):
                                with self.lock:
                                    self.position = alt_pos
                                    self.path = self.path[i:]
                                    moved = True
                                    print(f"Ghost {self.color}: Moved to alternative {self.position}")
                                    break
                    if not moved:
                        self.path = []

            if not moved:
                neighbors = self.maze.get_valid_moves(self.position)
                valid_neighbors = [n for n in neighbors if not self.is_position_occupied(n)]
                if valid_neighbors:
                    with self.lock:
                        self.position = random.choice(valid_neighbors)
                        print(f"Ghost {self.color}: Random move to {self.position}")
                else:
                    print(f"Ghost {self.color}: No valid moves from {self.position}")

            time.sleep(0.3)

    def update_goal(self, new_goal):
        with self.lock:
            self.goal = new_goal

    def stop(self):
        self.running = False

# Search Algorithms (trả về: path, expanded_nodes)

def bfs(maze, start, goal):
    queue = deque([(start, [start])])
    visited = set([start])
    expanded = 0

    while queue:
        current, path = queue.popleft()
        expanded += 1

        if current == goal:
            return path, expanded

        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None, expanded

def dfs(maze, start, goal):
    stack = [(start, None)]
    parent_map = {start: None}
    visited = {start}
    expanded = 0

    while stack:
        current, _ = stack.pop()
        expanded += 1

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent_map[current]
            return path[::-1], expanded

        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent_map[neighbor] = current
                stack.append((neighbor, current))

    return None, expanded

def ucs(maze, start, goal):
    heap = [(0, start, [start])]
    visited = set()
    expanded = 0

    while heap:
        cost, current, path = heapq.heappop(heap)
        expanded += 1

        if current == goal:
            return path, expanded

        if current in visited:
            continue
        visited.add(current)

        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                heapq.heappush(heap, (cost + 1, neighbor, path + [neighbor]))

    return None, expanded

def a_star(maze, start, goal):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    heap = [(heuristic(start, goal), 0, start, [start])]
    visited = set()
    expanded = 0

    while heap:
        _, cost, current, path = heapq.heappop(heap)
        expanded += 1

        if current == goal:
            return path, expanded

        if current in visited:
            continue
        visited.add(current)

        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                g = cost + 1
                f = g + heuristic(neighbor, goal)
                heapq.heappush(heap, (f, g, neighbor, path + [neighbor]))

    return None, expanded
