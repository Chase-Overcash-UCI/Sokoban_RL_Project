import sys
import numpy
import util
from util import Action
from Sokoban import Sokoban
import time
import copy
import random
from Q_Node import Q_Node

class Q_Learning:
    def __init__(self):
        self.learning_rate = .01
        self.discount_factor = .98
        self.r = -.5
        self.future_unsolvability_penalty = -1
        self.visited = []
        self.box_on_goal_reward = 3

    def epsilon_greedy(self, iteration):
        rand_var = random.randint(0,100)
        if rand_var == 0:
            return True
        else:
            return False
        return

    def policy_chosen_action(self,curr):
        valid_moves = curr.sokoban.get_current_valid_moves()
        best_value = -float("inf")
        action = None
        for move in valid_moves:
            child = Q_Node(curr.sokoban,move,curr)
            if child.sokoban.board not in self.visited:
                self.visited.append(child.sokoban.board)
            state_value =  child.getValue()
            if state_value > best_value:
                best_value = state_value
                action = move
        return action

    def update_q(self,curr):
        q_value = curr.getValue()
        valid_moves = curr.get_current_valid_moves()
        best_value = -float("inf")
        action = None
        for move in valid_moves:
            child = Q_Node(curr.sokoban,move,curr)
            if child not in self.visited:
                self.visited.append(child)
            value = child.getValue()
            if value > best_value:
                best_value = value
                action = move
        child = Q_Node(curr.sokoban,action,curr)
        # after an action that pushes a box, check if that box is no longer able to go into any goal, if so penalize that state's value
        push_bool, box_pos = child.sokoban.get_pushed_box()
        if push_bool and child.sokoban.is_unsolvable():
            child.setValue(float("-INF"))
            updated_value = q_value + self.learning_rate*(self.future_unsolvability_penalty+self.discount_factor*best_value - q_value)
            curr.setValue(updated_value)
            return curr
            #print("unsolvable state")
            # penalize value of state
        else:
            if child.sokoban.is_solved():
                print("solved")
                # run path on board from here
                sys.exit(1)
            else:
                #update these
                updated_q_val = child.sokoban.get_num_box_on_goal() - curr.sokoban.get_num_box_on_goal() * self.box_on_goal_reward
                newValue = updated_q_val + self.learning_rate*(self.r + self.discount_factor*best_value - q_value)
                curr.setValue(newValue)
        return child_state

    def exploration(self, root, training_iterations):
        # agent starts exploration
        node = root
        for i in range(0, training_iterations):
            sokoban = copy.deepcopy(node.sokoban)
            while not sokoban.is_completed():
                valid_moves = sokoban.get_current_valid_moves()
                for move in valid_moves:
                    action = None
                    if self.epsilon_greedy():
                        action = move
                    else:
                        action = self.policy_chosen_action(sokoban)
                    curr = Q_Node(sokoban,action,node)
                    if  curr.sokoban not in self.visited:
                        self.visited.append(curr.sokoban)
                    node = copy.deepcopy(update_q(curr))







