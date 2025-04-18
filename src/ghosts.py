import heapq
import threading
import time
import random
from collections import deque

class Ghost(threading.Thread):
    def __init__(self, maze, start, goal, algorithm, color):
        threading.Thread.__init__(self)
        self.maze = maze
        self.position = start
        self.goal = goal
        self.algorithm = algorithm
        self.color = color
        self.path = []
        self.running = True
        self.daemon = True
        self.last_goal = None  # Lưu mục tiêu trước đó để kiểm tra thay đổi

    def run(self):
        while self.running:
            # Tính toán lại đường đi nếu mục tiêu thay đổi hoặc không có đường đi
            if self.goal != self.last_goal or not self.path:
                self.last_goal = self.goal
                if self.goal != self.position:
                    self.path = self.algorithm(self.maze, self.position, self.goal)
                else:
                    self.path = None
            
            # Di chuyển theo đường đi nếu có
            if self.path and len(self.path) > 1:
                next_pos = self.path[1]
                if not self.maze.is_wall(next_pos):
                    self.position = next_pos
                    self.path = self.path[1:]
                else:
                    self.path = None  # Reset nếu đường đi không hợp lệ
            else:
                # Di chuyển ngẫu nhiên nếu không có đường đi
                neighbors = self.maze.get_valid_moves(self.position)
                if neighbors:
                    self.position = random.choice(neighbors)
                self.path = None
            
            time.sleep(0.3)  # Làm chậm ma quỷ để game dễ hơn (trước là 0.05)

    def stop(self):
        self.running = False

# Search Algorithms
def bfs(maze, start, goal):
    queue = deque([(start, [start])])
    visited = set([start])
    
    while queue:
        current, path = queue.popleft()
        
        if current == goal:
            return path
            
        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None

def dfs(maze, start, goal):
    stack = [(start, None)]
    parent_map = {start: None}
    visited = {start}
    
    while stack:
        current, _ = stack.pop()
        
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent_map[current]
            return path[::-1]
        
        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent_map[neighbor] = current
                stack.append((neighbor, current))
    
    return None

def ucs(maze, start, goal):
    heap = []
    heapq.heappush(heap, (0, start, [start]))
    visited = set()
    
    while heap:
        cost, current, path = heapq.heappop(heap)
        
        if current == goal:
            return path
            
        if current in visited:
            continue
            
        visited.add(current)
        
        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                new_cost = cost + 1
                heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))
    
    return None

def a_star(maze, start, goal):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    heap = []
    heapq.heappush(heap, (0 + heuristic(start, goal), 0, start, [start]))
    visited = set()
    
    while heap:
        _, cost, current, path = heapq.heappop(heap)
        
        if current == goal:
            return path
            
        if current in visited:
            continue
            
        visited.add(current)
        
        for neighbor in maze.get_valid_moves(current):
            if neighbor not in visited:
                new_cost = cost + 1
                heapq.heappush(
                    heap, 
                    (new_cost + heuristic(neighbor, goal), 
                    new_cost, 
                    neighbor, 
                    path + [neighbor])
                )
    
    return None