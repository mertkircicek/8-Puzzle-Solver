import heapq

class PriorityQueue:
    """A priority queue implementation for A* search"""
    
    def __init__(self):
        self.elements = []
        self.count = 0  # Tie-breaker for equal priorities
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        # Add count as a tie-breaker and to make the queue stable
        entry = (priority, self.count, item)
        heapq.heappush(self.elements, entry)
        self.count += 1
    
    def get(self):
        # Return the item (3rd element in the tuple)
        return heapq.heappop(self.elements)[2]
    
    def __contains__(self, item):
        for _, _, element in self.elements:
            if element == item:
                return True
        return False

def astar(start, goal, heuristic):

    # Initialize the frontier with the start state
    frontier = PriorityQueue()
    frontier.put(start, 0)
    
    # To keep track of parent states and actions that led to them
    parent = {start.to_tuple(): (None, None)}
    
    # To keep track of the cost to reach each state
    cost_so_far = {start.to_tuple(): 0}
    
    # Counter for number of nodes expanded
    expansions = 0
    
    while not frontier.empty():
        # Get the state with the lowest f(n) = g(n) + h(n)
        current = frontier.get()
        expansions += 1
        
        # Check if we've reached the goal
        if current == goal:
            # Reconstruct the path
            path = []
            while parent[current.to_tuple()][0] is not None:
                path.append(parent[current.to_tuple()][1])
                current = parent[current.to_tuple()][0]
            path.reverse()
            return path, expansions
        
        # Explore all possible next states
        for action, next_state in current.get_successors():
            # Calculate new cost to reach this state
            new_cost = cost_so_far[current.to_tuple()] + 1
            
            # If this state is new or we found a better path to it
            if next_state.to_tuple() not in cost_so_far or new_cost < cost_so_far[next_state.to_tuple()]:
                # Update the cost
                cost_so_far[next_state.to_tuple()] = new_cost
                
                # Calculate priority using the heuristic
                priority = new_cost + heuristic(next_state, goal)
                
                # Add to frontier
                frontier.put(next_state, priority)
                
                # Remember how we got to this state
                parent[next_state.to_tuple()] = (current, action)
    
    # If we've exhausted the frontier without finding a goal, there's no solution
    return [], expansions