"""!!! To reach the application interface and solve the puzzle, the gui.py code must be run."""

import time  
import sys
import os
import threading
import queue
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
from logic.puzzle_state import PuzzleState

def is_solvable(board_flat):
    inv_count = 0
    for i in range(len(board_flat)):
        for j in range(i + 1, len(board_flat)):
            if board_flat[i] and board_flat[j] and board_flat[i] > board_flat[j]:
                inv_count += 1
    return inv_count % 2 == 0

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI 8-Puzzle Solver")

        self.size = 3  # 3x3 puzzle at the beginning
        self.algorithm = tk.StringVar(value="Breadth First Search")
        self.iteration = 0

        self.board = [
            [3, 4, 6],
            [1, 0, 8],
            [7, 2, 5]
        ]
       #Initially there will be this puzzle, but with each click of the "Random" button the puzzle will change.
        
        self.solution_path = []
        self.current_solution_step = 0
        self.running = False
        self.paused = False
        self.search_thread = None
        self.solution_queue = queue.Queue()
        self.update_queue = queue.Queue()  # Queue for iteration updates
        
        # Track if we're in tile setup mode
        self.setup_mode = False
        self.selected_tile = None

        self.create_widgets()
        self.draw_puzzle()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)
        
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=10)
        
        # Algorithm selection
        algo_frame = tk.LabelFrame(left_frame, text="Algorithm Selection", font=("Helvetica", 12, "bold"))
        algo_frame.pack(pady=10, fill=tk.X)

        self.algo_combo = ttk.Combobox(algo_frame, textvariable=self.algorithm, font=("Helvetica", 12))
        self.algo_combo['values'] = (
            "Breadth First Search",
            "Depth First Search",
            "Iterative Deepening Search",
            "A* - Misplaced",
            "A* - Manhattan"
        )
        self.algo_combo.pack(padx=10, pady=10, ipady=5, fill=tk.X)

        # Control buttons
        button_frame = tk.LabelFrame(left_frame, text="Controls", font=("Helvetica", 12, "bold"))
        button_frame.pack(pady=10, fill=tk.X)

        # Search controls
        search_controls = tk.Frame(button_frame)
        search_controls.pack(pady=5, fill=tk.X)
        
        self.start_button = tk.Button(search_controls, text="Start", bg="green", fg="white", font=("Helvetica", 10, "bold"), command=self.start_search, width=8)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.step_button = tk.Button(search_controls, text="Step", bg="orange", fg="black", font=("Helvetica", 10, "bold"), command=self.step_search, state=tk.DISABLED, width=8)
        self.step_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = tk.Button(search_controls, text="Pause", bg="red", fg="white", font=("Helvetica", 10, "bold"), command=self.pause_search, state=tk.DISABLED, width=8)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Puzzle controls
        puzzle_controls = tk.Frame(button_frame)
        puzzle_controls.pack(pady=5, fill=tk.X)
        
        self.reset_button = tk.Button(puzzle_controls, text="Random", bg="blue", fg="white", font=("Helvetica", 10, "bold"), command=self.reset_puzzle, width=8)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.load_button = tk.Button(puzzle_controls, text="Load File", bg="purple", fg="white", font=("Helvetica", 10, "bold"), command=self.load_puzzle, width=8)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.setup_button = tk.Button(puzzle_controls, text="Setup", bg="teal", fg="white", font=("Helvetica", 10, "bold"), command=self.toggle_setup_mode, width=8)
        self.setup_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Status display area
        status_frame = tk.LabelFrame(left_frame, text="Status", font=("Helvetica", 12, "bold"))
        status_frame.pack(pady=10, fill=tk.X)

        # Iteration display
        self.iteration_label = tk.Label(status_frame, text="Iterations: 0", font=("Helvetica", 12))
        self.iteration_label.pack(pady=5, anchor=tk.W, padx=10)
        
        # Step display
        self.step_label = tk.Label(status_frame, text="Step: 0/0", font=("Helvetica", 12))
        self.step_label.pack(pady=5, anchor=tk.W, padx=10)
        
        # Status label
        self.status_label = tk.Label(status_frame, text="Status: Ready", font=("Helvetica", 12))
        self.status_label.pack(pady=5, anchor=tk.W, padx=10)
        
        # Setup mode label
        self.setup_mode_label = tk.Label(status_frame, text="", font=("Helvetica", 12, "italic"))
        self.setup_mode_label.pack(pady=5, anchor=tk.W, padx=10)

        # Right side - Puzzle area
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, padx=10)
        
        puzzle_frame = tk.LabelFrame(right_frame, text="Puzzle", font=("Helvetica", 12, "bold"))
        puzzle_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(puzzle_frame, width=300, height=300)
        self.canvas.pack(padx=10, pady=10)
        
        # Bind canvas click event for setup mode
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def draw_puzzle(self):
        self.canvas.delete("all")
        cell_size = 100
        for i in range(self.size):
            for j in range(self.size):
                val = self.board[i][j]
                x0, y0 = j * cell_size, i * cell_size
                x1, y1 = x0 + cell_size, y0 + cell_size

                # Different colors for setup mode vs normal mode
                if self.setup_mode:
                    if val == 0:
                        fill_color = "light gray"
                    else:
                        fill_color = "#66bb6a"  # Light green in setup mode
                else:
                    if val == 0:
                        fill_color = "white"
                    else:
                        fill_color = "#4da6ff"  # Normal blue color
                
                # Highlight selected tile in setup mode
                if self.setup_mode and self.selected_tile and self.selected_tile == (i, j):
                    fill_color = "#ffab40"  # Orange highlight for selected tile
                
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline="black", width=2)

                if val != 0:
                    self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=str(val), font=("Helvetica", 24, "bold"), fill="white")
    
    def update_board_from_state(self, state):
        """Update the board from a PuzzleState object"""
        self.board = state.board
        self.draw_puzzle()
    
    def check_updates_queue(self):
        """Check for iteration updates from the algorithm thread"""
        try:
            while True:
                update_type, data = self.update_queue.get_nowait()
                
                if update_type == "iteration":
                    self.iteration = data
                    self.update_iteration()
                elif update_type == "state":
                    self.update_board_from_state(data)
        except queue.Empty:
            # Continue checking if search is running
            if (self.search_thread and self.search_thread.is_alive()) or self.running:
                self.root.after(100, self.check_updates_queue)
    
    def search_algorithm_thread(self):
        """Execute the selected algorithm in a separate thread"""
        algo = self.algorithm.get()
        
        start = PuzzleState(self.board, self.size)
        goal_board = [[(i * self.size + j + 1) % (self.size * self.size) for j in range(self.size)] for i in range(self.size)]
        goal = PuzzleState(goal_board, self.size)
        
        start_time = time.time()
        path = []
        expansions = 0
        
        # Reset iteration counter
        self.update_queue.put(("iteration", 0))
        
        try:
            if algo == "Breadth First Search":
                from algorithms.bfs import bfs
                path, expansions = bfs(start, goal, max_depth=50)
                
            elif algo == "Depth First Search":
                from algorithms.dfs import dfs
                path, expansions = dfs(start, goal, max_depth=50)
    
            elif algo == "Iterative Deepening Search":
                from algorithms.ids import ids
                path, expansions = ids(start, goal, max_depth=50)
    
            elif algo == "A* - Misplaced":
                from algorithms.astar import astar
                from heuristics.misplaced import misplaced_tiles
                path, expansions = astar(start, goal, misplaced_tiles)
    
            elif algo == "A* - Manhattan":
                from algorithms.astar import astar
                from heuristics.manhattan import heuristic_manhattan
                path, expansions = astar(start, goal, heuristic_manhattan)
                
            # Update final iteration count
            self.update_queue.put(("iteration", expansions))
            
        except Exception as e:
            self.solution_queue.put(("error", str(e)))
            return
            
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Put the solution path and statistics in the queue for the main thread to consume
        if path:
            # Reconstruct all states from the path
            states = self.reconstruct_states(start, path)
            self.solution_queue.put(("solution", (states, path, expansions, elapsed_time)))
        else:
            self.solution_queue.put(("no_solution", None))
    
    def check_solution_queue(self):
        """Check for results from the algorithm thread"""
        try:
            result_type, data = self.solution_queue.get_nowait()
            
            if result_type == "solution":
                states, path, expansions, elapsed_time = data
                self.solution_states = states
                self.solution_path = path
                self.current_solution_step = 0
                self.total_solution_steps = len(states)
                
                # Enable stepping through the solution
                self.step_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.DISABLED)
                self.start_button.config(state=tk.NORMAL, text="Auto Play")
                
                # Update status
                self.status_label.config(text=f"Status: Solution found")
                self.step_label.config(text=f"Step: 0/{len(states)-1}")
                
                messagebox.showinfo(
                    self.algorithm.get(),
                    f"Solution found in {len(path)} steps!\n"
                    f"Tiles moved: {len(path)}\n"
                    f"Expanded nodes: {expansions}\n"
                    f"Time: {elapsed_time:.4f} seconds"
                )
                
            elif result_type == "no_solution":
                messagebox.showwarning(self.algorithm.get(), "No solution found.")
                self.reset_buttons()
                self.status_label.config(text="Status: No solution found")
                
            elif result_type == "error":
                messagebox.showerror("Error", f"An error occurred: {data}")
                self.reset_buttons()
                self.status_label.config(text="Status: Error")
                
        except queue.Empty:
            if self.search_thread and self.search_thread.is_alive():
                # Keep checking while the search is ongoing
                self.root.after(100, self.check_solution_queue)
            
    def start_search(self):
        # If solution already found, auto-play through it
        if hasattr(self, 'solution_states') and self.solution_states:
            if self.start_button.cget("text") == "Auto Play":
                self.auto_play_solution()
                return
            elif self.start_button.cget("text") == "Stop":
                # Stop auto-play
                self.running = False
                self.start_button.config(text="Auto Play")
                return
        
        # Start a new search
        self.reset_solution()
        self.status_label.config(text="Status: Searching...")
        
        # Update buttons during search
        self.start_button.config(state=tk.DISABLED)
        self.step_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        # Reset pause state
        self.paused = False
        self.running = True
        
        # Start the search in a separate thread
        self.search_thread = threading.Thread(target=self.search_algorithm_thread)
        self.search_thread.daemon = True
        self.search_thread.start()
        
        # Start checking for results and updates
        self.root.after(100, self.check_solution_queue)
        self.root.after(100, self.check_updates_queue)
    
    def auto_play_solution(self):
        """Auto-play through the solution"""
        if not hasattr(self, 'solution_states') or not self.solution_states:
            return
            
        self.running = True
        self.start_button.config(text="Stop")
        self.step_button.config(state=tk.DISABLED)
        
        def play_next_step():
            if not self.running or self.current_solution_step >= len(self.solution_states) - 1:
                self.running = False
                self.start_button.config(text="Auto Play")
                self.step_button.config(state=tk.NORMAL)
                return
                
            self.current_solution_step += 1
            self.update_board_from_state(self.solution_states[self.current_solution_step])
            self.step_label.config(text=f"Step: {self.current_solution_step}/{len(self.solution_states)-1}")
            
            # Schedule next step after a delay
            self.root.after(500, play_next_step)
            
        play_next_step()
    
    def step_search(self):
        """Step through the solution one move at a time"""
        if not hasattr(self, 'solution_states') or not self.solution_states:
            return
            
        if self.current_solution_step < len(self.solution_states) - 1:
            self.current_solution_step += 1
            self.update_board_from_state(self.solution_states[self.current_solution_step])
            self.step_label.config(text=f"Step: {self.current_solution_step}/{len(self.solution_states)-1}")
            
            # If reached the end, update status
            if self.current_solution_step == len(self.solution_states) - 1:
                self.status_label.config(text="Status: Solution complete")

    def pause_search(self):
        """Pause or resume the search"""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Resume")
            self.status_label.config(text="Status: Paused")
        else:
            self.pause_button.config(text="Pause")
            self.status_label.config(text="Status: Running")

    def reset_puzzle(self):
        """Reset the puzzle to a new random state"""
        nums = list(range(self.size * self.size))
        random.shuffle(nums)

        # If you get a puzzle with no solution, shuffle again.
        while not is_solvable(nums):
            random.shuffle(nums)

        self.board = [nums[i * self.size:(i + 1) * self.size] for i in range(self.size)]
        self.iteration = 0
        self.update_iteration()
        self.draw_puzzle()
        self.reset_solution()
        self.reset_buttons()
        self.status_label.config(text="Status: Ready")

    def reset_solution(self):
        """Reset solution-related variables"""
        if hasattr(self, 'solution_states'):
            del self.solution_states
        self.solution_path = []
        self.current_solution_step = 0
        self.step_label.config(text="Step: 0/0")
    
    def reset_buttons(self):
        """Reset buttons to their default state"""
        self.start_button.config(state=tk.NORMAL, text="Start")
        self.step_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.running = False
        self.paused = False

    def update_iteration(self):
        self.iteration_label.config(text=f"Iterations: {self.iteration}")

    def load_puzzle(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            board = []
            for line in lines:
                board.append([int(x) for x in line.strip().split()])

            # Verify the board is square
            size = len(board)
            for row in board:
                if len(row) != size:
                    raise ValueError("Board must be square")

            # Verify all numbers 0 to size^2-1 are present
            flat_board = [num for row in board for num in row]
            if sorted(flat_board) != list(range(size * size)):
                raise ValueError(f"Board must contain exactly the numbers 0 to {size*size-1}")

            # Check if solvable
            if not is_solvable(flat_board):
                messagebox.showwarning("Warning", "This puzzle configuration is not solvable!")
                return

            self.size = size
            self.board = board
            self.iteration = 0
            self.update_iteration()
            self.draw_puzzle()
            self.reset_solution()
            self.reset_buttons()
            self.status_label.config(text="Status: Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load puzzle: {str(e)}")
    
    def toggle_setup_mode(self):
        """Toggle tile setup mode"""
        self.setup_mode = not self.setup_mode
        self.selected_tile = None
        
        if self.setup_mode:
            self.setup_button.config(bg="orange")
            self.setup_mode_label.config(text="Setup Mode: Click tiles to rearrange")
        else:
            self.setup_button.config(bg="teal")
            self.setup_mode_label.config(text="")
        
        self.draw_puzzle()
    
    def on_canvas_click(self, event):
        """Handle canvas clicks for tile setup"""
        if not self.setup_mode:
            return
            
        # Convert click coordinates to tile position
        cell_size = 100
        row = event.y // cell_size
        col = event.x // cell_size
        
        if 0 <= row < self.size and 0 <= col < self.size:
            if self.selected_tile is None:
                # First click - select a tile
                self.selected_tile = (row, col)
            else:
                # Second click - swap tiles
                r1, c1 = self.selected_tile
                r2, c2 = row, col
                
                # Swap the tiles
                self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]
                
                # Reset selection
                self.selected_tile = None
                
                # Check if puzzle is solvable
                flat_board = [num for row in self.board for num in row]
                if not is_solvable(flat_board):
                    self.status_label.config(text="Warning: Puzzle not solvable!")
                else:
                    self.status_label.config(text="Status: Ready")
            
            self.draw_puzzle()
    
    def reconstruct_states(self, initial_state, path):
        """Reconstruct all states from the initial state and path"""
        states = [initial_state]
        current = initial_state
        
        for move in path:
            if move == "Up":
                next_state = current.move_up()
            elif move == "Down":
                next_state = current.move_down()
            elif move == "Left":
                next_state = current.move_left()
            elif move == "Right":
                next_state = current.move_right()
            else:
                continue
                
            if next_state:
                states.append(next_state)
                current = next_state
                
        return states


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()