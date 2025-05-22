def heuristic_manhattan(state, goal):
    """
    Manhattan distance heuristic - sum of the Manhattan distances of each tile from its goal position.
    
        state: Current PuzzleState
        goal: Goal PuzzleState
    
    Returns:
        Sum of Manhattan distances
    """
    total_distance = 0
    
    # Create a mapping of values to their goal positions for quick lookup
    goal_positions = {}
    for i in range(goal.size):
        for j in range(goal.size):
            goal_positions[goal.board[i][j]] = (i, j)
    
    # Calculate Manhattan distance for each tile
    for i in range(state.size):
        for j in range(state.size):
            if state.board[i][j] != 0:  # Skip the empty tile
                # Find where this tile should be
                goal_i, goal_j = goal_positions[state.board[i][j]]
                # Add the Manhattan distance
                total_distance += abs(i - goal_i) + abs(j - goal_j)
    
    return total_distance