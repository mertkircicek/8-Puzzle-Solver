def misplaced_tiles(state, goal):
    """
    Misplaced tiles heuristic - counts the number of tiles not in their goal position.
    
        state: Current PuzzleState
        goal: Goal PuzzleState
    
    Returns:
        Number of misplaced tiles
    """
    count = 0
    for i in range(state.size):
        for j in range(state.size):
            # Skip the empty tile (0)
            if state.board[i][j] != 0 and state.board[i][j] != goal.board[i][j]:
                count += 1
    return count