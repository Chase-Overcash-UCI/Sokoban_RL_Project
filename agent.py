from Sokoban import Sokoban
import copy
import numpy as np
from util import print_board

EPSILON = 1 # for epsilon greedy, 0 <= EPSILON <= 1
ALPHA = 0.1 # Learning rate
MAX_DEPTH = 100
#MAX_EPISODE = 10000


class agent:

    def __init__(self, file):
        self.game = Sokoban(input_path=file,debug=False)
        self.epsilon = EPSILON
        
        self.board = copy.copy(self.game.board)
        self.player = copy.copy(self.game.player_pos)
        self.boxes = copy.copy(self.game.box_cells)
    
        self.value_board = dict()

    def MCTS(self):
        solved = False
        episode = 0
        while not solved:
            #print('new episode')
            step = 0
            solution = list()
            states = set()
            done = False
            episode += 1

            while (not done) and (step < MAX_DEPTH):
                current_state = self.get_current_state()
                states.add(current_state)
                action = self.MCTS_step()
                
                done, r = self.make_move(action, step)
                solution.append(action)
                step += 1

            if (episode % 1000 == 0):
                self.epsilon *= 0.9
                print('episode:',episode,'______________________________________')
                print_board(self.game.board)
                #input()

            solved = self.is_solved()
            if solved:
                return solution

            #print('update')
            # MC update
            self.MC_update(states,r)
            #print('reset')
            #print(self.game.box_cells)
            #print(self.game.player_pos)
            #print(self.player)
            #print(self.boxes)
            #print_board(self.game.board)
            # Reset
            self.game.set_box_and_player_pos(self.boxes,self.player)

        return solution


    def MCTS_step(self):
        self.game.valid_moves = self.game.get_current_valid_moves()
        valid_acts = self.game.valid_moves
        
        next_states = [(a,self.get_state_value(self.get_next_state(a))) for a in valid_acts]
        return self.epsilon_greedy_move(valid_acts, next_states)

    def epsilon_greedy_move(self,valid_acts, next_states):
        if np.random.uniform(0.0,1.0) < self.epsilon:
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
        #print(action)
        temp_player = copy.copy(self.game.player_pos)
        temp_boxes = copy.copy(self.game.box_cells)

        # get the state assuming taking the given action
        self.game.move(action)
        next_state = self.get_state(self.game.player_pos, self.game.box_cells)
        
        # reset the board to original state
        self.game.set_box_and_player_pos(temp_boxes, temp_player)
        #self.game.valid_moves = self.game.get_current_valid_moves()
        return next_state 
    
    def get_state(self, player, boxes):
        return (player,frozenset(boxes))

    def get_current_state(self):
        return self.get_state(self.game.player_pos,self.game.box_cells)

    def get_num_on_goal(self):
        num_on_goal = 0
        for box in self.game.box_cells:
            for goal in self.game.goal_cells:
                if (box == goal):
                    num_on_goal += 1
                    break
        return num_on_goal

    def get_reward(self, step, done, solved, on_off_goal):
        temp = 2*int(solved) - int(done)
        return step*(-0.1) + int(on_off_goal) * (1.0) + temp * (10.0)

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


    def make_move(self, action, step):
        num_on_goal = self.get_num_on_goal()
        self.game.move(action)
        on_off_goal = self.get_num_on_goal() - num_on_goal # change in number of boxes on goals, 1 if the prev action pushes a box on goal, 0 if no change, -1 if prev action pushes a box off goal.
        
        done = self.game.is_completed()
        solved = self.is_solved()

        r = self.get_reward(step,done,solved,on_off_goal)
        return done, r

    