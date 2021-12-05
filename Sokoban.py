from util import convert_text_to_board, print_board, get_new_pos, Action, CellState


class Sokoban:
    # board is a numpy 2D array, all other are list of tuples
    # This way it's easier to index board
    def __init__(self, input_path, mode = 0, board = None):
        if mode == 0:
            self.board, self.box_cells, self.goal_cells, self.player_pos = convert_text_to_board(input_path)
            self.n_row, self.n_col = self.board.shape[0], self.board.shape[1]
            self.valid_moves = self.get_current_valid_moves()
        
        elif mode == 1:
            self.set_board_to(board)
 

    # If move is not legal we can just skip the whole method
    def move(self, action, debug=True):
        if action not in self.valid_moves:
            return

        player_next_pos = get_new_pos(self.player_pos, action)

        # check if next cell is a box, if yes then push box. Could check with self.cell_at but we would have to
        # compare against BOX and BOX_ON_GOAL it's faster to write but less efficient
        if player_next_pos in self.box_cells:
            self.__push_box(player_next_pos, action)

        # move player to next pos
        if player_next_pos in self.goal_cells:
            self.set_cell_at(player_next_pos, CellState.PLAYER_ON_GOAL)
        else:
            self.set_cell_at(player_next_pos, CellState.PLAYER)

        # clear current cell after moving player
        if self.player_pos in self.goal_cells:
            self.set_cell_at(self.player_pos, CellState.GOAL)
        else:
            self.set_cell_at(self.player_pos, CellState.EMPTY)

        # update player pos
        self.player_pos = player_next_pos
        if debug:
            print_board(self.board)

        # update valid move
        self.valid_moves = self.get_current_valid_moves()

    # Assuming move is legal, push box only doesn't care who pushes it
    def __push_box(self, box_pos, action):
        box_next_pos = get_new_pos(box_pos, action)
        # Set state of box in next pos
        if self.cell_at(box_next_pos) == CellState.GOAL:
            self.set_cell_at(box_next_pos, CellState.BOX_ON_GOAL)
        else:
            self.set_cell_at(box_next_pos, CellState.BOX)

        # Set state in current pos
        if self.cell_at(box_pos) == CellState.BOX_ON_GOAL:
            self.set_cell_at(box_pos, CellState.GOAL)
        else:
            self.set_cell_at(box_pos, CellState.EMPTY)

        # set box_cells, also because
        self.box_cells.remove(box_pos)
        self.box_cells.append(box_next_pos)

    # Check if move is legal. Move is considered if it changes the board state somehow. Bumping into wall or pushing
    # one box into another doesn't change anything so by our definition move is not valid
    def is_valid_move(self, action):
        # The cell we are moving into can be either one of the three following:
        # 1) A wall: Not valid
        # 2) Not a box: Always valid since it's either empty, or a goal
        # 3) A box: Need to check the cell next to the box according to our action. If it's a wall then it's not valid,
        # otherwise everything else is valid
        next_pos = get_new_pos(self.player_pos, action)
        cell_next_pos = self.cell_at(next_pos)
        if cell_next_pos is CellState.WALL:
            return False
        elif cell_next_pos is not CellState.BOX and cell_next_pos is not CellState.BOX_ON_GOAL:
            return True
        else:  # next pos is box
            next_box_pos = get_new_pos(next_pos, action)
            if self.cell_at(next_box_pos) is CellState.WALL:
                return False
            return True

    # basically iterate all possible move and check if it's valid
    def get_current_valid_moves(self):
        valid_moves = []
        for action in Action:
            if self.is_valid_move(action):
                valid_moves.append(action)
        return valid_moves

    def is_completed(self):
        for box_pos in self.box_cells:
            if box_pos not in self.goal_cells:
                return False
        return True

    # getter
    def cell_at(self, pos):
        return self.board[pos[0], pos[1]]

    # set cell to CellState
    def set_cell_at(self, pos, state):
        self.board[pos[0], pos[1]] = state

    # Functions added by Huilai
    # Please let me know if I wrongly use any attribute
    
    # update goal cells
    def _update_goals(self):
        # update goal_cells based on self.board
        self.goal_cells = [(i,j) 
        for i in range(self.n_row) 
            for j in range(self.n_col) 
                if self.board[i,j] == CellState.GOAL or self.board[i,j] == CellState.BOX_ON_GOAL]
    
    # update box cells
    def _update_boxes(self):
        # update box_cells based on self.board
        self.box_cells = [(i,j) 
        for i in range(self.n_row)
            for j in range(self.n_col)
                if self.board[i,j] == CellState.BOX or self.board[i,j] == CellState.BOX_ON_GOAL] 
    
    # update player pos
    def _update_player_pos(self):
        for i in range(self.n_row):
            for j in range(self.n_col):
                if self.board[i,j] == CellState.PLAYER or self.board[i,j] == CellState.PLAYER_ON_GOAL:
                    self.player_pos = (i,j)

    # update goal_cells, box_cells, player_pos, valid_moves
    def _update_all(self):
        self.goal_cells = list()
        self.box_cells = list()
        
        for i in range(self.n_row):
            for j in range(self.n_col):
                if self.board[i,j] == CellState.GOAL or self.board[i,j] == CellState.BOX_ON_GOAL:
                    self.goal_cells.append((i,j))
                elif self.board[i,j] == CellState.BOX or self.board[i,j] == CellState.BOX_ON_GOAL:
                    self.box_cells.append((i,j))
                    if self.board[i,j] == CellState.BOX_ON_GOAL:
                        self.num_on_goal += 1
                elif self.board[i,j] == CellState.PLAYER or self.board[i,j] == CellState.PLAYER_ON_GOAL:
                    self.player_pos = (i,j)
        
        self.valid_moves = self.get_current_valid_moves()


    # set self.board to a given board
    def set_board_to(self, board):
        self.board = board
        self.num_on_goal = 0
        
        self.n_row, self.n_col = self.board.shape[0], self.board.shape[1]

        self._update_all()


