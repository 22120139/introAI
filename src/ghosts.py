import heapq
import threading
import time
import random
from collections import deque

class Ghost(threading.Thread):
    def __init__(self, maze, start, goal, algorithm, color):
        super().__init__()
        self.maze = maze
        self.position = start
        self.goal = goal
        self.algorithm = algorithm
        self.color = color
        self.path = []
        self.running = True
        self.daemon = True
        self.last_goal = None
        self.lock = threading.Lock()  # Tránh conflict đa luồng

    def run(self):
        while self.running:
            with self.lock:
                # Nếu mục tiêu thay đổi hoặc path không còn hợp lệ thì tính lại
                if self.goal != self.last_goal or not self.path:
                    self.last_goal = self.goal
                    if self.goal != self.position:
                        new_path = self.algorithm(self.maze, self.position, self.goal)
                        # Nếu thuật toán không tìm được đường, ghost sẽ random
                        if new_path and len(new_path) > 1:
                            self.path = new_path
                        else:
                            self.path = []

                # Di chuyển nếu có đường đi
                if self.path and len(self.path) > 1:
                    next_pos = self.path[1]
                    # Kiểm tra lại tính hợp lệ (tường có thể thay đổi)
                    if not self.maze.is_wall(next_pos):
                        self.position = next_pos
                        self.path = self.path[1:]
                    else:
                        # Nếu vị trí tiếp theo là tường, reset lại đường
                        self.path = []
                else:
                    # Di chuyển ngẫu nhiên nếu không có đường hợp lệ
                    neighbors = self.maze.get_valid_moves(self.position)
                    if neighbors:
                        self.position = random.choice(neighbors)
                    self.path = []

            time.sleep(0.3)  # Delay để ghost không di chuyển quá nhanh

    def update_goal(self, new_goal):
        """Cập nhật mục tiêu mới an toàn."""
        with self.lock:
            self.goal = new_goal

    def stop(self):
        """Dừng thread ghost."""
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