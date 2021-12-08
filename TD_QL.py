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
        self.learning_rate = .1
        self.discount_factor = .98
        self.r = -1
        self.future_unsolvability_penalty = -2
        self.visited = {}
        self.box_on_goal_reward = 100

    def manhatten_hint_goals(self,sokoban, pos):
        min = 10000.0
        for goal in sokoban.goal_cells:
            dist = util.manhattan_distance(pos,goal)
            if dist < min:
                min = dist
        min = min * -1
        print(min)
        return min

    def manhatten_hint_boxes(self,sokoban, pos):
        min = 10000.0
        for box in sokoban.box_cells:
            dist = util.manhattan_distance(pos,box)
            if dist < min:
                min = dist
        min = min * -1
        print(min)
        return min


    def epsilon_greedy(self):
        rand_var = random.randint(0,100)
        print(rand_var)
        if rand_var <= 4:
            return True
        else:
            return False
        return

    def policy_chosen_action(self,curr):
        valid_moves = curr.sokoban.get_current_valid_moves()
        best_value = -100000.0
        action = None
        for move in valid_moves:
            child = Q_Node(curr.sokoban,move,curr)
            if  child.get_hash_key() not in self.visited:
                self.visited[child.get_hash_key()] = self.manhatten_hint_boxes(child.sokoban,child.sokoban.player_pos)
            state_value =  self.visited[child.get_hash_key()]
            if state_value > best_value:
                best_value = state_value
                action = move
        return action

    def update_q(self,curr):
        valid_moves = curr.sokoban.get_current_valid_moves()
        child = Q_Node(curr.sokoban,self.policy_chosen_action(curr),curr)
        # after an action that pushes a box, check if that box is no longer able to go into any goal, if so penalize that state's value
        push_bool, box_pos = child.sokoban.get_pushed_box()
        push_reward = 0
        if push_bool:
            if child.sokoban.is_unsolvable(box_pos):
                self.visited[child.get_hash_key()] = -10000
                q_value = self.visited[curr.get_hash_key()]
                updated_value = q_value + self.learning_rate*(self.r+self.discount_factor*0 - q_value)
                self.visited[curr.get_hash_key()] = updated_value
                return curr, self.visited[curr.get_hash_key()]
                #print("unsolvable state")
                # penalize value of state
            elif self.manhatten_hint_goals(child.sokoban,box_pos) < self.manhatten_hint_goals(child.sokoban,child.sokoban.player_pos):
                push_reward = 10
        if child.sokoban.is_solved():
            # update values?
            print("solved")
            # run path on board from here
            sys.exit(1)
        else:
            # update q values
            q_value = self.visited[curr.get_hash_key()]
            updated_reward = child.sokoban.get_num_box_on_goal() - curr.sokoban.get_num_box_on_goal() * self.box_on_goal_reward + self.r
            newValue = q_value + self.learning_rate*(updated_reward + self.discount_factor* self.visited[child.get_hash_key()]- q_value) + push_reward
            self.visited[curr.get_hash_key()] = newValue
        return child, self.visited[child.get_hash_key()]

    def exploration(self, root, training_iterations):
        # agent starts exploration
        node = root
        self.visited[node.get_hash_key()] = self.manhatten_hint_boxes(node.sokoban,node.sokoban.player_pos)
        for i in range(0, training_iterations):
            while not node.sokoban.is_solved():
                valid_moves = node.sokoban.get_current_valid_moves()
                action = None
                if self.epsilon_greedy():
                    rand_index = numpy.random.randint(0,len(valid_moves))
                    action = valid_moves[rand_index]
                else:
                    action = self.policy_chosen_action(node)
                curr = Q_Node(node.sokoban,action,node)
                push_bool, box_pos  = curr.sokoban.get_pushed_box()
                push_reward = 0
                if push_bool:
                    if curr.sokoban.is_unsolvable(box_pos):
                        self.visited[curr.get_hash_key()] = -10000
                        node = root
                        continue
                    elif self.manhatten_hint_goals(curr.sokoban,box_pos) < self.manhatten_hint_goals(curr.sokoban,curr.sokoban.player_pos):
                        push_reward = 10
                if curr.get_hash_key() not in self.visited:
                    self.visited[curr.get_hash_key()] = self.manhatten_hint_boxes(curr.sokoban,curr.sokoban.player_pos) + push_reward
                q_value = self.visited[node.get_hash_key()]
                child_node, child_value = self.update_q(curr)
                newValue = q_value + self.learning_rate * (self.r + self.discount_factor *child_value- q_value) + push_reward
                self.visited[node.get_hash_key()] = newValue
                node = child_node