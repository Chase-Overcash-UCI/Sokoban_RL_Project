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
        self.learning_rate = .03
        self.reward_decay = .09
        self.box_reward = 1000
        self.discount_factor = 0
        self.random_decay = .999
        self.q_dictionary = {}
        self.path = ''


    def assign_key(self,qnode):
        key = str(qnode.action)
        for row in range(len(qnode.sokoban.board)):
            for col in range(len(qnode.sokoban.board[0])):
                key = key + str(qnode.sokoban.board[row][col])
        return key


    def epsilon_greedy(self, iteration):
        rand_var = random.randint(0,100)
        if rand_var == 0:
            return True
        else:
            return False
        return


    def sokoban_chosen_policy(self,sokoban):
        valid_moves = sokoban.get_current_valid_moves()
        best_value = -float("inf")
        action = None
        for move in valid_moves:
            curr = Q_Node(sokoban,move)
            key = self.assign_key(curr)
            if  key not in self.q_dictionary:
                self.q_dictionary[key] = 0.0
            value = self.q_dictionary.get(key)
            if value > best_value:
                best_value = value
                action = move
        return action

    def update_q(self,curr):
        q = self.q_dictionary.get(self.assign_key(curr))
        child_state = copy.deepcopy(curr.sokoban)
        child_state.move(curr.action)
        child_state.iterate_visit_count()
        valid_moves = child_state.get_current_valid_moves()
        best_value = -float("inf")
        move = None
        for move in valid_moves:
            child = Q_Node(child_state,move)
            key = self.assign_key(child)
            if key not in self.q_dictionary:
                self.q_dictionary[key] = 0.0
            value = self.q_dictionary.get(key)
            if value > best_value:
                best_value = value
        # TO DO: after an action that pushes a box, check if that box is no longer able to go into any goal
        if child_state.is_unsolvable():
            print("unsolvable state")
            # penalize value of state
        else:
            if child_state.is_completed():
                print("solved")
                return
            else:
                reward = (child_state.get_num_box_on_goal() - curr.sokoban.get_num_box_on_goal()) * self.box_reward + self.discount_factor
                newValue = q + self.learning_rate*(reward+self.reward_decay*best_value - q)
                self.q_dictionary.update(self.assign_key(curr),newValue)
        return child_state

    def exploration(self, state, training_iterations):
        # agent starts exploration
        sokoban = copy.deepcopy(state)
        for i in range(0, training_iterations):
            while not sokoban.is_completed():
                valid_moves = sokoban.get_current_valid_moves()
                # randomly picks a valid action
                rand_index = random.randint(0,len(valid_moves)-1)
                selected_action = valid_moves[rand_index]
                policy_action = self.sokoban_chosen_policy(sokoban)
                action = None
                if self.epsilon_greedy(i):
                    action = selected_action
                else:
                    action = policy_action
                curr = Q_Node(sokoban,action)
                if  self.assign_key(curr) not in self.q_dictionary:
                    self.q_dictionary[self.assign_key(curr)] = 0.0
                sokoban = self.update_q(curr)






