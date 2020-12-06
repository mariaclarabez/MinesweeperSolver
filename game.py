from Buttons import *
from backtrack import *
from propagators import *
import minesweeper_csp
import random

'''Our executable file. The game board is a list of lists, where every item in the nested list is a Button object.
Once revealed, a cell can be a numerical value between 1 and 8, representing how many bombs are adjacent to a the
cell; a mine; or a blank square with no information. The Minesweeper class creates all of the game visualization and
adds the buttons to the GUI, and calls the methods to solve single or multiple iterations of the game. '''


class Minesweeper:

    def __init__(self, master):

        # create a frame where the game will reside
        self.frame = Frame(master)
        self.frame.pack()

        self.num_games = 0
        self.games_won = 0

        self.buttons = []
        self.mines = []
        self.board = []
        self.done = False

        # These values can be changed. The default game is set to 16x16 with 40 mines.
        self.row = 16
        self.col = 16
        self.num_mines = 55
        self.mines_left = self.num_mines
        self.flags = 0

        self.first_click = True
        self.first_click_btn = None

        # set up the smiley buttons, which will start/restart a game.
        self.smiley_default = PhotoImage(file="images/smiley.gif")
        self.smiley_won = PhotoImage(file="images/smiley_won.gif")
        self.smiley_lost = PhotoImage(file="images/smiley_lost.gif")

        # a dictionary of images, where the key is a string describing the image and the value is the image file.
        self.images = {'flag': PhotoImage(file="images/flag.gif"), 'mine': PhotoImage(file="images/mine.gif"),
                       'blank': PhotoImage(file="images/blank_cell.gif"),
                       'hit_mine': PhotoImage(file="images/mine_hit.gif"),
                       'wrong': PhotoImage(file="images/mine_incorrect.gif"), 'no': []}
        for i in range(0, 9):
            self.images['no'].append(PhotoImage(file="images/img_" + str(i) + ".gif"))

        # if the board is empty, import the game
        if not board:
            self.init_board()
        else:
            self.create_board(board)

        # Button object to restart the game
        self.restart_game_btn = Button(self.frame, image=self.smiley_default)
        # position the button in the grid
        self.restart_game_btn.grid(row=0, column=0, columnspan=self.col)
        # bind it to the grid
        self.restart_game_btn.bind("<Button-1>", lambda Button: self.init_game())

        # Display solve button
        self.solve_btn = Button(self.frame, text="Solve")
        self.solve_btn.grid(row=self.row + 2, column=0, columnspan=self.col, sticky=W)
        # Call solve method when the solve button is clicked.
        self.solve_btn.bind("<Button-1>", lambda Button: self.solve())

        self.iterations = 1000
        # Display "Run x iterations" button.
        self.solve_btn = Button(self.frame, text="Run " + str(self.iterations) + " iterations")
        self.solve_btn.grid(row=self.row + 3, column=0, columnspan=self.col, sticky=W)
        # Call solve_x_times method when the button is clicked, passing in a value of 50. This value can be changed.
        self.solve_btn.bind("<Button-1>", lambda Button: self.solve_x_times(self.iterations))

        # label to display how many mines are left.
        self.mines_left_label = Label(self.frame, text="Mines left: ")
        # widget will occupy 4 columns
        self.mines_left_label.grid(row=self.row + 1, column=0, columnspan=4, sticky=SW)
        self.mines_left_label_2 = Label(self.frame, text=self.num_mines)
        self.mines_left_label_2.grid(row=self.row + 1, column=4, columnspan=self.row, sticky=W)

    def init_board(self):
        """ Creates the default board and places the cells on it (which are Button objects).
        A board is a list of lists, where each element of the inner list is a cell button.
        """

        for row in range(self.row):
            # initialize outer list
            lst = []
            for col in range(self.col):
                # initialize button. Each button has a row, column, frame, and defined image
                button = Buttons(row, col, self.frame, self.images)
                # first row grid
                button.grid(row=row + 1, column=col)
                # append inner list of buttons
                lst.append(button)
                self.buttons.append(button)
            self.board.append(lst)

    def init_game(self):
        """ Resets all of the game's attributes so that a new game can start,
        including all of the buttons and labels displayed in the GUI. Increments
        the num_games attribute by 1 every time the method is called.
        """

        # increment the number of games at every turn. We use this variable when
        # we run the game several times and check the win rate.
        self.num_games += 1
        self.first_click = True
        self.first_click_btn = None
        self.done = False
        self.flags = 0
        # at the beginning of each game, the number of mines left is equal to the
        # number of mines at the start of the game
        self.mines_left = self.num_mines
        self.mines = []

        # The buttons should be reset at the start of every game.
        for each in self.buttons:
            each.reset()

        # reset mines left label
        # use config so mines_left can be modified during runtime
        self.mines_left_label_2.config(text=self.mines_left)
        # Reset the new game button, which is the smiley face.
        self.restart_game_btn.config(image=self.smiley_default)

    def place_mines(self):
        """ Places mines on the game board randomly.
        """
        mines = self.num_mines
        # while there are still mines left
        while mines:
            # get the surrounding cells, passing in the coordinates of the first cell that was clicked
            buttons = self.get_adj_cells(self.first_click_btn.x, self.first_click_btn.y)
            # append to the list of click buttons
            buttons.append(self.first_click_btn)

            # flag to check if random coordinates matches the initial click's 9 grids
            match = True
            row = None
            col = None
            while match:
                row = random.choice(range(self.row))
                col = random.choice(range(self.col))
                match = False
                for b in buttons:
                    if (row == b.x) and (col == b.y):
                        match = True
                        break

            # if a mine is being placed at a given cell
            if self.board[row][col].place_mine():
                # place it on the board
                self.mines.append(self.board[row][col])
                # update the surrounding buttons passing in the row, column, and value of 1
                self.update_adj_btns(row, col, 1)
                mines -= 1

    def get_adj_cells(self, row, col):
        """Return a list of surrounding buttons of button at row and col in board.

        :param row: int
        :param col: int
        :return: list of buttons
        """

        SURROUNDING = ((-1, -1), (-1, 0), (-1, 1),
                       (0, -1), (0, 1),
                       (1, -1), (1, 0), (1, 1))

        neighbours = []

        for pos in SURROUNDING:
            temp_row = row + pos[0]
            temp_col = col + pos[1]
            if 0 <= temp_row < self.row and 0 <= temp_col < self.col:
                neighbours.append(self.board[temp_row][temp_col])

        return neighbours

    def update_adj_btns(self, row, col, value):
        '''Update surrounding buttons' value adding given value.

        :param row: int
        :param col: int
        '''

        cells = self.get_adj_cells(row, col)
        for cell in cells:
            if not cell.is_mine():
                cell.value += value

    def lclicked(self, button):
        '''Left click action on given button.
        '''

        if self.first_click == True:
            # print("enter_first_click")
            self.first_click_btn = button
            self.place_mines()
            self.first_click = False

        # Do nothing if it's visible or it's flagged.
        if button.is_show() or button.is_flag():
            return

        # Case0: hits a number button, show the button.
        button.show()
        # Case1: hits a mine, game over.
        if button.is_mine():
            button.show_hit_mine()
            self.restart_game_btn.config(image=self.smiley_lost)
            self.gameover()
        # Case2: hits an empty button, keep showing surrounding buttons until all not empty.
        elif button.value == 0:
            buttons = [button]
            while buttons:
                temp_button = buttons.pop()
                surrounding = self.get_adj_cells(temp_button.x, temp_button.y)
                for neighbour in surrounding:
                    if not neighbour.is_show() and neighbour.value == 0:
                        buttons.append(neighbour)
                    neighbour.show()

        # Check whether the game wins or not.
        if self.is_win():
            self.gameover()

    def rclicked(self, button):
        '''Right click action on given button.
        '''

        # Do nothing if it's visible.
        if button.is_show():
            return

        # Flag/Unflag a button.
        if button.is_flag():
            button.flag()
            self.flags -= 1
        else:
            button.flag()
            self.flags += 1

        # Update remaining mines label.
        self.mines_left = (self.num_mines - self.flags) if self.flags < self.num_mines else 0
        self.mines_left_label_2.config(text=self.mines_left)

        if self.is_win():
            self.gameover()

    def gameover(self):
        '''Disable all buttons and show all mines.
        '''
        # if self.is_win():
        #     self.win_times += 1
        self.done = True
        for button in self.buttons:
            if button.is_mine():
                if not button.is_flag() and not self.is_win():
                    button.show()
            elif button.is_flag():
                button.show_wrong_flag()
            button.unbind('<Button-1>')
            button.unbind('<Button-3>')

    def is_win(self):
        '''Return True if game wins; False otherwise. The game wins if all buttons are either visible or flagged, and
        the amount of flags equals the amount of mines.

        :return: bool
        '''

        # if self.flags == self.mines_amount:
        # for mine in self.mines:
        # if not mine.is_flag():
        # return False
        for button in self.buttons:
            if not button.is_show() and not button.is_mine():
                return False
        self.restart_game_btn.config(image=self.smiley_won)
        return True
        # else:
        # return False

    def solve(self):
        '''Solve current game completely.
        '''
        if self.done:
            return
        # Unflag all buttons.
        for button in self.buttons:
            if button.is_flag():
                button.flag()
                self.flags -= 1

        while not self.done:
            assigned = self.solve_step()
            # No variable assigned by CSP.
            if not assigned:
                choose_button = self.guess_move()
                self.lclicked(choose_button)

    def solve_x_times(self, times):
        self.games_won = 0
        self.num_games = 0
        print("board size: {0}x{1}\nmines #: {2}\n{3}".format(self.row, self.col, self.num_mines, "-" * 27))
        for i in range(times):
            self.solve()
            if self.is_win():
                self.games_won += 1
            self.init_game()
            if (i + 1) % 100 == 0:
                print("solved: " + str(i + 1) + " times")

        print("-------Run results---------")
        print("Matches played: " + str(self.num_games))
        print("Wins: " + str(self.games_won))
        print("Win rate: " + str(self.games_won / self.num_games))
        self.games_won = 0
        self.num_games = 0

    def guess_move(self):
        '''Return an unclick button.

        :return: button
        '''

        buttons = []
        corners = [self.board[0][0], self.board[0][self.col - 1], self.board[self.row - 1][0],
                   self.board[self.row - 1][self.col - 1]]
        for button in self.buttons:
            if not button.is_show() and not button.is_flag():
                buttons.append(button)

        for button in corners:
            if not button.is_show() and not button.is_flag():
                return button

        return random.choice(buttons)

    def solve_step(self):
        """Solve parts of the game bases on current board's information by using CSP.
        Return the number of variables made.

        :return: Return int
        """

        is_assigned = False

        csp = minesweeper_csp.csp_model(self)

        solver = BT(csp)
        solver.bt_search_MS(prop_GAC)
        for var in csp.get_all_vars():

            try:
                cell = var.name.split()
                row = int(cell[0])
                col = int(cell[1])
            except:
                # continue if it's not a vriable in board.
                # in board variable name's format: row, col
                continue

            if var.get_assigned_value() == 1:
                if not self.board[row][col].is_flag():
                    self.rclicked(self.board[row][col])
                    is_assigned = True
            elif var.get_assigned_value() == 0:
                if not self.board[row][col].is_show():
                    self.lclicked(self.board[row][col])
                    is_assigned = True

        return is_assigned

    def create_board(self, board):
        '''Import game from a list of lists with numbers.
        '''

        self.row = len(board)
        self.col = len(board[0])

        self.num_mines = 0

        self.flags = 0
        self.buttons = []
        self.mines = []
        self.board = []

        for row in range(self.row):
            lis = []
            for col in range(self.col):
                button = Buttons(row, col, self.frame, self.images, board[row][col])
                if button.is_mine():
                    self.mines.append(button)
                    self.num_mines += 1
                # first row grid for new game button
                button.grid(row=row + 1, column=col)
                lis.append(button)
                self.buttons.append(button)
            self.board.append(lis)

        self.mines_left = self.num_mines


def main():
    global root
    root = Tk()
    root.title("Minesweeper")
    minesweeper = Minesweeper(root)
    root.mainloop()


boards = [[[2, -1, -1],
           [-1, 4, 2],
           [-1, 2, 0],
           [2, 2, 0],
           [-1, 1, 0],
           [1, 1, 0]],
          [[0, 0, -1, 0, -1],
           [-1, 2, 1, 3, 0],
           [0, 2, 1, 2, 0 - 1],
           [-1, 0, 1, -1, 0],
           [0, 1, 1, 1, 1]]
          ]

board = []

if __name__ == "__main__":
    main()
