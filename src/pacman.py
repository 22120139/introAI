class PacMan:
    def __init__(self, position):
        self.position = position
        self.score = 0
        
    def move(self, direction, maze):
        """Move Pac-Man in the specified direction if valid"""
        dx, dy = direction
        x, y = self.position
        new_x, new_y = x + dx, y + dy
        
        # Check if new position is valid
        if not maze.is_wall((new_x, new_y)):
            self.position = (new_x, new_y)
            return True
        return False