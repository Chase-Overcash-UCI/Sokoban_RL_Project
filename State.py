import sys

import numpy

import util
from util import Action
from Sokoban import Sokoban
import time
import copy

#Create Node for Search Graph
class State:
    def __init__(self, sokoban, parent, parent_direction):
        # constructs the root node
        if parent is None:
            self.sokoban = sokoban
            self.parent = None
            self.parent_direction = None
            self.x,self.y = sokoban.player_pos
            self.path = ''
        else:
            temp = copy.deepcopy(parent)
            self.parent_direction = parent_direction
            temp.sokoban.move(parent_direction)
            self.path = temp.path + str(parent_direction)
            self.sokoban = temp.getSokoban()
            self.parent = parent
            self.x,self.y = temp.sokoban.player_pos

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getPath(self):
        return self.path

    def getPos(self):
        return self.x, self.y

    def getSokoban(self):
        return self.sokoban

    def getNewPos(self, x, y, direction):
        if direction == Action.UP:
            newX = x - 1
            return newX, y
        elif direction == Action.DOWN:
            newX = x + 1
            return newX, y
        elif direction == Action.LEFT:
            newY = y - 1
            return x, newY
        elif direction == Action.RIGHT:
            newY = y + 1
            return x, newY

    def hasVisited(self,visited, curr_board):
        if len(visited) == 0:
            return False
        for board in visited:
            if numpy.all(board == curr_board):
                return True
            #else:
                #print("Not Equal")
        return False;

    def DFS(self, root):
        visited = []
        frontier = []
        curr = root
        frontier.append(root)
        start_time = time.time_ns()
        diving = True
        while diving:
            if len(frontier) == 0:
                print("DFS failed")
                return
            curr = frontier.pop()
            if not self.hasVisited(visited,curr.sokoban.board):
                visited.append(curr.sokoban.board)
                if curr.sokoban.is_completed():
                    print("soln found")
                    return curr.getPath()
                for move in curr.sokoban.get_current_valid_moves():
                    child = State(curr.sokoban,curr,move)
                    if not self.hasVisited(visited,child.sokoban.board):
                        frontier.append(child)