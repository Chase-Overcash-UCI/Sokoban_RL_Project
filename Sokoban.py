import numpy as np
from util import convert_text_to_board, print_board, get_new_pos, Action, CellState, get_pos_dif, pos_dif_to_action
from typing import List, Collection


class Sokoban:
    # board is a numpy 2D array, all other are list of tuples
    # This way it's easier to index board

    def __init__(self,  input_path=None, board=None, debug=True):
        assert (board is not None) ^ (input_path is not None), "Either board or input path must present"

        if input_path:
            self.board, self.box_cells, self.goal_cells, self.player_pos = convert_text_to_board(input_path)
        elif board:
            self.__set_board_to(board)

        assert self.board is not None and self.box_cells and self.goal_cells and self.player_pos is not None

        self.n_row, self.n_col = self.board.shape[0], self.board.shape[1]
        self.valid_moves = self.get_current_valid_moves()
        self.action_list = [action for action in Action]
        self.corner_seq_pos = [Action.LEFT, Action.UP, Action.RIGHT, Action.DOWN]
        self.boxes_in_corner = []
        self.num_actions = len(Action)
        self.debug = debug
        self.visit_count = 0
        self.did_push_box = False
        self.box_pushed = None

    # If move is not legal we can just skip the whole method
    def move(self, action):
        if action not in self.valid_moves:
            return

        player_next_pos = get_new_pos(self.player_pos, action)

        # check if next cell is a box, if yes then push box. Could check with self.cell_at but we would have to
        # compare against BOX and BOX_ON_GOAL it's faster to write but less efficient
        if player_next_pos in self.box_cells:
            self.__push_box(player_next_pos, action)
            self.did_push_box = True
            self.pushed_box = get_new_pos(player_next_pos,action)
        else:
            self.did_push_box = False
            self.pushed_box = None

        self.set_player_pos(player_next_pos)
        if self.debug:
            print_board(self.board)

        # update valid move (no need since player pos already update valid move. Player always move last
        # self.valid_moves = self.get_current_valid_moves()
        # TODO: assign boxes in corner. Is it faster if instead of checking box in corner for
        #  every move, we check after pushing box?
        self.boxes_in_corner = self.get_boxes_in_corner()

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
            if (self.cell_at(next_box_pos) is CellState.WALL or
             self.cell_at(next_box_pos) is CellState.BOX or
              self.cell_at(next_box_pos) is CellState.BOX_ON_GOAL):
                return False
            return True

    # basically iterate all possible move and check if it's valid
    def get_current_valid_moves(self):
        valid_moves = []
        for action in Action:
            if self.is_valid_move(action):
                valid_moves.append(action)
        return valid_moves

    # These now only check for hard corner, soft corner like box next to box currently not considered
    # return 2 status (game complete, failed state)
    def is_completed(self):
        if len(self.boxes_in_corner) > 0:
            for box in self.boxes_in_corner:
                if self.cell_at(box) is not CellState.BOX_ON_GOAL:
                    return True, True
        for box_pos in self.box_cells:
            if box_pos not in self.goal_cells:
                return False, False
        return True, False

    def set_player_pos(self, new_player_pos, update_valid_move=True):
        if self.player_pos == new_player_pos:
            return

        assert new_player_pos not in self.box_cells, "New player position in box position"
        assert self.cell_at(new_player_pos) is not CellState.WALL, f"New player box in wall: {new_player_pos}"

        # move player to next pos
        if new_player_pos in self.goal_cells:
            self.set_cell_at(new_player_pos, CellState.PLAYER_ON_GOAL)
        else:
            self.set_cell_at(new_player_pos, CellState.PLAYER)
        # clear current cell after moving player
        if self.player_pos in self.goal_cells:
            self.set_cell_at(self.player_pos, CellState.GOAL)
        else:
            self.set_cell_at(self.player_pos, CellState.EMPTY)

        # reset player position and valid moves
        self.player_pos = new_player_pos
        if update_valid_move:
            self.valid_moves = self.get_current_valid_moves()

    def set_box_and_player_pos(self, new_box_pos: Collection[tuple], new_player_pos: tuple):
        # These shouldn't happen, but if the code has bug it will be caught faster
        assert len(new_box_pos) == len(self.box_cells), "Number of box should be the same"
        assert all([self.cell_at(box_pos) is not CellState.WALL
                    for box_pos in new_box_pos]), f"New box positions in wall {new_box_pos}"
        assert new_player_pos not in new_box_pos

        # Everything is correct we can reset board's state now
        # reset box cell on board information
        for box_pos in self.box_cells:
            if self.cell_at(box_pos) is CellState.BOX_ON_GOAL:
                self.set_cell_at(box_pos, CellState.GOAL)
            else:
                self.set_cell_at(box_pos, CellState.EMPTY)
        
        self.box_cells = list()
        self.set_player_pos(new_player_pos, update_valid_move=False)
        #self.box_cells = []

        for box_pos in new_box_pos:
            if box_pos in self.goal_cells:
                self.set_cell_at(box_pos, CellState.BOX_ON_GOAL)
            else:
                self.set_cell_at(box_pos, CellState.BOX)
            self.box_cells.append(box_pos)
        self.valid_moves = self.get_current_valid_moves()

    # getter
    def cell_at(self, pos):
        return self.board[pos[0], pos[1]]

    # set cell to CellState
    def set_cell_at(self, pos, state):
        self.board[pos[0], pos[1]] = state

    def get_num_box_on_goal(self):
        num_box_on_goal = 0
        for box in self.box_cells:
            if box in self.goal_cells:
                num_box_on_goal += 1

        return num_box_on_goal

    def get_boxes_in_corner(self):
        boxes = []
        for box in self.box_cells:
            if self.is_box_in_corner(box):
                boxes.append(box)

        return boxes

    def is_box_in_corner(self, box):
        for i in range(len(self.corner_seq_pos)):
            if self.cell_at(get_new_pos(box, self.corner_seq_pos[i])) is CellState.WALL and \
                    self.cell_at(get_new_pos(box, self.corner_seq_pos[(i + 1) % self.num_actions])) is CellState.WALL:
                return True

        return False

    # get reachable pos from original position without pushing
    def get_adj_reachable_pos_no_push(self, pos):
        reachable_pos = []
        for action in Action:
            new_pos = get_new_pos(pos, action)
            if self.can_move_into_no_push(new_pos):
                reachable_pos.append(new_pos)

        return reachable_pos

    # check if box or player can move into one cell without pushing anything, assuming box/player is adjacent
    def can_move_into_no_push(self, pos):
        return self.cell_at(pos) is not CellState.WALL and pos not in self.box_cells

    # box is pushable only when we can reach it and two cells in opposite direction of the box are not wall/another box
    # return a dictionary that map pushable box with its pushing direction. Each pushing direction in list is a tuple
    # of (pushing action, path to pushing location)
    def get_pushable_box(self):
        pushable_box = {box: [] for box in self.box_cells}
        opposite_direction_actions = [[Action.UP, Action.DOWN], [Action.LEFT, Action.RIGHT]]

        for box, push_direction in pushable_box.items():
            for opp_action_1, opp_action_2 in opposite_direction_actions:
                opp_pos_1 = get_new_pos(box, opp_action_1)
                opp_pos_2 = get_new_pos(box, opp_action_2)
                # prelim check 2 opposite cells of box
                if self.can_move_into_no_push(opp_pos_1) and self.can_move_into_no_push(opp_pos_2):
                    path_to_pos_1 = self.bidirectional_search(self.player_pos, opp_pos_1)
                    path_to_pos_2 = self.bidirectional_search(self.player_pos, opp_pos_2)
                    # if either path is available, then add the action corresponding to pushing from that pos
                    # e.g. opp_pos_1 is the pos to the left. So from opp_pos_1, we can push to the right
                    if path_to_pos_1:
                        push_direction.append((opp_action_2, path_to_pos_1))
                    if path_to_pos_2:
                        push_direction.append((opp_action_1, path_to_pos_2))

        # remove box without push direction
        for box in list(pushable_box):  # force create copy
            if not pushable_box[box]:
                pushable_box.pop(box)

        return pushable_box

    # A* to find path from one cell pos to another cell pos
    def bidirectional_search(self, start_pos, goal_pos):
        if start_pos == goal_pos:
            return [start_pos]

        start_queue = [start_pos]
        goal_queue = [goal_pos]
        # each cell in this board points to its parent, init the board the the start and goal position
        parent_board = np.empty((self.n_row, self.n_col), dtype=tuple)
        parent_board[start_pos] = start_pos
        parent_board[goal_pos] = goal_pos
        start_visited_cells = set()
        goal_visited_cells = set()
        intersection = None  # tuple of cell from start -> end
        path = []

        # while these list both contain items (actually my first time checking if list is empty this way)
        while start_queue and goal_queue:
            intersection = self.bidirectional_expand_subroutine(start_queue, start_visited_cells, goal_visited_cells,
                                                                parent_board)
            if intersection:
                break
            intersection = self.bidirectional_expand_subroutine(goal_queue, goal_visited_cells, start_visited_cells,
                                                                parent_board)
            if intersection:
                # we just find path from goal to start so we have to reverse intersection
                intersection = intersection[::-1]
                break
            # if done here and either list is empty, then it's not reachable
            if start_queue is None or goal_queue is None:
                break
        if intersection is not None:
            path = self.bidirectional_path_reconstruction(start_pos, goal_pos, intersection, parent_board)

        return path

    # perform one step of expand in either direction, update visited cells, and check intersection condition
    # return intersection cell if found, None if not
    # here intersection is checked whenever cell is expanded, not when cell is visited, since if we don't check
    # whenever cell is expanded, parent_board position could be overridden
    def bidirectional_expand_subroutine(self, queue, this_visited_cells, other_visited_cells, parent_board):
        current_pos = queue.pop()

        this_visited_cells.add(current_pos)
        next_reachable_pos = self.get_adj_reachable_pos_no_push(current_pos)
        # filter out visited cell and cell already in queue
        next_reachable_pos[:] = [pos for pos in next_reachable_pos
                                 if pos not in this_visited_cells and pos not in queue]
        for next_pos in next_reachable_pos:  # set parent for easier path finding
            if parent_board[next_pos]:  # intersection found
                return current_pos, next_pos

            parent_board[next_pos] = current_pos
        queue.extend(next_reachable_pos)

        return None

    @staticmethod
    def bidirectional_path_reconstruction(start_pos, goal_pos, intersection, parent):
        path_from_start = []
        path_from_goal = []

        start_intersection, goal_intersection = intersection
        path_from_start.append(start_intersection)
        path_from_goal.append(goal_intersection)

        while start_intersection != start_pos:
            path_from_start.append(parent[start_intersection])
            start_intersection = parent[start_intersection]

        while goal_intersection != goal_pos:
            path_from_goal.append(parent[goal_intersection])
            goal_intersection = parent[goal_intersection]

        return path_from_start[::-1] + path_from_goal

    @staticmethod
    def action_from_path(path):
        action_sequences = []
        if len(path) <= 1:  # either invalid path or start = goal
            return action_sequences
        for i in range(len(path) - 1):
            current_pos = path[i]
            next_pos = path[i + 1]
            action_sequences.append(pos_dif_to_action[get_pos_dif(next_pos, current_pos)])
        return action_sequences

    # Functions added by Huilai
    # Please let me know if I wrongly use any attribute

    # update goal cells
    def _update_goals(self):
        # update goal_cells based on self.board
        self.goal_cells = [(i, j)
                           for i in range(self.n_row)
                           for j in range(self.n_col)
                           if self.board[i, j] == CellState.GOAL or self.board[i, j] == CellState.BOX_ON_GOAL]

    # update box cells
    def _update_boxes(self):
        # update box_cells based on self.board
        self.box_cells = [(i, j)
                          for i in range(self.n_row)
                          for j in range(self.n_col)
                          if self.board[i, j] == CellState.BOX or self.board[i, j] == CellState.BOX_ON_GOAL]

        # update player pos

    def _update_player_pos(self):
        for i in range(self.n_row):
            for j in range(self.n_col):
                if self.board[i, j] == CellState.PLAYER or self.board[i, j] == CellState.PLAYER_ON_GOAL:
                    self.player_pos = (i, j)

    # set self.board to a given board
    def __set_board_to(self, board):
        self.board = np.copy(board)
        self.goal_cells = []
        self.box_cells = []
        self.player_pos = None

        for r in range(self.board.shape[0]):
            for c in range(self.board.shape[1]):
                if self.board[r, c] == CellState.GOAL or self.board[r, c] == CellState.BOX_ON_GOAL or \
                        self.board[r, c] == CellState.PLAYER_ON_GOAL:
                    self.goal_cells.append((r, c))
                if self.board[r, c] == CellState.BOX or self.board[r, c] == CellState.BOX_ON_GOAL:
                    self.box_cells.append((r, c))
                if self.board[r, c] == CellState.PLAYER or self.board[r, c] == CellState.PLAYER_ON_GOAL:
                    self.player_pos = (r, c)

    def iterate_visit_count(self):
        self.visit_count += 1

    # checks if a box was pushed, returns a tuple of boolean, position tuple
    def get_pushed_box(self):
        #determine what box was pushed
        return self.did_push_box, self.pushed_box

    #returns true if a vertical wall adjacent to a box causes an unsolvable state, return false otherwise
    def vertical_wall_check(self, box_pos, wall_pos):
        box_x, box_y = box_pos
        wall_x, wall_y = wall_pos

        # next check if there are achievable goals on the axis that the box can still move to:
        for goal in self.goal_cells:
            goal_x,goal_y = goal
            if goal_y == box_y:
                #found a goal on this axis but can we get to it directly?
                goal_path = []
                if goal_x > box_x:
                    goal_path = self.board[box_x+1:goal_x,box_y]
                elif goal_x < box_x:
                    goal_path = np.flip(self.board[goal_x+1:box_x, box_y])
                pathable = True
                # no walls in way means that box can directly be pathed there
                for diff_x in range(0,len(goal_path)):
                    if self.cell_at(diff_x, box_y) == CellState.WALL:
                        pathable = False
                        break
                if pathable:
                    return False

        # if there are no inbound openings on wall axis, state is unsolvable
        if wall_y == 0 or wall_y == len(self.board) - 1:
            return True

        # no goals on this axis, but is there an opening that lets us escape?
        # if there is an opening there needs to b an adjacent spot to push
        wall_axis = self.board[:,wall_y]
        box_axis =  self.board[:,box_y]
        parallel_axis = []
        par_y = None
        if wall_y < box_y:
            parallel_axis = self.board[:,box_y+1]
            par_y = box_y+1
        elif wall_y > box_y:
            parallel_axis = self.board[:,box_y-1]
            par_y = box_y-1
        # keeps track if opening is part of the actual map or not, if it is inboundes there has to be a wall before it at some point
        inbounds = False
        for x in range(1, len(wall_axis)-1):
            if self.cell_at((x,box_y)) == CellState.WALL and not inbounds:
                inbounds = True
            if inbounds and np.all(self.cell_at((x,wall_y)) != CellState.WALL) and np.all(self.cell_at((x,par_y)) != CellState.WALL) and np.all(self.cell_at((x,box_y)) != CellState.WALL):
                # an opening? or is it, make sure that it is not out of bounds, make sure that box can get there
                box_path = []
                if x > box_x:
                    box_path = self.board[box_x+1:x,box_y ]
                else:
                    box_path = np.flip(self.board[x+1:box_x,box_y])
                pathable = True
                for diff_x in range(0,len(box_path)):
                    if self.cell_at((diff_x,box_y)) == CellState.WALL:
                        pathable == False
                        break
                if pathable:
                    return False
        return True

    #returns true if a horizontal wall adjacent to a box causes an unsolvable state, return false otherwise
    def horizonal_wall_check(self, box_pos, wall_pos):
        box_x, box_y = box_pos
        wall_x, wall_y = wall_pos
        # first check if there are achievable goals on the axis that the box can still move to:
        for goal in self.goal_cells:
            goal_x,goal_y = goal
            if goal_x == box_x:
                #found a goal on this axis but can we get to it directly?
                goal_path = []
                if goal_y > box_y:
                    goal_path = self.board[box_x,box_y+1:goal_y]
                elif goal_y < box_y:
                    goal_path = np.flip(self.board[box_x,goal_y+1:box_y])
                # no walls in way means that box can directly be pathed there
                pathable = True
                for diff_y in range(0,len(goal_path)):
                    if self.cell_at((box_x,diff_y)) == CellState.WALL:
                        pathable = False
                        break
                if pathable:
                    return False
        # if the wall is a problem border: state is unsolvable
        if wall_y == 0 or wall_y >= len(self.board[0])-1:
            return True
        # if there are no inbound openings on wall axis, state is unsolvable
        # no goals on this axis, but is there an opening that lets us escape?
        # if there is an opening there needs to b an adjacent spot to push
        wall_axis = self.board[wall_x,:]
        box_axis =  self.board[box_x,:]
        parallel_axis = []
        par_x = None
        if wall_x < box_x:
            parallel_axis = self.board[box_x+1,:]
            par_x = box_x+1
        elif wall_x > box_x:
            parallel_axis = self.board[box_x-1,:]
            par_x = box_x-1
        # keeps track if opening is part of the actual map or not, if it is inboundes there has to be a wall before it at some point
        inbounds = False
        for y in range(0,len(wall_axis)-1):
            if not inbounds and self.cell_at((box_x,y)) == CellState.WALL:
                inbounds = True
            elif inbounds and np.all(self.cell_at((wall_x,y)) != CellState.WALL) and np.all(self.cell_at((par_x,y)) != CellState.WALL) and np.all(self.cell_at((box_x,y)) != CellState.WALL):
                # an opening? or is it, make sure that it is not out of bounds, make sure that box can get there
                box_path = []
                if y > box_y:
                    box_path = self.board[box_x,box_y+1:y]
                else:
                    box_path = np.flip(self.board[box_x,y+1:box_y])
                walkable = True
                for diff_y in range(0,len(box_path)):
                    if self.cell_at((box_x,diff_y)) == CellState.WALL:
                        walkable == False
                        break
                if walkable:
                    return False
        return True

    def neighboring_boxes_unsovability(self,box):
        return False

    def is_unsolvable(self,box):
        x,y = box
        # case 0: box pushed on goal
        if (self.cell_at((x,y)) == CellState.BOX_ON_GOAL):
            return False

        # case0: another neighboring box has caused an unsolvable board
        if self.neighboring_boxes_unsovability(box):
            return True
        # case1: a box is in a corner that is not a goal
        # case2: a box against a wall but can still reach a goal
        # case3: a box is against a wall and can no longer reach a goal

        #identify adjacent space
        left_adjacent = (x,y-1)
        left_state = self.cell_at(left_adjacent)
        right_adjacent = (x,y+1)
        right_state = self.cell_at(right_adjacent)
        up_adjacent = (x-1,y)
        up_state = self.cell_at(up_adjacent)
        down_adjacent= (x+1,y)
        down_state = self.cell_at(down_adjacent)

        #check if in a corner
        if (left_state == CellState.WALL and up_state == CellState.WALL ) or (left_state == CellState.WALL and down_state == CellState.WALL):
            #stuck in corner
            return True
        elif (right_state == CellState.WALL and up_state == CellState.WALL) or (right_state == CellState.WALL and down_state == CellState.WALL):
            #stuck in corner
            return True
        else:
            # now check for horizontal, vertical walls that create unsolveable states

            # horizontal wall check
            if up_state == CellState.WALL:
                return self.horizonal_wall_check(box, up_adjacent)
            elif down_state == CellState.WALL:
                return self.horizonal_wall_check(box, down_adjacent)
            # vertical wall check
            elif left_state == CellState.WALL:
                return self.vertical_wall_check(box,left_adjacent)
            elif right_state == CellState.WALL:
                return self.vertical_wall_check(box,right_adjacent)
            else:
                return False

    def is_solved(self):
        for box in self.box_cells:
            if box not in self.goal_cells:
                return False
        return True
