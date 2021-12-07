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
        self.reward_decay = .98
        self.discount_factor = 0
        self.visited = []

    def epsilon_greedy(self, iteration):
        rand_var = random.randint(0,100)
        if rand_var == 0:
            return True
        else:
            return False
        return

    def TD_0(self,sokoban):
        valid_moves = sokoban.get_current_valid_moves()
        best_value = -float("inf")
        action = None
        # TO DO: TD_0
        return action

    def update_q(self,curr):
        q_value = curr.getValue()
        valid_moves = curr.get_current_valid_moves()
        new_q_value = -float("inf")
        action = None
        for move in valid_moves:
            child = Q_Node(curr.sokoban,move,curr)
            if child not in self.visited:
                self.visited.append(child)
            value = child.getValue()
            if value > best_value:
                best_value = value
                action = move
        # TO DO: after an action that pushes a box, check if that box is no longer able to go into any goal
        if child.sokoban.is_unsolvable():
            print("unsolvable state")
            # penalize value of state
        else:
            if child.sokoban.is_completed():
                print("solved")
                return
            else:
                #update these
                newValue = q_value + self.learning_rate*(self.discount_factor +self.reward_decay*best_value - q)
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
                        action = self.TD_0(sokoban)
                    curr = Q_Node(sokoban,action,node)
                    if  curr.sokoban not in self.visited:
                        self.visited.append(curr.sokoban)
                    node = copy.deepcopy(update_q(curr))







