import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox
import copy
import random
import json # Keep this if you still want the save functionality in __main__

# --- Paste your Sudoku logic functions here ---
# (is_valid, find_all_solutions, solve_and_check_unique,
#  solve_first, generate_sudoku, print_board, generate_random_start_board)

# <PASTE SUDOKU LOGIC HERE>
def is_valid(board, row, col, num):
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in [board[r][col] for r in range(9)]:
        return False
    # Check 3x3 box
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3
    for r in range(box_row_start, box_row_start + 3):
        for c in range(box_col_start, box_col_start + 3):
            if board[r][c] == num:
                return False
    return True

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None

def find_all_solutions(board, max_solutions=2):
    solutions = []
    
    # Use a slightly different backtrack approach that might be less prone to deep recursion issues
    # and explicitly finds empty cells
    def backtrack_find(b):
        nonlocal solutions
        if len(solutions) >= max_solutions:
            return True # Found enough solutions

        find = find_empty(b)
        if not find:
            solutions.append(copy.deepcopy(b))
            return len(solutions) >= max_solutions

        row, col = find
        for num in range(1, 10):
            if is_valid(b, row, col, num):
                b[row][col] = num
                if backtrack_find(b):
                    return True # Propagate stop signal
                b[row][col] = 0 # Backtrack

        return False # Did not find enough solutions from this path

    # Create a copy to work on
    board_copy = copy.deepcopy(board)
    backtrack_find(board_copy)
    return solutions


def solve_and_check_unique(board):
    solutions = find_all_solutions(board, max_solutions=2)
    return len(solutions) == 1

def solve_first(board):
    solutions = find_all_solutions(board, max_solutions=1)
    return solutions[0] if solutions else None

def generate_sudoku(puzzle, effort=5):
    """
    Takes an incomplete puzzle (0 = empty), and an 'effort' level.
    Returns a new puzzle with numbers removed, while preserving a unique solution.
    Effort roughly corresponds to how many removal attempts are made per round.
    Higher effort leads to potentially harder puzzles (more removed cells).
    """
    # Step 1: Ensure the input puzzle is solvable and get a full solution
    full_solution = solve_first(puzzle)
    if not full_solution:
        # If the initial random board isn't solvable, try generating again
        # This can happen, although less likely with the improved generator
        print("Warning: Initial random board not solvable, regenerating...")
        return generate_sudoku(generate_random_start_board(), effort)
        # raise ValueError("Input puzzle is not solvable") # Or handle differently

    working_puzzle = copy.deepcopy(full_solution)
    
    # Get all cell coordinates and shuffle them for random removal attempts
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    
    cells_removed = 0
    max_removals = 81 - 17 # Minimum number of clues for a unique solution is generally 17
    
    # Try removing cells one by one
    for r, c in cells:
        if working_puzzle[r][c] == 0: # Skip already empty cells
            continue

        removed_val = working_puzzle[r][c]
        working_puzzle[r][c] = 0
        
        # Check if the puzzle still has a unique solution
        if solve_and_check_unique(working_puzzle):
             # Keep the cell removed
             cells_removed += 1
             if cells_removed >= max_removals : # Optional: Stop if too many cells removed
                 break 
        else:
            # Restore the number if uniqueness is lost
            working_puzzle[r][c] = removed_val

    # The 'effort' parameter from the original code isn't directly used here.
    # Instead, we use the number of successfully removed cells while maintaining uniqueness.
    # The difficulty slider can map to this process indirectly if needed,
    # perhaps by controlling the 'max_removals' or by applying post-processing.
    # For now, the difficulty slider in the UI influences the *generation* effort.
    # Let's adjust generate_sudoku slightly to use difficulty:
    # Higher difficulty = try remove more cells (more potential iterations)

    # Re-implementing with 'effort' idea more directly:
    # Effort here will control the number of *passes* over random cells.
    working_puzzle = copy.deepcopy(full_solution)
    
    # Adjust attempts based on difficulty (1-10)
    # Scale the number of removal attempts based on difficulty.
    # A simple scaling: total cells * difficulty / 10 * some factor
    # Let's try roughly 'effort * 10' attempts.
    
    removal_attempts = effort * 15 # More attempts for higher difficulty
    
    
    filled_cells = [(r, c) for r in range(9) for c in range(9) if working_puzzle[r][c] != 0]
    random.shuffle(filled_cells)
    
    removed_count = 0
    
    # Try removing cells based on the shuffled list and effort
    for r_idx in range(len(filled_cells)):
        r, c = filled_cells[r_idx]
        
        # Limit removal attempts based on 'effort' scaling
        if r_idx >= removal_attempts and effort < 10: # Allow max effort to try all
             break 
        
        if working_puzzle[r][c] == 0: continue # Should not happen with this list, but safe check

        removed_val = working_puzzle[r][c]
        working_puzzle[r][c] = 0
        
        temp_solution_check = find_all_solutions(working_puzzle, max_solutions=2)

        if len(temp_solution_check) == 1:
             # Removal was successful, keep it removed
             removed_count += 1
        else:
             # Removal resulted in non-unique or no solution, put it back
             working_puzzle[r][c] = removed_val

    print(f"Removed {removed_count} cells for difficulty {effort}.")
    return working_puzzle


def print_board(board):
    # (Keep this for debugging if needed, but GUI will replace it)
    for i, row in enumerate(board):
        row_str = ""
        for j, num in enumerate(row):
            char = "." if num == 0 else str(num)
            row_str += char + " "
            if (j + 1) % 3 == 0 and j < 8:
                row_str += "| "
        print(row_str)
        if (i + 1) % 3 == 0 and i < 8:
            print("-" * 21)


def generate_random_start_board():
    # Generate a fully solved board first, then remove numbers.
    # This is a more reliable way to get a valid starting point.
    board = [[0 for _ in range(9)] for _ in range(9)]

    # Fill the diagonal boxes first (guaranteed valid locally)
    for i in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for r in range(3):
            for c in range(3):
                board[i+r][i+c] = nums.pop()

    # Solve the rest of the board
    full_board = solve_first(board)
    if not full_board:
        # Should be rare with the diagonal pre-fill, but handle recursion
        print("Failed to create initial solved board, retrying...")
        return generate_random_start_board()

    # Now we have a fully solved board. We don't need to return this directly.
    # We can immediately start removing elements based on some criteria,
    # or just return this solvable state to `generate_sudoku`.
    # The original `generate_random_start_board` seemed to aim for an *incomplete*
    # but solvable board. Let's return the *solved* board, as `generate_sudoku`
    # expects a complete board (or at least a solvable one) to start removing from.
    # Edit: Let's return an *incomplete* but solvable board by removing some elements
    # from the solved one randomly, ensuring it's still solvable.
    
    attempts = 40 # Try removing a fixed number of cells initially
    temp_puzzle = copy.deepcopy(full_board)
    removed_count = 0
    cells = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    for r, c in cells:
        if removed_count >= attempts: break
        
        val = temp_puzzle[r][c]
        temp_puzzle[r][c] = 0
        
        # Quick check if it's still solvable (doesn't need unique check here)
        if solve_first(temp_puzzle):
            removed_count += 1
        else:
            temp_puzzle[r][c] = val # Put back if it broke solvability

    # Return this partially filled, solvable board
    # `generate_sudoku` will then remove more based on difficulty and uniqueness.
    return temp_puzzle

# </PASTE SUDOKU LOGIC HERE>


# --- Tkinter GUI Application ---

class SudokuGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sudoku Solver")
        master.geometry("600x750") # Adjusted size for controls

        # --- Constants ---
        self.cell_size = 60
        self.grid_size = self.cell_size * 9
        self.note_font_size = 10
        self.value_font_size = 28
        self.color_bg = "#FFFFFF"
        self.color_grid = "#808080"
        self.color_block_grid = "#000000"
        self.color_fixed_text = "#333333" # Dark grey for initial numbers
        self.color_user_text = "#0000FF"  # Blue for user values
        self.color_note_text = "#666666"  # Lighter grey for notes
        self.color_active_cell = "#FFFF99" # Light yellow for active cell
        self.color_highlight = "#FFDDDD" # Light red for highlighting errors
        self.color_valid = "#DDFFDD"     # Light green for success

        # --- Fonts ---
        self.value_font = tkFont.Font(size=self.value_font_size, weight="bold")
        self.note_font = tkFont.Font(size=self.note_font_size)

        # --- Data Structures ---
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)] # The generated puzzle
        self.user_values = [[0 for _ in range(9)] for _ in range(9)]   # User's main entries
        self.user_notes = [[set() for _ in range(9)] for _ in range(9)] # User's pencil marks

        self.active_cell = None  # Tuple (row, col) or None
        self.highlighted_cells = set() # Set of (row, col) tuples for error highlighting

        # --- UI Elements ---

        # Frame for the grid
        self.grid_frame = tk.Frame(master)
        self.grid_frame.pack(pady=20)

        self.canvas = tk.Canvas(self.grid_frame,
                                width=self.grid_size,
                                height=self.grid_size,
                                bg=self.color_bg)
        self.canvas.pack()

        # Frame for controls below the grid
        self.control_frame = tk.Frame(master)
        self.control_frame.pack(pady=10, fill=tk.X, padx=20)

        # Difficulty Slider
        difficulty_frame = tk.Frame(self.control_frame)
        difficulty_frame.pack(pady=5)
        tk.Label(difficulty_frame, text="Difficulty (1-10):").pack(side=tk.LEFT, padx=5)
        self.difficulty_var = tk.IntVar(value=5) # Default difficulty
        self.difficulty_slider = tk.Scale(difficulty_frame, from_=1, to=10,
                                          orient=tk.HORIZONTAL, variable=self.difficulty_var,
                                          length=150)
        self.difficulty_slider.pack(side=tk.LEFT)

        # Input Mode Toggle (Radio Buttons)
        mode_frame = tk.Frame(self.control_frame)
        mode_frame.pack(pady=5)
        tk.Label(mode_frame, text="Input Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value="value") # Default to entering final values
        self.value_radio = tk.Radiobutton(mode_frame, text="Final Value", variable=self.mode_var, value="value")
        self.notes_radio = tk.Radiobutton(mode_frame, text="Pencil Notes", variable=self.mode_var, value="notes")
        self.value_radio.pack(side=tk.LEFT)
        self.notes_radio.pack(side=tk.LEFT, padx=10)

        # Action Buttons Frame
        button_frame = tk.Frame(self.control_frame)
        button_frame.pack(pady=10)

        self.new_puzzle_button = tk.Button(button_frame, text="New Puzzle", command=self.generate_new_puzzle, width=12)
        self.new_puzzle_button.pack(side=tk.LEFT, padx=5)

        self.check_button = tk.Button(button_frame, text="Check Validity", command=self.check_current_validity, width=12)
        self.check_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = tk.Button(button_frame, text="Restart Puzzle", command=self.restart_current_puzzle, width=12)
        self.restart_button.pack(side=tk.LEFT, padx=5)

        # Status Label
        self.status_var = tk.StringVar(value="Generate a new puzzle to start!")
        self.status_label = tk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, bd=1, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=2)

        # --- Bindings ---
        self.canvas.bind("<Button-1>", self._canvas_click)
        master.bind("<KeyPress>", self._key_press) # Bind to main window for global key capture

        # --- Initial Setup ---
        self._draw_grid_lines()
        self.generate_new_puzzle() # Start with a puzzle


    def _draw_grid_lines(self):
        """Draws the Sudoku grid lines on the canvas."""
        for i in range(10):
            # Determine line thickness
            thickness = 3 if i % 3 == 0 else 1
            color = self.color_block_grid if i % 3 == 0 else self.color_grid

            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_size, fill=color, width=thickness)

            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_size, y, fill=color, width=thickness)

    def _draw_all_cells(self):
        """Redraws the contents of all cells based on current state."""
        self.canvas.delete("numbers") # Clear previous numbers
        self.canvas.delete("notes")   # Clear previous notes
        self.canvas.delete("highlight") # Clear previous highlights
        self.canvas.delete("active_highlight") # Clear active highlight

        for r in range(9):
            for c in range(9):
                x0 = c * self.cell_size
                y0 = r * self.cell_size
                x_center = x0 + self.cell_size / 2
                y_center = y0 + self.cell_size / 2

                # Draw background highlight if needed
                if (r, c) in self.highlighted_cells:
                    self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size,
                                                 fill=self.color_highlight, outline="", tags="highlight")
                elif self.active_cell == (r, c):
                     self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size,
                                                 fill=self.color_active_cell, outline="", tags="active_highlight")


                # Draw initial puzzle numbers (fixed)
                if self.initial_board[r][c] != 0:
                    self.canvas.create_text(x_center, y_center,
                                            text=str(self.initial_board[r][c]),
                                            font=self.value_font,
                                            fill=self.color_fixed_text,
                                            tags="numbers")
                # Draw user-entered values
                elif self.user_values[r][c] != 0:
                    self.canvas.create_text(x_center, y_center,
                                            text=str(self.user_values[r][c]),
                                            font=self.value_font,
                                            fill=self.color_user_text,
                                            tags="numbers")
                # Draw user notes (if no value is entered)
                elif self.user_notes[r][c]:
                    notes = sorted(list(self.user_notes[r][c]))
                    note_str = "".join(map(str, notes))

                    # Simple grid layout for notes within the cell
                    rows_cols = 3 # Arrange notes in a 3x3 grid within the cell
                    for i, note_num in enumerate(notes):
                        note_r = i // rows_cols
                        note_c = i % rows_cols
                        # Calculate position within the cell (adjust offsets as needed)
                        note_x = x0 + (note_c + 0.5) * (self.cell_size / rows_cols)
                        note_y = y0 + (note_r + 0.5) * (self.cell_size / rows_cols)

                        self.canvas.create_text(note_x, note_y,
                                                text=str(note_num),
                                                font=self.note_font,
                                                fill=self.color_note_text,
                                                tags="notes")

    def _canvas_click(self, event):
        """Handles clicking on the canvas to select a cell."""
        x, y = event.x, event.y
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            col = x // self.cell_size
            row = y // self.cell_size

            # Only allow selecting cells that are not part of the initial puzzle
            if self.initial_board[row][col] == 0:
                self.active_cell = (row, col)
                self.status_var.set(f"Selected cell ({row+1}, {col+1}). Enter number or notes.")
            else:
                self.active_cell = None # Cannot select fixed cells
                self.status_var.set("Cannot modify initial puzzle numbers.")

            self._clear_highlights() # Clear validity highlights on click
            self._draw_all_cells() # Redraw to show active cell highlight

    def _key_press(self, event):
        """Handles number key presses and mode switching."""
        key = event.keysym
        # print(f"Key pressed: {key}") # Optional: for debugging

        # --- Handle Mode Toggle Key (e.g., 'm') ---
        # We check this *before* checking for active_cell, so mode can be switched anytime
        if key.lower() == 'm': # Use 'm' or 'M' to toggle mode
            current_mode = self.mode_var.get()
            if current_mode == "value":
                new_mode = "notes"
                self.mode_var.set(new_mode)
                mode_text = "Pencil Notes"
            else: # current_mode == "notes"
                new_mode = "value"
                self.mode_var.set(new_mode)
                mode_text = "Final Value"
            self.status_var.set(f"Input mode switched to: {mode_text}")
            # Optional: Give a visual cue, like briefly changing active cell color if one exists
            # if self.active_cell: self._flash_active_cell() # You'd need to implement _flash_active_cell
            return # Prevent 'm' from being processed further (e.g., as input)

        # --- Subsequent actions require an active cell ---
        if self.active_cell is None:
            # If no cell is active, only the mode switch ('m') should work.
            # Any other key press does nothing if no cell is selected.
            return

        r, c = self.active_cell

        # --- Handle Number Input (1-9) ---
        if key.isdigit() and '1' <= key <= '9':
            num = int(key)
            mode = self.mode_var.get()

            if mode == "value":
                # Enter the final value
                if self.user_values[r][c] != num: # Only redraw if changed
                    self.user_values[r][c] = num
                    self.user_notes[r][c] = set() # Clear notes when value is set
                    self.status_var.set(f"Entered value {num} in cell ({r+1}, {c+1})")
                    self._clear_highlights() # Clear previous validity highlights
                    self._draw_all_cells() # Redraw needed
                else:
                     self.status_var.set(f"Cell ({r+1}, {c+1}) already has value {num}")


            elif mode == "notes":
                # Add or remove the number from notes
                if self.user_values[r][c] == 0: # Can only add notes if no final value
                    notes_changed = False
                    if num in self.user_notes[r][c]:
                        self.user_notes[r][c].remove(num)
                        self.status_var.set(f"Removed note {num} from cell ({r+1}, {c+1})")
                        notes_changed = True
                    else:
                        self.user_notes[r][c].add(num)
                        self.status_var.set(f"Added note {num} to cell ({r+1}, {c+1})")
                        notes_changed = True

                    if notes_changed:
                        self._clear_highlights()
                        self._draw_all_cells() # Redraw needed
                else:
                    self.status_var.set(f"Cannot add notes, cell ({r+1}, {c+1}) has value {self.user_values[r][c]}")


        # --- Handle Deletion (Backspace/Delete) ---
        elif key in ("BackSpace", "Delete"):
            cleared_something = False
            # Clear value primarily. If no value, clear notes.
            if self.user_values[r][c] != 0:
                self.user_values[r][c] = 0
                self.status_var.set(f"Cleared value from cell ({r+1}, {c+1})")
                cleared_something = True
            elif self.user_notes[r][c]:
                 self.user_notes[r][c] = set() # Clear all notes if no value
                 self.status_var.set(f"Cleared notes from cell ({r+1}, {c+1})")
                 cleared_something = True

            if cleared_something:
                self._clear_highlights()
                self._draw_all_cells() # Redraw needed

        # --- Handle Arrow Keys for Navigation ---
        elif key in ("Up", "Down", "Left", "Right"):
            nr, nc = r, c
            if key == "Up":    nr = max(0, r - 1)
            elif key == "Down":  nr = min(8, r + 1)
            elif key == "Left":  nc = max(0, c - 1)
            elif key == "Right": nc = min(8, c + 1)

            original_nr, original_nc = nr, nc # Store initial target

            # Skip over fixed cells during navigation
            # Keep track of visited cells during skip to prevent infinite loops in fully fixed rows/cols
            visited_while_skipping = set([(r,c)])
            while self.initial_board[nr][nc] != 0 and (nr, nc) not in visited_while_skipping:
                 visited_while_skipping.add((nr, nc))
                 if key == "Up":    nr = max(0, nr - 1)
                 elif key == "Down":  nr = min(8, nr + 1)
                 elif key == "Left":  nc = max(0, nc - 1)
                 elif key == "Right": nc = min(8, nc + 1)
                 # Break if we wrapped around or hit the original again
                 if (nr, nc) in visited_while_skipping:
                     nr, nc = r, c # Stay in the original cell if no valid move found
                     break

            # Only move if the target cell is different and empty
            if (nr, nc) != (r, c) and self.initial_board[nr][nc] == 0:
                self.active_cell = (nr, nc)
                self.status_var.set(f"Moved to cell ({nr+1}, {nc+1})")
                self._clear_highlights()
                self._draw_all_cells() # Redraw needed for active cell highlight change
            elif (nr, nc) == (r,c):
                 self.status_var.set(f"Cannot move {key} from cell ({r+1}, {c+1}). Blocked or edge.")


    def _clear_highlights(self):
        """Removes any validity highlighting."""
        self.highlighted_cells.clear()
        self.canvas.configure(bg=self.color_bg) # Reset canvas bg just in case
        self.status_label.configure(bg='SystemButtonFace', fg='black') # Reset status bar colors

    def _get_current_board_state(self):
        """Combines initial board and user values into one board."""
        current_board = copy.deepcopy(self.initial_board)
        for r in range(9):
            for c in range(9):
                if self.user_values[r][c] != 0:
                    # Ensure user value doesn't conflict with initial board (shouldn't happen with UI logic)
                    if current_board[r][c] == 0:
                        current_board[r][c] = self.user_values[r][c]
                    elif current_board[r][c] != self.user_values[r][c]:
                         # This indicates a logic error or data corruption
                         print(f"ERROR: Conflict at ({r},{c}). Initial={current_board[r][c]}, User={self.user_values[r][c]}")
                         # Handle error appropriately, maybe highlight the conflict
                         self.highlighted_cells.add((r,c))


        return current_board

    # --- Button Actions ---

    def generate_new_puzzle(self):
        """Generates a new Sudoku puzzle based on selected difficulty."""
        self._clear_highlights()
        self.active_cell = None
        difficulty = self.difficulty_var.get()
        self.status_var.set(f"Generating new puzzle (difficulty {difficulty})...")
        self.master.update_idletasks() # Update UI to show status message

        try:
            # Generate a solvable base board
            start_board = generate_random_start_board()
            # Remove numbers based on difficulty, ensuring unique solution
            self.initial_board = generate_sudoku(start_board, difficulty)

            # Reset user inputs
            self.user_values = [[0 for _ in range(9)] for _ in range(9)]
            self.user_notes = [[set() for _ in range(9)] for _ in range(9)]

            self.status_var.set(f"New puzzle (difficulty {difficulty}) generated. Good luck!")
            self._draw_all_cells()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate puzzle:\n{e}")
            self.status_var.set("Error generating puzzle. Try again.")
            # Optionally reset to a blank or previous state
            self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
            self.user_values = [[0 for _ in range(9)] for _ in range(9)]
            self.user_notes = [[set() for _ in range(9)] for _ in range(9)]
            self._draw_all_cells()

    def check_current_validity(self):
        """Checks if the current user entries violate Sudoku rules."""
        self._clear_highlights()
        current_board = self._get_current_board_state()
        is_overall_valid = True
        violation_found = False

        for r in range(9):
            for c in range(9):
                num = current_board[r][c]
                if num != 0:
                    # Temporarily set cell to 0 to check validity against others
                    current_board[r][c] = 0
                    if not is_valid(current_board, r, c, num):
                        self.highlighted_cells.add((r, c))
                        is_overall_valid = False
                        violation_found = True
                    # Restore the number
                    current_board[r][c] = num

        self._draw_all_cells() # Redraw to show highlights

        if violation_found:
            self.status_var.set("Invalid entries found (marked in red).")
            self.status_label.configure(bg=self.color_highlight, fg='black')
        else:
             # Check if board is full
             is_full = all(current_board[r][c] != 0 for r in range(9) for c in range(9))
             if is_full:
                 self.status_var.set("Board is full and valid according to rules!")
                 self.status_label.configure(bg=self.color_valid, fg='black')
                 # Optional: Add a check against the actual solution here if you store it
             else:
                 self.status_var.set("Current entries are valid according to Sudoku rules.")
                 self.status_label.configure(bg=self.color_valid, fg='black')


    def restart_current_puzzle(self):
        """Clears user inputs and resets to the initial state of the current puzzle."""
        if not any(any(row) for row in self.initial_board): # No puzzle loaded
             self.status_var.set("Generate a puzzle first.")
             return

        confirm = messagebox.askyesno("Restart Puzzle", "Are you sure you want to clear your progress on this puzzle?")
        if confirm:
            self._clear_highlights()
            self.active_cell = None
            self.user_values = [[0 for _ in range(9)] for _ in range(9)]
            self.user_notes = [[set() for _ in range(9)] for _ in range(9)]
            self.status_var.set("Puzzle restarted. Showing initial board.")
            self._draw_all_cells()


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    gui = SudokuGUI(root)
    root.mainloop()

    # Example of using the original save functionality (optional)
    # if hasattr(gui, 'initial_board') and any(any(row) for row in gui.initial_board):
    #     try:
    #         with open("last_generated_sudoku.json", "w") as f:
    #             json.dump(gui.initial_board, f)
    #         print("✅ Last generated puzzle saved to last_generated_sudoku.json")
    #     except Exception as e:
    #         print(f"Error saving puzzle: {e}")