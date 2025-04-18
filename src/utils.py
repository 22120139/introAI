import time
import psutil
import os

def measure_performance(algorithm, maze, start, goal):
    """Measure search algorithm performance"""
    process = psutil.Process(os.getpid())
    
    # Memory before
    mem_before = process.memory_info().rss / 1024  # KB
    
    # Time and path finding
    start_time = time.time()
    path = algorithm(maze, start, goal)
    elapsed = time.time() - start_time
    
    # Memory after
    mem_after = process.memory_info().rss / 1024  # KB
    
    return {
        'time_ms': elapsed * 1000,
        'memory_kb': mem_after - mem_before,
        'path_length': len(path) if path else 0,
        'success': path is not None
    }

def run_tests(maze, algorithms):
    """Run performance tests for all algorithms"""
    test_cases = [
        ((1, 1), (18, 18)),
        ((1, 18), (18, 1)),
        ((5, 5), (15, 15)),
        ((2, 10), (18, 10)),
        ((10, 2), (10, 18))
    ]
    
    results = {}
    
    for name, algorithm in algorithms.items():
        results[name] = []
        for start, goal in test_cases:
            result = measure_performance(algorithm, maze, start, goal)
            results[name].append(result)
    
    return results

def print_results(results):
    """Print test results in a readable format"""
    for algo, tests in results.items():
        print(f"\n{algo} Results:")
        print("Test | Time (ms) | Memory (KB) | Path Length | Success")
        for i, test in enumerate(tests, 1):
            print(f"{i:4} | {test['time_ms']:8.2f} | {test['memory_kb']:10.2f} | "
                  f"{test['path_length']:11} | {test['success']}")