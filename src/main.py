import pygame
import sys
from maze import Maze
from pacman import PacMan
from ghosts import Ghost, bfs, dfs, ucs, a_star
from utils import run_tests, print_results

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Search Algorithms")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 182, 193)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
WALL_COLOR = (0, 0, 128)
GREEN = (0, 255, 0)

# Font
font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("arial", 36)

# Load and scale Pac-Man image
try:
    pacman_image = pygame.image.load("images/pacman.png").convert_alpha()
    # Scale image to match the size of the original Pac-Man (CELL_SIZE - 4 to match the circle size)
    pacman_image = pygame.transform.scale(pacman_image, (CELL_SIZE - 4, CELL_SIZE - 4))
except FileNotFoundError:
    pacman_image = None
    print("Pac-Man image not found, falling back to default circle.")

# Load ghost images (scaled to fit CELL_SIZE - 4)
def load_ghost_image(filename):
    try:
        img = pygame.image.load(f"images/{filename}").convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE - 4, CELL_SIZE - 4))
    except FileNotFoundError:
        print(f"{filename} not found, using colored circle fallback.")
        return None

ghost_images = {
    BLUE: load_ghost_image("blue_ghost.png"),
    PINK: load_ghost_image("pink_ghost.png"),
    ORANGE: load_ghost_image("orange_ghost.png"),
    RED: load_ghost_image("red_ghost.png"),
}


# Sounds
try:
    eat_dot_sound = pygame.mixer.Sound("sounds/eat_dot.wav")
    game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")
except FileNotFoundError:
    eat_dot_sound = None
    game_over_sound = None

def draw_maze(maze, pacman, ghosts, score, level):
    """Draw the maze, Pac-Man, ghosts, dots, walls, score, level, and quit instruction."""
    screen.fill(BLACK)
    # Draw dots
    for dot in maze.dots:
        pygame.draw.circle(screen, WHITE, 
                          (dot[0] * CELL_SIZE + CELL_SIZE//2, 
                           dot[1] * CELL_SIZE + CELL_SIZE//2), 
                          CELL_SIZE//8)
    # Draw walls
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.is_wall((x, y)):
                pygame.draw.rect(screen, WALL_COLOR, 
                                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw Pac-Man
    if pacman_image:
        # Calculate position to center the image
        pacman_rect = pacman_image.get_rect(center=(
            pacman.position[0] * CELL_SIZE + CELL_SIZE//2,
            pacman.position[1] * CELL_SIZE + CELL_SIZE//2
        ))
        screen.blit(pacman_image, pacman_rect)
    else:
        # Fallback to default circle if image is not available
        pygame.draw.circle(screen, YELLOW, 
                          (pacman.position[0] * CELL_SIZE + CELL_SIZE//2, 
                           pacman.position[1] * CELL_SIZE + CELL_SIZE//2), 
                          CELL_SIZE//2 - 2)
    # Draw ghosts
    for ghost in ghosts:
        ghost_img = ghost_images.get(ghost.color)
        if ghost_img:
            ghost_rect = ghost_img.get_rect(center=(
                ghost.position[0] * CELL_SIZE + CELL_SIZE // 2,
                ghost.position[1] * CELL_SIZE + CELL_SIZE // 2
            ))
            screen.blit(ghost_img, ghost_rect)
        else:
            pygame.draw.circle(screen, ghost.color,
                            (ghost.position[0] * CELL_SIZE + CELL_SIZE // 2,
                            ghost.position[1] * CELL_SIZE + CELL_SIZE // 2),
                            CELL_SIZE // 2 - 2)

    # Draw score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (655, 40))
    screen.blit(level_text, (655, 70))
    # Draw quit instruction
    quit_text = font.render("Press Q to Quit", True, WHITE)
    screen.blit(quit_text, (WIDTH - quit_text.get_width() - 10, 10))
    pygame.display.flip()

def draw_game_over(score, level):
    """Display game over screen with final score and level."""
    screen.fill(BLACK)
    game_over_text = title_font.render("Game Over!", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    level_text = font.render(f"Level Reached: {level}", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 70))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
    screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 20))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 70))
    pygame.display.flip()

def draw_level_selection():
    """Display level selection screen."""
    screen.fill(BLACK)
    title = title_font.render("PAC-MAN SEARCH ALGORITHMS", True, YELLOW)
    subtitle = font.render("Select a level to start:", True, WHITE)
    level1 = font.render("1. Blue Ghost (BFS) - Pac-Man stationary", True, BLUE)
    level2 = font.render("2. Pink Ghost (DFS) - Pac-Man stationary", True, PINK)
    level3 = font.render("3. Orange Ghost (UCS) - Pac-Man stationary", True, ORANGE)
    level4 = font.render("4. Red Ghost (A*) - Pac-Man stationary", True, RED)
    level5 = font.render("5. All Ghosts - Pac-Man stationary", True, WHITE)
    level6 = font.render("6. All Ghosts - Player controls Pac-Man", True, GREEN)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 120))
    screen.blit(level1, (WIDTH//2 - level1.get_width()//2, 180))
    screen.blit(level2, (WIDTH//2 - level2.get_width()//2, 220))
    screen.blit(level3, (WIDTH//2 - level3.get_width()//2, 260))
    screen.blit(level4, (WIDTH//2 - level4.get_width()//2, 300))
    screen.blit(level5, (WIDTH//2 - level5.get_width()//2, 340))
    screen.blit(level6, (WIDTH//2 - level6.get_width()//2, 380))
    pygame.display.flip()

def initialize_game(level):
    """Initialize game state for the given level."""
    maze = Maze(20, 20)
    pacman = PacMan((1, 1))
    score = 0
    ghosts = []
    pacman_controlled = (level == 6)
    
    # Tạo ma quỷ trước
    if level == 1:
        ghosts.append(Ghost(maze, (10, 10), pacman.position, bfs, BLUE))
    elif level == 2:
        ghosts.append(Ghost(maze, (10, 10), pacman.position, dfs, PINK))
    elif level == 3:
        ghosts.append(Ghost(maze, (10, 10), pacman.position, ucs, ORANGE))
    elif level == 4:
        ghosts.append(Ghost(maze, (10, 10), pacman.position, a_star, RED))
    elif level == 5:
        ghosts.extend([
            Ghost(maze, (10, 10), pacman.position, bfs, BLUE),
            Ghost(maze, (10, 1), pacman.position, dfs, PINK),
            Ghost(maze, (1, 10), pacman.position, ucs, ORANGE),
            Ghost(maze, (5, 5), pacman.position, a_star, RED)
        ])
    elif level == 6:
        ghosts.extend([
            Ghost(maze, (10, 10), pacman.position, bfs, BLUE),
            Ghost(maze, (10, 1), pacman.position, dfs, PINK),
            Ghost(maze, (1, 10), pacman.position, ucs, ORANGE),
            Ghost(maze, (5, 5), pacman.position, a_star, RED)
        ])
    
    # Truyền danh sách ghosts vào mỗi Ghost để kiểm tra chồng nhau
    for ghost in ghosts:
        ghost.ghosts = ghosts
        ghost.start()
    
    return maze, pacman, ghosts, score, pacman_controlled

def main():
    """Main game loop for Pac-Man Search Algorithms."""
    # Run performance tests if --test flag is provided
    if '--test' in sys.argv:
        maze = Maze(20, 20)
        algorithms = {
            'BFS': bfs,
            'DFS': dfs,
            'UCS': ucs,
            'A*': a_star
        }
        results = run_tests(maze, algorithms)
        print_results(results)
        pygame.quit()
        sys.exit()

    # Initialize game state
    current_level = 0  # 0 means level selection screen
    maze = None
    pacman = None
    ghosts = []
    score = 0
    game_over = False
    pacman_controlled = False
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_level == 0:  # Level selection
                    if event.key == pygame.K_1:
                        current_level = 1
                        maze, pacman, ghosts, score, pacman_controlled = initialize_game(1)
                    elif event.key == pygame.K_2:
                        current_level = 2
                        maze, pacman, ghosts, score, pacman_controlled = initialize_game(2)
                    elif event.key == pygame.K_3:
                        current_level = 3
                        maze, pacman, ghosts, score, pacman_controlled = initialize_game(3)
                    elif event.key == pygame.K_4:
                        current_level = 4
                        maze, pacman, ghosts, score, pacman_controlled = initialize_game(4)
                    elif event.key == pygame.K_5:
                        current_level = 5
                        maze, pacman, ghosts, score, pacman_controlled = initialize_game(5)
                    elif event.key == pygame.K_6:
                        current_level = 6
                        maze, pacman, ghosts, score, pacman_controlled = initialize_game(6)
                    elif event.key == pygame.K_q:
                        running = False
                elif game_over:  # Game over screen
                    if event.key == pygame.K_r:
                        current_level = 0
                        game_over = False
                        for ghost in ghosts:
                            ghost.stop()
                            ghost.join()
                        ghosts = []
                        maze = None
                        pacman = None
                        score = 0
                        pacman_controlled = False
                    elif event.key == pygame.K_q:
                        running = False
                else:  # In-game
                    if event.key == pygame.K_q:
                        # Return to level selection menu
                        current_level = 0
                        game_over = False
                        for ghost in ghosts:
                            ghost.stop()
                            ghost.join()
                        ghosts = []
                        maze = None
                        pacman = None
                        score = 0
                        pacman_controlled = False
                    elif pacman_controlled:  # Pac-Man movement (level 6)
                        old_position = pacman.position
                        if event.key == pygame.K_UP:
                            pacman.move((0, -1), maze)
                        elif event.key == pygame.K_DOWN:
                            pacman.move((0, 1), maze)
                        elif event.key == pygame.K_LEFT:
                            pacman.move((-1, 0), maze)
                        elif event.key == pygame.K_RIGHT:
                            pacman.move((1, 0), maze)
                        # Check for eating dots
                        if pacman.position in maze.dots:
                            maze.dots.remove(pacman.position)
                            score += 10
                            if eat_dot_sound:
                                eat_dot_sound.play()

        # Update game state
        if current_level == 0:
            draw_level_selection()
        else:
            if not game_over:
                # Update ghost goals to chase Pac-Man
                for ghost in ghosts:
                    ghost.goal = pacman.position
                # Check for collisions
                for ghost in ghosts:
                    if pacman.position == ghost.position:
                        game_over = True
                        if game_over_sound:
                            game_over_sound.play()
                        break
                # Draw game
                draw_maze(maze, pacman, ghosts, score, current_level)
            else:
                draw_game_over(score, current_level)

        # Control frame rate (20 FPS for level 6, 15 FPS for others)
        if current_level == 6:
            clock.tick(20)
        else:
            clock.tick(15)

    # Clean up
    for ghost in ghosts:
        ghost.stop()
        ghost.join()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()