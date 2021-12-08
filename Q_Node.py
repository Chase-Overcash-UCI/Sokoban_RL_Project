import sys
import numpy
import util
from util import Action
from Sokoban import Sokoban
import time
import copy

class Q_Node:
    def __init__(self, sokoban, parent_action, parent):
        if parent is None:
            self.parent = None
            self.action = None
            self.sokoban = sokoban
            self.path = ''
            self.key = ''
            self.set_hash_key()

        else:
            temp = copy.deepcopy(sokoban)
            temp.move(parent_action)
            self.sokoban = temp
            self.action = parent_action
            self.path = parent.path + str(parent_action)
            self.key = ''
            self.set_hash_key()
            self.parent = parent

    def getSokoban(self):
        return self.sokoban

    def setSokoban(self, new_sokoban):
        self.sokoban = copy.deepcopy(new_sokoban)

    def getAction(self):
        return self.action

    def setAction(self, new_action):
        self.action = new_action

    def setValue(self,new_value):
        self.value = new_value

    def getValue(self):
        return self.value

    def set_hash_key(self):
        hash_key = ''
        for row in range(len(self.sokoban.board)):
            for col in range(len(self.sokoban.board[0])):
                hash_key += str(self.sokoban.board[row][col])
        self.key = hash_key

    def get_hash_key(self):
        return self.key
