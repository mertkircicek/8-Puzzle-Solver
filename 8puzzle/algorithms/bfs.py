from collections import deque

def bfs(start, goal, max_depth=None):
    """
    Breadth-first search algorithm to find a path from start to goal state.
    
    Args:
        start: Starting state object
        goal: Goal state object
        max_depth: Maximum search depth (optional)
    
    Returns:
        tuple: (path, expansions) where:
            - path is a list of actions to reach the goal
            - expansions is the number of nodes expanded during search
    """
    # Initialize the FIFO queue with the start state and its depth (0)
    queue = deque([(start, 0)])
    
    # Set to track visited states
    visited = set([start.to_tuple()])
    
    # Dictionary to store parent states and actions
    parent = {start.to_tuple(): (None, None)}
    
    # Counter for nodes expanded
    expansions = 0
    
    # BFS loop
    while queue:
        # Get the next state and its depth from the queue
        state, depth = queue.popleft()
        expansions += 1
        
        # Goal check
        if state == goal:
            # Reconstruct path
            path = []
            current = state
            while parent[current.to_tuple()][0] is not None:
                path.append(parent[current.to_tuple()][1])
                current = parent[current.to_tuple()][0]
            path.reverse()
            return path, expansions
        
        # If max_depth is specified and we've reached it, skip expansion
        if max_depth is not None and depth >= max_depth:
            continue
        
        # Explore all possible next states
        for action, next_state in state.get_successors():
            next_tuple = next_state.to_tuple()
            
            # Only explore unvisited states
            if next_tuple not in visited:
                visited.add(next_tuple)
                parent[next_tuple] = (state, action)
                queue.append((next_state, depth + 1))
    
    # No solution found
    return [], expansions