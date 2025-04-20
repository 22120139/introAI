import time
import psutil
import os
import pygame

CELL_SIZE = 25
WALL_COLOR = (40, 40, 40)
PATH_COLOR = (240, 240, 240)
PACMAN_COLOR = (255, 255, 0)
GHOST_COLOR = (255, 0, 0)


def wait_for_keypress():
    """Chờ người dùng nhấn phím bất kỳ để tiếp tục"""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False


def draw_test_case(maze, pacman_pos, ghost_positions):
    """Hiển thị bản đồ đơn giản với Pac-Man và Ghosts"""
    pygame.init()
    grid = maze.grid
    width = len(grid[0]) * CELL_SIZE
    height = len(grid) * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Test Case Viewer")

    # Vẽ bản đồ
    for y in range(maze.height):
        for x in range(maze.width):
            color = WALL_COLOR if maze.is_wall((x, y)) else PATH_COLOR
            pygame.draw.rect(screen, color, pygame.Rect(
                x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE
            ))

    # Vẽ Pac-Man
    pygame.draw.circle(screen, PACMAN_COLOR, (
        pacman_pos[0] * CELL_SIZE + CELL_SIZE // 2,
        pacman_pos[1] * CELL_SIZE + CELL_SIZE // 2
    ), CELL_SIZE // 2 - 3)

    # Vẽ Ghosts
    for ghost_pos in ghost_positions:
        pygame.draw.circle(screen, GHOST_COLOR, (
            ghost_pos[0] * CELL_SIZE + CELL_SIZE // 2,
            ghost_pos[1] * CELL_SIZE + CELL_SIZE // 2
        ), CELL_SIZE // 2 - 4)

    pygame.display.flip()


def measure_performance(algorithm, maze, start, goal):
    """Đo hiệu suất thuật toán tìm kiếm"""
    process = psutil.Process(os.getpid())

    mem_before = process.memory_info().rss / 1024
    start_time = time.time()
    path, expanded_nodes = algorithm(maze, start, goal)
    elapsed = time.time() - start_time
    mem_after = process.memory_info().rss / 1024

    return {
        'time_ms': elapsed * 1000,
        'memory_kb': mem_after - mem_before,
        'path_length': len(path) if path else 0,
        'expanded_nodes': expanded_nodes,
        'success': path is not None
    }



def run_tests(maze, algorithms):
    """Chạy các test case. Mỗi test vẽ bản đồ, nhấn phím rồi chạy TẤT CẢ thuật toán và in bảng"""
    test_cases = [
        ((1, 1), (18, 18)),
        ((1, 18), (18, 1)),
        ((5, 5), (15, 15)),
        ((2, 10), (18, 10)),
        ((10, 2), (10, 18))
    ]

    all_results = {name: [] for name in algorithms}

    for idx, (start, goal) in enumerate(test_cases, 1):
        print(f"\n🧪 Test {idx}: From {start} to {goal}")

        draw_test_case(maze, start, [goal])
        print("👉 Nhấn phím bất kỳ để chạy các thuật toán...")
        wait_for_keypress()

        result_table = []

        for name, algorithm in algorithms.items():
            result = measure_performance(algorithm, maze, start, goal)
            all_results[name].append(result)
            result_table.append({
                'name': name,
                **result
            })

        pygame.display.quit()

        # In bảng
        print("Algo | Time (ms) | Memory (KB) | Path Length | Expanded Nodes | Success")
        for r in result_table:
            print(f"{r['name']:<5} | {r['time_ms']:9.2f} | {r['memory_kb']:10.2f} | "
                f"{r['path_length']:11} | {r['expanded_nodes']:14} | {r['success']}")


    return all_results


def print_results(results):
    """In bảng tổng hợp cuối cùng (nếu muốn)"""
    for algo, tests in results.items():
        print(f"\n📊 Tổng kết cho {algo}:")
        print("Test | Time (ms) | Memory (KB) | Path Length | Expanded Nodes | Success")
        for i, test in enumerate(tests, 1):
            print(f"{i:4} | {test['time_ms']:8.2f} | {test['memory_kb']:10.2f} | "
                f"{test['path_length']:11} | {test['expanded_nodes']:14} | {test['success']}")

