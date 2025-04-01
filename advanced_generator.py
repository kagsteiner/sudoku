import json
import copy
import random

def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False

    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3

    for r in range(box_row_start, box_row_start + 3):
        for c in range(box_col_start, box_col_start + 3):
            if board[r][c] == num:
                return False

    return True

def find_all_solutions(board, max_solutions=2):
    solutions = []

    def backtrack(b):
        if len(solutions) >= max_solutions:
            return
        for row in range(9):
            for col in range(9):
                if b[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(b, row, col, num):
                            b[row][col] = num
                            backtrack(b)
                            b[row][col] = 0
                    return
        solutions.append(copy.deepcopy(b))

    backtrack(copy.deepcopy(board))
    return solutions

def solve_and_check_unique(board):
    return len(find_all_solutions(board, max_solutions=2)) == 1

def solve_first(board):
    solutions = find_all_solutions(board, max_solutions=1)
    return solutions[0] if solutions else None

def generate_sudoku(puzzle, effort=5):
    """
    Takes an incomplete puzzle (0 = empty), and an 'effort' level.
    Returns a new puzzle with numbers removed, while preserving a unique solution.
    """
    # Step 1: Solve it fully to get a complete puzzle
    full_solution = solve_first(puzzle)
    if not full_solution:
        raise ValueError("Input puzzle is not solvable")

    working_puzzle = copy.deepcopy(full_solution)

    while True:
        modified = False
        for _ in range(effort):
            # Get coordinates of non-zero cells
            filled_cells = [(r, c) for r in range(9) for c in range(9) if working_puzzle[r][c] != 0]
            if not filled_cells:
                break  # All cells are empty?

            r, c = random.choice(filled_cells)
            removed_val = working_puzzle[r][c]
            working_puzzle[r][c] = 0

            if solve_and_check_unique(working_puzzle):
                modified = True  # Successful removal
            else:
                working_puzzle[r][c] = removed_val  # Restore it

        if not modified:
            break  # Couldn’t remove anything in this round → done

    return working_puzzle


def print_board(board):
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
    board = [[0 for _ in range(9)] for _ in range(9)]

    # Step 1–2: Place digits 1–9 randomly
    all_cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(all_cells)
    placed_digits = set()
    i = 0
    while len(placed_digits) < 9 and i < len(all_cells):
        r, c = all_cells[i]
        digit = len(placed_digits) + 1
        board[r][c] = digit
        placed_digits.add(digit)
        i += 1

    best_board = copy.deepcopy(board)

    # Step 4: Try to randomly fill more cells
    attempts = 0
    while True:
        success = False
        for _ in range(5):
            r, c = random.randint(0, 8), random.randint(0, 8)
            if board[r][c] != 0:
                continue
            digit = random.randint(1, 9)
            if is_valid(board, r, c, digit):
                board[r][c] = digit
                if solve_first(board):
                    best_board = copy.deepcopy(board)
                    success = True
                    break
                board[r][c] = 0  # Backtrack
        if not success:
            break

    return best_board




if __name__ == "__main__":
    # Generate a random starting Sudoku board
    input_puzzle = generate_random_start_board()

    # Generate a puzzle with effort=10
    puzzle = generate_sudoku(input_puzzle, effort=10)

    # Save result
    with open("generated_sudoku.json", "w") as f:
        json.dump(puzzle, f)

    print("✅ Puzzle generated and saved to generated_sudoku.json")
    print_board(puzzle)