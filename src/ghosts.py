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
        self.ghosts = ghosts  # Danh sách tất cả ma quỷ để kiểm tra chồng nhau
        self.path = []
        self.running = True
        self.daemon = True
        self.last_goal = None
        self.lock = threading.Lock()  # Tránh conflict đa luồng

    def is_position_occupied(self, position):
        """Kiểm tra xem vị trí có bị ma quỷ khác chiếm không."""
        if self.ghosts is None:
            return False
        for other_ghost in self.ghosts:
            if other_ghost != self:
                with other_ghost.lock:  # Khóa trên đối tượng khác
                    if other_ghost.position == position:
                        print(f"Ghost {self.color}: Position {position} occupied by {other_ghost.color}")
                        return True
        return False

    def run(self):
        """Luồng chính của ma quỷ: tính đường đi và di chuyển."""
        while self.running:
            # Cập nhật đường đi nếu mục tiêu thay đổi hoặc path không còn hợp lệ
            with self.lock:
                if self.goal != self.last_goal or not self.path:
                    self.last_goal = self.goal
                    if self.goal != self.position:
                        new_path = self.algorithm(self.maze, self.position, self.goal)
                        if new_path and len(new_path) > 1:
                            self.path = new_path
                            print(f"Ghost {self.color}: New path calculated to {self.goal}: {self.path}")
                        else:
                            self.path = []
                            print(f"Ghost {self.color}: No valid path to {self.goal}")
                    else:
                        self.path = []
                        print(f"Ghost {self.color}: Already at goal {self.goal}")

            # Di chuyển nếu có đường đi
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
                    # Thử các ô khác trong path nếu có
                    if len(self.path) > 2:
                        for i in range(2, min(len(self.path), 4)):  # Kiểm tra tối đa 3 ô tiếp theo
                            alt_pos = self.path[i]
                            if not self.maze.is_wall(alt_pos) and not self.is_position_occupied(alt_pos):
                                with self.lock:
                                    self.position = alt_pos
                                    self.path = self.path[i:]
                                    moved = True
                                    print(f"Ghost {self.color}: Moved to alternative {self.position}")
                                    break
                    if not moved:
                        self.path = []  # Reset path để tính lại

            # Di chuyển ngẫu nhiên nếu không có đường đi hoặc không di chuyển được
            if not moved:
                neighbors = self.maze.get_valid_moves(self.position)
                valid_neighbors = [n for n in neighbors if not self.is_position_occupied(n)]
                if valid_neighbors:
                    with self.lock:
                        self.position = random.choice(valid_neighbors)
                        moved = True
                        print(f"Ghost {self.color}: Random move to {self.position}")
                else:
                    print(f"Ghost {self.color}: No valid moves from {self.position}")

            time.sleep(0.3)  # Delay để ghost không di chuyển quá nhanh

    def update_goal(self, new_goal):
        """Cập nhật mục tiêu mới an toàn."""
        with self.lock:
            self.goal = new_goal

    def stop(self):
        """Dừng thread ghost."""
        self.running = False

# Search Algorithms (giữ nguyên)
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