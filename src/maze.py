import numpy as np

class Maze:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = self.generate_maze()
        self.dots = self.generate_dots()
        
    def generate_maze(self):
        """Generate a simple maze with walls around borders and random internal walls"""
        grid = np.zeros((self.height, self.width))
        
        # Border walls
        grid[0, :] = 1
        grid[-1, :] = 1
        grid[:, 0] = 1
        grid[:, -1] = 1
        
        # Add some random internal walls (20% of space)
        for i in range(1, self.height-1):
            for j in range(1, self.width-1):
                if np.random.random() < 0.2:
                    grid[i, j] = 1
                    
        return grid
    
    def generate_dots(self):
        """Generate dots in all non-wall cells, excluding Pac-Man and ghost starting positions"""
        dots = []
        # Exclude starting positions of Pac-Man and ghosts
        excluded_positions = [(1, 1), (10, 10), (10, 1), (1, 10), (5, 5)]
        
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_wall((x, y)) and (x, y) not in excluded_positions:
                    dots.append((x, y))
                    
        return dots
    
    def is_wall(self, position):
        x, y = position
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.grid[y, x] == 1
    
    def get_valid_moves(self, position):
        """Get all valid moves from current position"""
        x, y = position
        moves = []
        
        # Check four directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                if not self.is_wall((new_x, new_y)):
                    moves.append((new_x, new_y))
                    
        return moves
    
    def print_maze(self, pacman=None, ghosts=None):
        """Print maze to console (for debugging)"""
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if pacman and (x, y) == pacman.position:
                    row.append('P')
                elif ghosts and any((x, y) == ghost.position for ghost in ghosts):
                    for ghost in ghosts:
                        if (x, y) == ghost.position:
                            row.append(ghost.color[0].upper())
                            break
                elif self.is_wall((x, y)):
                    row.append('#')
                elif (x, y) in self.dots:
                    row.append('.')
                else:
                    row.append(' ')
            print(' '.join(row))