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

def draw_maze(maze, pacman, ghosts, score, level):
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
    pygame.draw.circle(screen, YELLOW, 
                      (pacman.position[0] * CELL_SIZE + CELL_SIZE//2, 
                       pacman.position[1] * CELL_SIZE + CELL_SIZE//2), 
                      CELL_SIZE//2 - 2)

    # Draw ghosts
    for ghost in ghosts:
        pygame.draw.circle(screen, ghost.color, 
                          (ghost.position[0] * CELL_SIZE + CELL_SIZE//2, 
                           ghost.position[1] * CELL_SIZE + CELL_SIZE//2), 
                          CELL_SIZE//2 - 2)

    # Draw score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))

    pygame.display.flip()

def draw_game_over(score, level):
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
    screen.fill(BLACK)
    
    title = title_font.render("PAC-MAN SEARCH ALGORITHMS", True, YELLOW)
    subtitle = font.render("Select a level to start:", True, WHITE)
    
    level1 = font.render("1. Blue Ghost (BFS) - Pac-Man fixed", True, BLUE)
    level2 = font.render("2. Pink Ghost (DFS) - Pac-Man fixed", True, PINK)
    level3 = font.render("3. Orange Ghost (UCS) - Pac-Man fixed", True, ORANGE)
    level4 = font.render("4. Red Ghost (A*) - Pac-Man fixed", True, RED)
    level5 = font.render("5. All Ghosts - Pac-Man fixed", True, WHITE)
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
    maze = Maze(20, 20)
    pacman = PacMan((1, 1))
    score = 0
    ghosts = []
    pacman_controlled = (level == 6)  # Only controllable in level 6
    
    if level == 1:
        ghosts.append(Ghost(maze, (10, 10), pacman, bfs, BLUE))
    elif level == 2:
        ghosts.append(Ghost(maze, (10, 10), pacman, dfs, PINK))
    elif level == 3:
        ghosts.append(Ghost(maze, (10, 10), pacman, ucs, ORANGE))
    elif level == 4:
        ghosts.append(Ghost(maze, (10, 10), pacman, a_star, RED))
    elif level == 5:
        ghosts.extend([
            Ghost(maze, (10, 10), pacman, bfs, BLUE),
            Ghost(maze, (10, 1), pacman, dfs, PINK),
            Ghost(maze, (1, 10), pacman, ucs, ORANGE),
            Ghost(maze, (5, 5), pacman, a_star, RED)
        ])
    elif level == 6:
        ghosts.extend([
            Ghost(maze, (10, 10), pacman, bfs, BLUE),
            Ghost(maze, (10, 1), pacman, dfs, PINK),
            Ghost(maze, (1, 10), pacman, ucs, ORANGE),
            Ghost(maze, (5, 5), pacman, a_star, RED)
        ])
    
    for ghost in ghosts:
        ghost.start()
    
    return maze, pacman, ghosts, score, pacman_controlled

def main():
    current_level = 0  # 0 means level selection screen
    maze = None
    pacman = None
    ghosts = []
    score = 0
    game_over = False
    running = True
    pacman_controlled = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_level == 0:
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
                elif game_over:
                    if event.key == pygame.K_r:
                        current_level = 0
                        game_over = False
                        for ghost in ghosts:
                            ghost.stop()
                            ghost.join()
                    elif event.key == pygame.K_q:
                        running = False
                elif pacman_controlled:  # Only handle movement in level 6
                    old_position = pacman.position
                    if event.key == pygame.K_UP:
                        pacman.move((0, -1), maze)
                    elif event.key == pygame.K_DOWN:
                        pacman.move((0, 1), maze)
                    elif event.key == pygame.K_LEFT:
                        pacman.move((-1, 0), maze)
                    elif event.key == pygame.K_RIGHT:
                        pacman.move((1, 0), maze)
                    
                    if pacman.position in maze.dots:
                        maze.dots.remove(pacman.position)
                        score += 10
        
        if current_level == 0:
            draw_level_selection()
        else:
            if not game_over:
                # Continuous collision check
                for ghost in ghosts:
                    if pacman.position == ghost.position:
                        game_over = True
                        break
            
            if game_over:
                draw_game_over(score, current_level)
            else:
                draw_maze(maze, pacman, ghosts, score, current_level)
        
        clock.tick(10)
    
    # Clean up
    for ghost in ghosts:
        ghost.stop()
        ghost.join()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()