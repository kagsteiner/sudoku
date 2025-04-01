LLM used: ChatGPT o1.

Task: I want a sudoku solver.

Prompt:
Please create python code for a function that solves Sudoku puzzles. Input and output is a JSON file with 9 rows of 9 entries each, where each entry can be a number between 1 and 9 or an empty value (maybe 0, maybe something else, please decide what's best). Output is a JSON file of the same structure that contains a correctly solved sudoku where all numbers are the same, and all empty values are filled with numbers that solve the sudoku.

Result:
Code worked out of the box, with a simple but well written recursive backtracking algorithm. 



Task: now I want a sudoku generator. My idea was: if I have a fully solved Sudoku, I can randomly remove digits as long as there is still a unique solution. So I need a changed solver that computes all solutions.


Prompt:
Now please write a modified sudoku solver that checks if there is more than one solution to a sudoku. 

Result: 
Code again worked out of the box.



Task: write a sudoku generator that turns a fully solved sudoku into a random puzzle.

Prompt:
now, based on this solver, please create a python sudoku generator by this approach:

the generator is a function that takes two parameters: an incomplete sudoku and a number, the "effort". It performs these steps:

1. solve the sudoku to come to a new complete sudoku.
2. try the following forever, until you fail:
for effort times, pick a random number in the sudoku that is not 0. Remove the number from the puzzle and call the solver. If you still get a unique solution, remove the number from the puzzle.
The result is the last puzzle where the function couldn't remove a number in "effort" attempts.

Result:
Also worked out of the box. 



Task: I very much like how the effort gives me a nice difficulty level. effort 1 sudokus are trivial to solve, effort 10 are hard. But, obviously, all these sudoku solve to be the complete sudoku that I used as a starting point (by definition - taking away digits as long as there is only one solution). So the next task is to create a random start sudoku. Then I can solve this, and then I can unsolve it. For some reason I believe this is better as just using this start sudoku (doubtful, but I loved the sudoku I generated with the "come from full sudoku").

Prompt (intermediate):
can you add code to print the board as text?

Result: 
Worked.

LLM used: ChatGPT 4o - I wanted to try out how far I get without reasoning.

Prompt:
Great. Now I want to start with a random sudoku instead of always the same one. Please suggest python implementation of this algorithm:
1. start with an empty board
2. for the numbers 1 to 9, pick a random cell that is empty and put this number there.
3. remember the board as bestBoard
4. as long as you succeed, perform these steps:
4.1. try this for 10 times: pick a random cell and a random digit; fill the cell with the digit. Then check if the board is valid. If it is, try to solve the sudoku. If you succeed, store the board with the additional digit as the bestBoard. If you don't succeed after 10 times, the bestBoard is the random start sudoku.

Result: worked out of the box again. Don't underestimate o1, as long as you describe the way to go clearly instead of just the goal to achieve.


So by the end of this session I had the code to solve and generate Sudokus.

