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
            action = None
            self.sokoban = sokoban
            self.path = ''
            self.value = 0.0
        else:
            temp = copy.deepcopy(sokoban)
            self.sokoban = temp.move(parent_action)
            self.action = parent_action
            self.path = parent.path + str(parent_action)
            self.value = parent.value * .98 #need to doublecheck

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