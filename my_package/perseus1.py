
class Perseus_game():

    # STANDARD GAME SETTINGS
    # num_rows = 10
    # num_cols = 18
    # win_num = 5

    def __init__(self,num_rows,num_cols,win_num):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.win_num = win_num
        self.turn = 1
        self.board = [[' ' for col in range(self.num_cols)] for row in range(self.num_rows)]

    def ini_board(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.board[row][col] = ' '
                


    def curr_turn_symbol(self, o=None, x=None):
        if x is None:
            x = 'X'
        if o is None:
            o = 'O' 
        if(self.turn % 4 == 1 or self.turn % 4 == 2): curr_turn = f'{o}'
        else: curr_turn = f'{x}'
        return curr_turn

    def taketurn(self, chosen_col = None):

        num_rows = self.num_rows
        num_cols = self.num_cols
        board = self.board

        done = 0
        i = num_rows - 1 
        curr_turn = str(self.curr_turn_symbol())
        
        while (done != 1):
            done = 0

            #offset to match 0,1,2,...,num_rows-1
            if chosen_col == None:
                print(f"------ It's {curr_turn}'s Turn ------")
                chosen_col = input(f"Choose Your Tile(1 - {num_cols}): ")

                #check for empty string or none-integer inputs
                if chosen_col == "" or not chosen_col.isdigit():
                    print("Invalid Input, Please Try Again.")
                    continue        

            #offset to match 0,1,2,...,num_cols-1
            chosen_col = int(chosen_col) - 1

            #Check if col is available
            if(not (0 <= chosen_col < num_cols)):
                print(f'That Column({chosen_col}) is not Allowed The Board')
                continue
            else: 
                #Check if row is available
                while(board[i][chosen_col] != ' '):
                    if (i > 0): 
                        i -= 1
                    else: 
                        print(f'Column {chosen_col + 1} is Occupied! (have {board[i][chosen_col]})')
                        break
                done += 1

        print(f'{curr_turn} has been placed at ({i},{chosen_col})')
        board[i][chosen_col] = curr_turn
        return i, chosen_col
        
    def board_line(self):
        num_cols = self.num_cols
        
        for i in range(num_cols):
            print('|---',end='')
        print('|')

    def print_board(self):

        num_rows = self.num_rows
        num_cols = self.num_cols
        board = self.board

        for row in range(num_rows):
            self.board_line()
            for col in range(num_cols):
                #print(row, col,end="")
                print(f"| {board[row][col]} ",end='')
            print('|')
        self.board_line()

    #return 'True' if all the space in the board is occupied aka., a draw 
    def draw_condition(self):
        num_rows = self.num_rows
        num_cols = self.num_cols
        board = self.board
        empty = 0

        for row in range(num_rows):
            for col in range(num_cols):
                if(board[row][col] == ' '):
                    empty += 1
                    break
        if empty == 0: 
            print('No Space Left, It\'s a Draw')
            self.print_board()
            return True
        else: return False

    def horz_win_condition(self):
        # |---|---|---|---|---|---|
        # | X | X | X | X | X |   |
        # |---|---|---|---|---|---|
        # |   | X | X | X | X | X |
        # |---|---|---|---|---|---|

        # Determine how many ways can 'win_num' (default 5) identical characters
        # can be place consecutives on the HORIZONTAL line
        # depending on the column size of the board
        num_rows = self.num_rows
        num_cols = self.num_cols
        board = self.board
        win_num = self.win_num
        curr_turn = self.curr_turn_symbol()

        horz_win_way = num_rows - (win_num - 1)
        count = 0

        for row in range(num_rows):
            for horz_win in range(horz_win_way):
                count = 0
                for col in range(num_cols):
                    if(board[row][col] == curr_turn): count += 1
                    else: count = 0
                    #print(f'count - {count}', curr_turn, board[row][col])
                    if (count >= win_num):
                        print(f'{curr_turn}\'s Player Has Won Horizontally!')
                        self.print_board()
                        return True
        return 0

    def vert_win_condition(self):
        
        # |---|---|
        # | X |   |
        # |---|---|
        # | X | X |
        # |---|---|
        # | X | X |
        # |---|---|
        # | X | X |
        # |---|---|
        # | X | X |
        # |---|---|
        # |   | X |
        # |---|---|

        # Determine how many ways can 'win_num' (default 5) identical characters
        # can be place consecutives on the VERTICAL line
        # depending on the column size of the board
        num_rows = self.num_rows
        num_cols = self.num_cols
        board = self.board
        win_num = self.win_num
        curr_turn = self.curr_turn_symbol()

        vert_win_way = num_rows - (win_num - 1)
        count = 0

        for col in range(num_cols):
            for vert_win in range(vert_win_way):
                count = 0
                for row in range(num_rows):
                    if(board[row][col] == curr_turn): 
                        count += 1
                    else: count = 0
                    if (count >= win_num):
                        print(f'{curr_turn}\'s Player Has Won Vertically!')
                        self.print_board()
                        return True
        return 0

    def diag_win_condition(self):
        #           
        #               Bottom-Left to Top-Right
        #  |---|---|---|---|---|  &&  |---|---|---|---|---| 
        #  | X | X | X | X | X |  &&  |   |   |   |   |   |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X | X | X | X |   |  &&  |   |   |   |   | X |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X | X | X |   |   |  &&  |   |   |   | X | X |  
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X | X |   |   |   |  &&  |   |   | X | X | X |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X |   |   |   |   |  &&  |   | X | X | X | X |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|

        #               Top-Left to Bottom-Right
        #     Left Reference             Top Reference
        #  |---|---|---|---|---|  &&  |---|---|---|---|---| 
        #  | X |   |   |   |   |  &&  |   | X | X | X | X |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X | X |   |   |   |  &&  |   |   | X | X | X |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X | X | X |   |   |  &&  |   |   |   | X | X |  
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X | X | X | X |   |  &&  |   |   |   |   | X |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        #  | X | X | X | X | X |  &&  |   |   |   |   |   |
        #  |---|---|---|---|---|  &&  |---|---|---|---|---|
        num_rows = self.num_rows
        num_cols = self.num_cols
        board = self.board
        win_num = self.win_num
        curr_turn = self.curr_turn_symbol()

        count = 0
        
    # Loop through all the diagonals starting from the top-left
        for row in range(num_rows):
            for col in range(num_cols):
                count = 0
                # Check the top-left to bottom-right diagonal
                i, j = row, col
                while i < num_rows and j < num_cols:
                    # If the current slot is filled by the current player, increment the count
                    if board[i][j] == curr_turn:
                        count += 1
                    else:
                        count = 0
                    if count == win_num:
                        print(f'{curr_turn}\'s Player Has Won Diagonally!')
                        self.print_board()
                        return True
                    i += 1
                    j += 1
                
                count = 0
                # Check the top-right to bottom-left diagonal
                i, j = row, col
                while i < num_rows and j >= 0:
                    # If the current slot is filled by the current player, increment the count
                    if board[i][j] == curr_turn:
                        count += 1
                    else:
                        count = 0
                    if count == win_num:
                        print(f'{curr_turn}\'s Player Has Won Diagonally!')
                        self.print_board()
                        return True
                    i += 1
                    j -= 1

    def check_win(self):
        if (self.horz_win_condition() or
        self.vert_win_condition() or
        self.diag_win_condition() ): return 1
        elif self.draw_condition(): return 2

        else: return 0

if __name__ == '__main__':
    game = Perseus_game(3,3,3)
    game.ini_board()
    while(True):
        print(f'Turn - {game.turn}')
        game.print_board()

        #buffer to make turn update all at once for all functions
        game.taketurn()

        print(f'win - {game.check_win()}')
        if(game.check_win()): break

        game.turn += 1


