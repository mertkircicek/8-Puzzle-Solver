class PuzzleState:
    """
    Class representing a state of the n-puzzle game.
    The board is represented as a 2D list where 0 represents the empty space.
    """
    def __init__(self, board, size):
        """
        Initialize a puzzle state with the given board configuration
            board: 2D list representing the puzzle state
            size: Size of the puzzle (3, 5, 7, ... for 8-puzzle)
        """
        self.board = [row[:] for row in board]  # Create a deep copy of the board
        self.size = size
        self.empty_pos = self._find_empty_position()
    
    def _find_empty_position(self):
        """Find the position of the empty tile (0)"""
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return (i, j)
        raise ValueError("No empty position (0) found in the puzzle board")
    
    def move_up(self):
        """
        Move the empty tile up if possible
        Returns a new state if the move is valid, None otherwise
        """
        row, col = self.empty_pos
        if row == 0:  # Can't move up if already at the top row
            return None
            
        # Create a new state with the same board
        new_state = PuzzleState(self.board, self.size)
        
        # Swap the empty tile with the tile above it
        new_state.board[row][col], new_state.board[row-1][col] = new_state.board[row-1][col], new_state.board[row][col]
        
        # Update the empty position
        new_state.empty_pos = (row-1, col)
        
        return new_state
    
    def move_down(self):
        """
        Move the empty tile down if possible
        Returns a new state if the move is valid, None otherwise
        """
        row, col = self.empty_pos
        if row == self.size - 1:  # Can't move down if already at the bottom row
            return None
            
        # Create a new state with the same board
        new_state = PuzzleState(self.board, self.size)
        
        # Swap the empty tile with the tile below it
        new_state.board[row][col], new_state.board[row+1][col] = new_state.board[row+1][col], new_state.board[row][col]
        
        # Update the empty position
        new_state.empty_pos = (row+1, col)
        
        return new_state
    
    def move_left(self):
        """
        Move the empty tile left if possible
        Returns a new state if the move is valid, None otherwise
        """
        row, col = self.empty_pos
        if col == 0:  # Can't move left if already at the leftmost column
            return None
            
        # Create a new state with the same board
        new_state = PuzzleState(self.board, self.size)
        
        # Swap the empty tile with the tile to its left
        new_state.board[row][col], new_state.board[row][col-1] = new_state.board[row][col-1], new_state.board[row][col]
        
        # Update the empty position
        new_state.empty_pos = (row, col-1)
        
        return new_state
    
    def move_right(self):
        """
        Move the empty tile right if possible
        Returns a new state if the move is valid, None otherwise
        """
        row, col = self.empty_pos
        if col == self.size - 1:  # Can't move right if already at the rightmost column
            return None
            
        # Create a new state with the same board
        new_state = PuzzleState(self.board, self.size)
        
        # Swap the empty tile with the tile to its right
        new_state.board[row][col], new_state.board[row][col+1] = new_state.board[row][col+1], new_state.board[row][col]
        
        # Update the empty position
        new_state.empty_pos = (row, col+1)
        
        return new_state
    
    def get_successors(self):
        """
        Get all possible next states by trying all valid moves
        Returns a list of (action, state) pairs
        """
        successors = []
        
        # Try all four possible moves
        up_state = self.move_up()
        if up_state:
            successors.append(("Up", up_state))
            
        down_state = self.move_down()
        if down_state:
            successors.append(("Down", down_state))
            
        left_state = self.move_left()
        if left_state:
            successors.append(("Left", left_state))
            
        right_state = self.move_right()
        if right_state:
            successors.append(("Right", right_state))
            
        return successors
    
    def __eq__(self, other):
        """Check if two puzzle states are equal"""
        if not isinstance(other, PuzzleState):
            return False
        return self.board == other.board
    
    def __hash__(self):
        """Hash function for using PuzzleState in sets and as dictionary keys"""
        return hash(self.to_tuple())
    
    def to_tuple(self):
        """Convert the board to a tuple of tuples for hashing"""
        return tuple(tuple(row) for row in self.board)
    
    def __str__(self):
        """String representation of the puzzle state"""
        result = ""
        for row in self.board:
            result += " ".join(str(x) for x in row) + "\n"
        return result