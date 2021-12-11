from Sokoban import Sokoban
import copy
import numpy as np
from util import print_board, manhattan_distance
from SokobanGame import SokobanPygame

AD_FREQ = 500  # frequency of adjusting epsilon
EPSILON = 0.2  # for epsilon greedy, 0 <= EPSILON <= 1
EPSILON_DROP_RATE = 0.85  # epsilon *= EPSILON_DROP_RATE for every AD_FREQ episode
ALPHA = 0.01  # Learning rate
GAMMA = 0.8  # TD DISCOUNT FACTOR
MAX_DEPTH = 200
MAX_EPISODE = 10000


class agent:

    def __init__(self, file):
        self.game_engine = SokobanPygame(input_file=file, debug=False)
        self.game = self.game_engine.game
        # self.game = Sokoban(input_path=file, debug=False)
        self.epsilon = EPSILON

        self.board = copy.copy(self.game.board)
        self.player = copy.copy(self.game.player_pos)
        self.boxes = copy.copy(self.game.box_cells)

        self.value_board = dict()

    def MCTS(self):
        solved = False
        episode = 0
        while not solved:
            # print('new episode')
            step = 0
            solution = list()
            states = set()
            done = False
            episode += 1

            while (not done) and (step < MAX_DEPTH):
                # current_state = self.get_current_state()
                # states.add(current_state)
                # action = self.get_next_action()

                # done, r = self.make_move(action, step)
                # solution.append(action)
                solved, done, r = self.MC_step(step, solution, states)
                step += 1

            if (episode % AD_FREQ == 0):
                self.epsilon *= EPSILON_DROP_RATE
                print('episode:', episode, '______________________________________')
                print_board(self.game.board)

            self.MC_update(states, r)
            self.game.set_box_and_player_pos(self.boxes, self.player)

            if episode >= MAX_EPISODE:
                # restart
                episode = 0
                self.value_board = dict()
                self.epsilon = EPSILON

        return solution

    def TD(self):
        solved = False
        episode = 0
        while not solved:
            step = 0
            solution = list()
            done = False
            episode += 1

            while (not done) and (step < MAX_DEPTH):
                solved, done = self.TD_step(step, solution)
                self.game_engine.render()
                step += 1

            if episode % AD_FREQ == 0:
                self.epsilon *= EPSILON_DROP_RATE
                print('episode:', episode, '______________________________________')
                print_board(self.game.board)

            self.game.set_box_and_player_pos(self.boxes, self.player)

            if episode >= MAX_EPISODE:
                # restart
                episode = 0
                self.value_board = dict()
                self.epsilon = EPSILON

        return solution

    def TD_step(self, step, solution):
        current_state = self.get_current_state()
        action = self.get_next_action()
        solved, done, r = self.make_move(action, step)
        solution.append(action)
        next_state = self.get_current_state()
        self.TD_update(current_state, next_state, r)
        return solved, done

    def MC_step(self, step, solution, states):
        current_state = self.get_current_state()
        states.add(current_state)
        action = self.get_next_action()
        solution.append(action)
        return self.make_move(action, step)

    def get_next_action(self):
        self.game.valid_moves = self.game.get_current_valid_moves()
        valid_acts = self.game.valid_moves

        next_states = [(a, self.get_state_value(self.get_next_state(a))) for a in valid_acts]
        return self.epsilon_greedy_move(valid_acts, next_states)

    def epsilon_greedy_move(self, valid_acts, next_states):
        if np.random.uniform(0.0, 1.0) < self.epsilon:
            # RANDOM
            return np.random.choice(valid_acts)
        else:
            return self.get_best_move(next_states)

    def get_best_move(self, next_states):
        value = float('-inf')
        for element in next_states:
            if element[1] >= value:
                value = element[1]
                action = element[0]
        return action

    def get_state_value(self, state):
        try:
            return self.value_board[state]
        except:
            self.value_board[state] = 0
            return 0

    def get_next_state(self, action):
        # print(action)
        temp_player = copy.copy(self.game.player_pos)
        temp_boxes = copy.copy(self.game.box_cells)

        # get the state assuming taking the given action
        self.game.move(action)
        next_state = self.get_state(self.game.player_pos, self.game.box_cells)

        # reset the board to original state
        self.game.set_box_and_player_pos(temp_boxes, temp_player)
        return next_state

    def get_state(self, player, boxes):
        return (player, frozenset(boxes))

    def get_current_state(self):
        return self.get_state(self.game.player_pos, self.game.box_cells)

    def get_num_on_goal(self):
        num_on_goal = 0
        for box in self.game.box_cells:
            for goal in self.game.goal_cells:
                if (box == goal):
                    num_on_goal += 1
                    break
        return num_on_goal

    def get_reward(self, step, done, solved, on_off_goal, static_deadlocked=False, frozen_deadlock=False):
        temp = 2 * int(solved) - int(done)
        deadlock_penalty = int(static_deadlocked) + int(frozen_deadlock)
        distance_heuristics = 0
        for box in self.game.box_cells:
            total_distance = 0
            for goal in self.game.goal_cells:
                total_distance += manhattan_distance(box, goal)
            distance_heuristics += total_distance
        return step * (-1) + int(on_off_goal) * 100 + temp * 100 - 20 * deadlock_penalty - 20 * distance_heuristics

    def is_solved(self):
        for box in self.game.box_cells:
            if box not in self.game.goal_cells:
                return False
        return True

    def MC_update(self, states, r):
        for state in states:
            try:
                self.value_board[state] += ALPHA * (r - self.value_board[state])
            except:
                self.value_board[state] = ALPHA * (r - 0)

    def TD_update(self, current, next, r):
        if current not in self.value_board.keys():
            self.value_board[current] = 0
        if next not in self.value_board.keys():
            self.value_board[next] = 0

        self.value_board[current] += ALPHA * (r + GAMMA * self.value_board[next] - self.value_board[current])

    def make_move(self, action, step):
        num_on_goal = self.get_num_on_goal()
        self.game.move(action)
        on_off_goal = self.get_num_on_goal() - num_on_goal  # change in number of boxes on goals, 1 if the prev action pushes a box on goal, 0 if no change, -1 if prev action pushes a box off goal.

        done, failed = self.game.is_completed()
        solved = self.is_solved()

        just_pushed, box_pushed = self.game.get_pushed_box()
        static_deadlock = False
        frozen_box_deadlock = False
        if just_pushed:
            if self.game.deadlock_map[box_pushed]:
                static_deadlock = True
                # print("Unsolvable")
            if self.game.is_frozen_box_unsolvable(box_pushed):
                frozen_box_deadlock = True
                # print("Frozen boxes not on goal detected => Unsolvable")
        done = done or static_deadlock or frozen_box_deadlock

        r = self.get_reward(step, done, solved, on_off_goal, static_deadlock, frozen_box_deadlock)
        return solved, done, r
