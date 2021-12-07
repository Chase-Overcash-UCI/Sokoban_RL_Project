import sys
import numpy
import util
from util import Action
from Sokoban import Sokoban
import time
import copy

class Q_Node:
    def __init__(self, sokoban, action):
        self.sokoban = copy.deepcopy(sokoban)
        self.action = action

    def getSokoban(self):
        return self.sokoban

    def setSokoban(self, newSokoban):
        self.sokoban = copy.deepcopy(newSokoban)

    def getAction(self):
        return self.action

    def setAction(self, newAction ):
        self.action = newAction