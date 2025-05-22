import time
import random
import statistics
import threading
from logic.puzzle_state import PuzzleState
from algorithms.astar import astar
from heuristics.manhattan import heuristic_manhattan

class TimeoutError(Exception):
    pass

def generate_random_puzzle(size, distance_from_goal=20):
    goal_board = [[(i * size + j + 1) % (size * size) for j in range(size)] for i in range(size)]
    state = PuzzleState(goal_board, size)
    moves_made = 0
    previous_states = set()
    previous_states.add(tuple(map(tuple, state.board)))

    while moves_made < distance_from_goal:
        successors = state.get_successors()
        if not successors:
            break
        new_successors = [(move, new_state) for move, new_state in successors 
                          if tuple(map(tuple, new_state.board)) not in previous_states]
        if not new_successors and successors:
            _, state = random.choice(successors)
        elif new_successors:
            _, state = random.choice(new_successors)
        else:
            break
        previous_states.add(tuple(map(tuple, state.board)))
        moves_made += 1

    return state.board, moves_made

def run_with_timeout(func, args, timeout):
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        raise TimeoutError()
    if exception[0] is not None:
        raise exception[0]
    return result[0]

def run_experiment(size, distance_from_goal, num_trials, timeout):
    results = {
        'time': [],
        'nodes_expanded': [],
        'path_length': [],
        'actual_distances': [],
        'timeouts': 0,
        'errors': 0
    }

    for trial in range(num_trials):
        try:
            print(f"\nTrial {trial + 1}/{num_trials} for {size}x{size} puzzle with target distance {distance_from_goal}")
            print("Generating puzzle...")
            start_board, actual_distance = generate_random_puzzle(size, distance_from_goal)
            start_state = PuzzleState(start_board, size)

            goal_board = [[(i * size + j + 1) % (size * size) for j in range(size)] for i in range(size)]
            goal_state = PuzzleState(goal_board, size)

            print(f"Generated puzzle with actual distance: {actual_distance}")
            results['actual_distances'].append(actual_distance)

            print("Starting A* search...")
            start_time = time.time()
            path, expansions = run_with_timeout(astar, (start_state, goal_state, heuristic_manhattan), timeout)
            end_time = time.time()

            results['time'].append(end_time - start_time)
            results['nodes_expanded'].append(expansions)
            results['path_length'].append(len(path))

            print(f"[OK] Path length: {len(path)} | Nodes: {expansions} | Time: {end_time - start_time:.2f}s")

        except TimeoutError:
            results['timeouts'] += 1
            print(f"[TIMEOUT] Trial timed out after {timeout} seconds")
        except Exception as e:
            results['errors'] += 1
            print(f"[ERROR] {str(e)}")

    stats = {
        'avg_time': statistics.mean(results['time']) if results['time'] else float('inf'),
        'std_time': statistics.stdev(results['time']) if len(results['time']) > 1 else 0,
        'avg_nodes': statistics.mean(results['nodes_expanded']) if results['nodes_expanded'] else float('inf'),
        'std_nodes': statistics.stdev(results['nodes_expanded']) if len(results['nodes_expanded']) > 1 else 0,
        'avg_path': statistics.mean(results['path_length']) if results['path_length'] else float('inf'),
        'std_path': statistics.stdev(results['path_length']) if len(results['path_length']) > 1 else 0,
        'avg_distance': statistics.mean(results['actual_distances']) if results['actual_distances'] else 0,
        'timeouts': results['timeouts'],
        'errors': results['errors'],
        'success_rate': (num_trials - results['timeouts'] - results['errors']) / num_trials if num_trials > 0 else 0
    }

    return stats

def format_stat_with_ascii(value, std):
    if value == float('inf'):
        return "Timeout"
    if std > 0:
        return f"{value:.3f} (+/-){std:.3f}"
    return f"{value:.3f}"

def main():
    print("A* Search Experiment with Manhattan Distance Heuristic")
    print("======================================================")

    sizes = [3, 5, 7]
    distances = {3: 15, 5: 25, 7: 30}
    trials = {3: 10, 5: 5, 7: 3}
    timeouts = {3: 10, 5: 60, 7: 180}

    all_stats = {}

    for size in sizes:
        print(f"\n--- Testing {size}x{size} puzzle ---")
        stats = run_experiment(size, distances[size], trials[size], timeouts[size])
        all_stats[size] = stats

        print(f"\nResults for {size}x{size} puzzle:")
        print(f"Success rate: {stats['success_rate']*100:.1f}%")
        if stats['timeouts'] > 0:
            print(f"Timeouts: {stats['timeouts']}/{trials[size]}")
        if stats['errors'] > 0:
            print(f"Errors: {stats['errors']}/{trials[size]}")

        print(f"Average distance from goal: {stats['avg_distance']:.1f}")
        if stats['avg_time'] != float('inf'):
            print(f"Avg Time: {stats['avg_time']:.2f} (+/-){stats['std_time']:.2f} sec")
            print(f"Avg Nodes: {stats['avg_nodes']:.0f} (+/-){stats['std_nodes']:.0f}")
            print(f"Avg Path Length: {stats['avg_path']:.1f} (+/-){stats['std_path']:.1f}")
        else:
            print("No successful trials")

    print("\nComparison Summary")
    print("==================")
    print("Size | Success Rate  | Distance  |     Time          |    Nodes            |  Path Length")
    print("-----|---------------|-----------|-------------------|---------------------|--------------")
    for size in sizes:
        s = all_stats[size]
        if s['avg_time'] != float('inf'):
            time_str = format_stat_with_ascii(s['avg_time'], s['std_time'])
            nodes_str = format_stat_with_ascii(s['avg_nodes'], s['std_nodes'])
            path_str = format_stat_with_ascii(s['avg_path'], s['std_path'])

            print(f"{size}x{size}  |     {s['success_rate']*100:.0f}%      |    {int(s['avg_distance'])}     |  {time_str:<12} | {nodes_str:<11}  |    {path_str}")
        else:
            print(f"{size}x{size}  |     {s['success_rate']*100:.0f}%      |    {int(s['avg_distance'])}     |    Timeout     |    Timeout    |    Timeout")

if __name__ == "__main__":
    main()
