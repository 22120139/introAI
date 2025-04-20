import random
import time
import psutil
import os
import pygame
from collections import deque
import numpy as np

CELL_SIZE = 25
WALL_COLOR = (40, 40, 40)
PATH_COLOR = (240, 240, 240)
PACMAN_COLOR = (255, 255, 0)
GHOST_COLOR = (255, 0, 0)
VISITED_COLOR = (200, 200, 255)
EXPANDED_COLOR = (180, 255, 180)  # Color for expanded nodes visualization

def generate_valid_positions(maze, min_distance):
    """Generate random start and goal positions that are reachable and sufficiently far apart"""
    while True:
        # Get all walkable positions excluding borders and walls
        walkable = []
        for y in range(1, maze.height-1):
            for x in range(1, maze.width-1):
                if not maze.is_wall((x, y)):
                    walkable.append((x, y))
        
        if len(walkable) < 2:
            raise ValueError("Maze doesn't have enough walkable spaces")
        
        # Randomly select start and goal
        start, goal = random.sample(walkable, 2)
        
        # Check Manhattan distance
        distance = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
        if distance >= min_distance and maze.has_path(maze.grid, start, goal):
            return start, goal

def draw_test_case(maze, pacman_pos, ghost_pos, path=None, expanded=None):
    """Visualize the maze with optional path and expanded nodes"""
    pygame.init()
    width = maze.width * CELL_SIZE
    height = maze.height * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Test Case Viewer")

    # Draw maze
    for y in range(maze.height):
        for x in range(maze.width):
            color = WALL_COLOR if maze.is_wall((x, y)) else PATH_COLOR
            pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw expanded nodes if provided
    if expanded:
        for node in expanded:
            pygame.draw.rect(screen, EXPANDED_COLOR, 
                           (node[0]*CELL_SIZE, node[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw path if provided
    if path:
        for i, (x, y) in enumerate(path):
            pygame.draw.rect(screen, VISITED_COLOR, 
                           (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if i != 0 and i != len(path)-1:
                font = pygame.font.SysFont(None, 20)
                text = font.render(str(i), True, (0, 0, 0))
                screen.blit(text, (x*CELL_SIZE+8, y*CELL_SIZE+5))

    # Draw Pac-Man and Ghost
    pygame.draw.circle(screen, PACMAN_COLOR, 
                      (pacman_pos[0]*CELL_SIZE+CELL_SIZE//2, 
                       pacman_pos[1]*CELL_SIZE+CELL_SIZE//2), 
                      CELL_SIZE//2-3)
    pygame.draw.circle(screen, GHOST_COLOR, 
                      (ghost_pos[0]*CELL_SIZE+CELL_SIZE//2, 
                       ghost_pos[1]*CELL_SIZE+CELL_SIZE//2), 
                      CELL_SIZE//2-4)

    pygame.display.flip()

class NodeCounter:
    """Helper class to track node expansions during search"""
    def __init__(self):
        self.count = 0
        self.expanded_nodes = set()
    
    def increment(self, node):
        self.count += 1
        self.expanded_nodes.add(node)

def measure_performance(algorithm, maze, start, goal):
    """
    Measure algorithm performance with node expansion tracking
    Returns:
        dict: Performance metrics including expanded nodes count
    """
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024
    
    # Create counter for node expansions
    counter = NodeCounter()
    
    # Create a wrapper around get_valid_moves to count expansions
    original_get_moves = maze.get_valid_moves
    def counting_get_moves(pos):
        counter.increment(pos)
        return original_get_moves(pos)
    
    # Temporarily replace the method
    maze.get_valid_moves = counting_get_moves
    
    start_time = time.time()
    path = algorithm(maze, start, goal)
    elapsed = time.time() - start_time
    mem_after = process.memory_info().rss / 1024
    
    # Restore original method
    maze.get_valid_moves = original_get_moves
    
    return {
        'time_ms': elapsed * 1000,
        'memory_kb': mem_after - mem_before,
        'path_length': len(path) if path else 0,
        'success': path is not None,
        'expanded_nodes': counter.count,
        'path': path,
        'expanded_set': counter.expanded_nodes
    }

def run_tests(maze, algorithms, num_tests=5):
    """Run randomized tests with visualization and node expansion tracking"""
    # Calculate minimum distance based on maze size
    min_distance = (maze.width + maze.height) // 3
    
    all_results = {name: [] for name in algorithms}
    
    for test_num in range(1, num_tests+1):
        print(f"\n🎲 Test {test_num}/{num_tests}")
        start, goal = generate_valid_positions(maze, min_distance)
        print(f"🧪 From {start} to {goal}")
        
        # Show initial state
        draw_test_case(maze, start, goal)
        print("👉 Press any key to run algorithms...")
        wait_for_keypress()
        
        result_table = []
        
        for name, algorithm in algorithms.items():
            result = measure_performance(algorithm, maze, start, goal)
            all_results[name].append(result)
            result_table.append({
                'name': name,
                'time_ms': result['time_ms'],
                'memory_kb': result['memory_kb'],
                'path_length': result['path_length'],
                'expanded_nodes': result['expanded_nodes'],
                'success': result['success']
            })
            
            # Visualize expanded nodes and path
            if result['success']:
                draw_test_case(maze, start, goal, result['path'], result['expanded_set'])
                caption = (f"{name} (Path: {result['path_length']}, "
                         f"Expanded: {result['expanded_nodes']})")
                pygame.display.set_caption(caption)
                time.sleep(1)
                wait_for_keypress()
        
        pygame.display.quit()
        
        # Print results table
        print("\nAlgorithm | Time (ms) | Memory (KB) | Path Len | Expanded | Success")
        for r in result_table:
            print(f"{r['name']:<9} | {r['time_ms']:8.2f} | {r['memory_kb']:10.2f} | "
                  f"{r['path_length']:8} | {r['expanded_nodes']:8} | {r['success']}")
    
    return all_results

def print_results(results):
    """Print comprehensive final summary with expanded nodes statistics"""
    print("\n📊 FINAL SUMMARY")
    print("="*70)
    
    stats = {}
    for algo, tests in results.items():
        times = [t['time_ms'] for t in tests]
        memories = [t['memory_kb'] for t in tests]
        expansions = [t['expanded_nodes'] for t in tests]
        lengths = [t['path_length'] for t in tests if t['success']]
        
        stats[algo] = {
            'avg_time': sum(times)/len(times),
            'max_time': max(times),
            'avg_mem': sum(memories)/len(memories),
            'avg_expanded': sum(expansions)/len(expansions),
            'max_expanded': max(expansions),
            'success_rate': sum(1 for t in tests if t['success'])/len(tests)*100,
            'avg_len': sum(lengths)/len(lengths) if lengths else 0
        }
    
    print("\nPerformance Comparison:")
    print("Algorithm | Avg Time | Max Time | Avg Mem | Avg Expanded | Max Expanded | Success | Avg Len")
    for algo, data in stats.items():
        print(f"{algo:<9} | {data['avg_time']:8.2f} | {data['max_time']:8.2f} | "
              f"{data['avg_mem']:7.1f} | {data['avg_expanded']:12} | {data['max_expanded']:11} | "
              f"{data['success_rate']:6.1f}% | {data['avg_len']:7.2f}")

def wait_for_keypress():
    """Wait for any key press"""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False