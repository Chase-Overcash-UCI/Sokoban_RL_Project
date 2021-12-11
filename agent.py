from Sokoban import Sokoban
from SokobanGame import SokobanPygame
import copy
import numpy as np
from util import print_board
import pygame
import random
import time

AD_FREQ = 500  # frequency of adjusting epsilon
EPSILON = 0.2  # for epsilon greedy, 0 <= EPSILON <= 1
EPSILON_DROP_RATE = 0.85  # epsilon *= EPSILON_DROP_RATE for every AD_FREQ episode
ALPHA = 0.01  # Learning rate
GAMMA = 0.9  # TD DISCOUNT FACTOR
MAX_DEPTH = 200
MAX_EPISODE = 10000

def input_wait():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                time.sleep(5)
            elif event.key == pygame.K_q:
                exit(0)
        elif event.type == pygame.QUIT:
            exit(0)


class agent:

    def __init__(self, input_file):
        self.game_engine = SokobanPygame(input_file=input_file, debug=False)
        self.game = self.game_engine.game
        self.epsilon = EPSILON

        self.board = copy.copy(self.game.board)
        self.player = copy.copy(self.game.player_pos)
        self.boxes = copy.copy(self.game.box_cells)
        self.visited = None

        self.value_board = dict()

    # def MCTS(self):
    #     solved = False
    #     episode = 0
    #     while not solved:
    #         # print('new episode')
    #         step = 0
    #         solution = list()
    #         states = set()
    #         done = False
    #         episode += 1
    #
    #         while (not done) and (step < MAX_DEPTH):
    #             # current_state = self.get_current_state()
    #             # states.add(current_state)
    #             # action = self.get_next_action()
    #
    #             # done, r = self.make_move(action, step)
    #             # solution.append(action)
    #             solved, done, r = self.MC_step(step, solution, states)
    #             step += 1
    #
    #         if (episode % AD_FREQ == 0):
    #             self.epsilon *= EPSILON_DROP_RATE
    #             print('episode:', episode, '______________________________________')
    #             print_board(self.game.board)
    #
    #         self.MC_update(states, r)
    #         self.game.set_box_and_player_pos(self.boxes, self.player)
    #
    #         if episode >= MAX_EPISODE:
    #             # restart
    #             episode = 0
    #             self.value_board = dict()
    #             self.epsilon = EPSILON
    #
    #     return solution

    def TD(self):
        solved = False
        episode = 0
        self.visited = dict()
        while not solved:
            step = 0
            solution = list()
            done = False
            episode += 1

            while (not done) and (step < MAX_DEPTH):
                solved, done = self.TD_step(step, solution)
                step += 1
                if not done:
                    input_wait()
                    self.game_engine.render()
                # print(step)

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
        current_state = self.get_current_state()            # tuple(player_pos, frozenset(box list))
        action = self.get_next_action()                     # TODO: tuple(next_player_pos, action)
        if action is None:
            return False, True
        solved, done, r = self.make_move(action, step)      # move using action
        solution.append(action)                             # do this later?
        next_state = self.get_current_state()               # OK
        self.TD_update(current_state, next_state, r)
        return solved, done

    # def MC_step(self, step, solution, states):
    #     current_state = self.get_current_state()
    #     states.add(current_state)
    #     action = self.get_next_action()
    #     solution.append(action)
    #     return self.make_move(action, step)

    # Next action will explore pushable boxes instead of next valid action
    # Changed
    def get_next_action(self):
        # self.game.valid_moves = self.game.get_current_valid_moves()
        # valid_acts = self.game.valid_moves
        #
        # next_states = [(a, self.get_state_value(self.get_next_state(a))) for a in valid_acts]
        # next_action = self.epsilon_greedy_move(valid_acts, next_states)
        # print(next_states)'
        pushable_boxes = self.game.get_pushable_box()
        valid_acts = []
        for box in pushable_boxes:
            for action, path in pushable_boxes[box]:
                valid_acts.append((path[-1], action))
        if not valid_acts:
            return None
        next_states = [(a, self.get_state_value(self.get_next_state(a))) for a in valid_acts]
        next_action = self.epsilon_greedy_move(valid_acts, next_states)

        return next_action

    # No need to change
    def epsilon_greedy_move(self, valid_acts, next_states):
        if np.random.uniform(0.0, 1.0) < self.epsilon:
            # RANDOM
            return random.choice(valid_acts)
        else:
            return self.get_best_move(next_states)

    # No need to change
    def get_best_move(self, next_states):
        value = float('-inf')
        for element in next_states:
            if element[1] >= value:
                value = element[1]
                action = element[0]
        return action

    # No need to change
    def get_state_value(self, state):
        try:
            return self.value_board[state]
        except:
            self.value_board[state] = 0
            return 0

    # Changed
    def get_next_state(self, action):
        # # print(action)
        # temp_player = copy.copy(self.game.player_pos)
        # temp_boxes = copy.copy(self.game.box_cells)
        #
        # # get the state assuming taking the given action
        # self.game.move(action)
        # next_state = self.get_state(self.game.player_pos, self.game.box_cells)
        #
        # # reset the board to original state
        # self.game.set_box_and_player_pos(temp_boxes, temp_player)

        new_player_pos, next_action = action
        checkpoint = self.game.create_board_checkpoint()
        self.game.set_player_pos(new_player_pos)
        self.game.move(next_action)
        next_state = self.get_state(self.game.player_pos, self.game.box_cells)
        self.game.restore_checkpoint(checkpoint)

        return next_state

    # OK
    def get_state(self, player, boxes):
        return (player, frozenset(boxes))

    def get_state_v2(self, box_config):
        pass

    # OK
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

    def get_reward(self, step, done, solved, on_off_goal, static_deadlock=False, frozen_deadlock=False, visit_count=0):
        temp = 2 * int(solved) - int(done)
        deadlock_penalty = int(static_deadlock) * (-100) + int(frozen_deadlock) * (-100)
        visited_penalty = visit_count * (-1)
        print(visited_penalty)
        return step * (-1) + int(on_off_goal) * (10.0) + temp * (100.0) + deadlock_penalty + visited_penalty

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
        # num_on_goal = self.get_num_on_goal()
        # self.game.move(action)
        # on_off_goal = self.get_num_on_goal() - num_on_goal  # change in number of boxes on goals, 1 if the prev action pushes a box on goal, 0 if no change, -1 if prev action pushes a box off goal.
        #
        # done, failed = self.game.is_completed()
        # solved = self.is_solved()
        #
        # r = self.get_reward(step, done, solved, on_off_goal)
        # return solved, done, r

        new_player_pos, next_action = action
        num_on_goal = self.get_num_on_goal()
        self.game.set_player_pos(new_player_pos)
        self.game.move(next_action)
        on_off_goal = self.get_num_on_goal() - num_on_goal  # change in number of boxes on goals, 1 if the prev action pushes a box on goal, 0 if no change, -1 if prev action pushes a box off goal.

        _, just_pushed = self.game.get_pushed_box()
        static_deadlock = False
        frozen_box_deadlock = False
        if self.game.deadlock_map[just_pushed]:
            static_deadlock = True
            print("Unsolvable")
        if self.game.is_frozen_box_unsolvable(just_pushed):
            frozen_box_deadlock = True
            print("Frozen boxes not on goal detected => Unsolvable")

        pushable_boxes = self.game.get_pushable_box()
        box_state = ((*sorted(self.game.box_cells)), *sorted(frozenset(pushable_boxes)))
        if box_state not in self.visited:
            self.visited[box_state] = 0
        self.visited[box_state] += 1

        done, failed = self.game.is_completed()
        done = done or static_deadlock or frozen_box_deadlock

        solved = self.is_solved()

        r = self.get_reward(step, done, solved, on_off_goal,
                            static_deadlock, frozen_box_deadlock, self.visited[box_state])
        return solved, done, r

