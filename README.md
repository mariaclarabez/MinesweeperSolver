Our game.py file is our executable file containing a Minesweeper class that sets up the game. In the class constructor, 
we initialize the game board to be 16 x 16 with 40 mines.These values can be changed to produce different-sized boards. 
We set up buttons the user can click to solve the game. When the user clicks the button “solve,” 1 iteration of the game
 is played and the results are displayed. When the user clicks the “run x iterations”, the terminal displays the run 
 results in terms of matches played, wins, and the win rate. The number of iterations can be changed by changing the 
 value of the self.iterations attribute, which will also update the label with the correct number of iterations that 
 will be performed.

Dependencies: Python3 (make sure you have Tkinter)
