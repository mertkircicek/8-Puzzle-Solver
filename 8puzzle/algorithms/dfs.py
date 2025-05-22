def dfs(start, goal, max_depth=50):
    
    # Stack to keep track of states to explore (state, depth)
    stack = [(start, 0)]
    
    # Set to keep track of explored states
    explored = set()
    
    # To keep track of parent states and actions that led to them
    parent = {start.to_tuple(): (None, None)}
    
    # Counter for number of nodes expanded
    expansions = 0
    
    while stack:
        # Get the next state and its depth from the stack
        state, depth = stack.pop()
        
        # Increment expansion counter
        expansions += 1
        
        # Check if we've reached the goal
        if state == goal:
            # Reconstruct the path
            path = []
            while parent[state.to_tuple()][0] is not None:
                path.append(parent[state.to_tuple()][1])
                state = parent[state.to_tuple()][0]
            path.reverse()
            return path, expansions
        
        # Mark the current state as explored
        explored.add(state.to_tuple())
        
        # If we haven't reached the maximum depth, explore further
        if depth < max_depth:
            # Get successors (possible next states) in reverse order for DFS
            successors = state.get_successors()
            successors.reverse()  # Reverse to explore right-to-left first
            
            for action, successor in successors:
                # If this state hasn't been seen before
                if successor.to_tuple() not in explored:
                    # Remember how we got to this state
                    parent[successor.to_tuple()] = (state, action)
                    # Add to stack for exploration
                    stack.append((successor, depth + 1))
    
    # There is no solution
    return [], expansions