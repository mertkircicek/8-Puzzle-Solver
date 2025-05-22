def depth_limited_search(start, goal, depth_limit):
    """
    Depth-limited search 
    
        start: The initial PuzzleState
        goal: The goal PuzzleState
        depth_limit: Maximum depth to explore
    
    """
    # Stack to keep track of states to explore (state, depth)
    stack = [(start, 0)]
    
    # Set to keep track of visited states
    visited = set()
    
    # To keep track of parent states and actions that led to them
    # Key: state tuple, Value: (parent state, action)
    parent = {start.to_tuple(): (None, None)}
    
    # Counter for number of nodes expanded
    expansions = 0
    
    while stack:
        # Get the next state and its depth from the stack
        state, depth = stack.pop()
        
        # Skip if we've already visited this state
        if state.to_tuple() in visited:
            continue
            
        # Mark this state as visited
        visited.add(state.to_tuple())
        
        # Increment expansion counter
        expansions += 1
        
        # Check if we've reached the goal
        if state == goal:
            # Reconstruct the path
            path = []
            current = state
            while parent[current.to_tuple()][0] is not None:
                path.append(parent[current.to_tuple()][1])
                current = parent[current.to_tuple()][0]
            path.reverse()
            return path, expansions, True
        
        # If we haven't reached the maximum depth, explore further
        if depth < depth_limit:
            # Get successors (possible next states) in reverse order for DFS
            successors = state.get_successors()
            successors.reverse()  # Reverse to explore right-to-left first
            
            for action, successor in successors:
                successor_tuple = successor.to_tuple()
                # Only add states we haven't seen before
                if successor_tuple not in parent:
                    # Remember how we got to this state
                    parent[successor_tuple] = (state, action)
                    # Add to stack for exploration
                    stack.append((successor, depth + 1))
    
    # If we've exhausted the stack without finding a goal at this depth
    return [], expansions, False


def ids(start, goal, max_depth=50):
    """
    Iterative Deepening Search algorithm 
    
        start: The initial PuzzleState
        goal: The goal PuzzleState
        max_depth: Maximum depth to explore
    
    """
    total_expansions = 0
    
    # Iteratively increase the depth limit
    for depth in range(max_depth + 1):
        path, expansions, found = depth_limited_search(start, goal, depth)
        total_expansions += expansions
        
        if found:
            return path, total_expansions
    
    # If no solution found within max_depth
    return [], total_expansions