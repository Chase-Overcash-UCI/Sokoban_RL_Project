import sys

import numpy
from util import Action
from Sokoban import Sokoban
import time

#Create Node for Search Graph
class State:
    def __init__(self, board, parent, parent_direction):
        # constructs the root node
        if parent is None:
            self.board  = board
            self.parent = parent
            self.parent_direction = parent_direction
            self.x,self.y = board.player_pos
            self.path = ''
        else:
            self.board = board
            self.parent = parent
            self.parent_direction = parent_direction
            self.x,self.y = board.player_pos
            self.path = parent.path + str(parent_direction)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getPath(self):
        return self.path

    def getPos(self):
        return self.x, self.y

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

    def BFS(self, root):
        visited = []
        frontier = []
        root_node = root
        frontier.append(root)
        start_time = time.time_ns()
        bread = True
        while bread:
            if not frontier:
                print("BFS failed")
                return
            curr = frontier.pop(0)
            visited.append(curr.getPos())
            valid_moves = curr.board.get_current_valid_moves()
            for move in valid_moves:
                print(move)
                newX,newY = self.getNewPos(curr.x, curr.y, move)
                child = State(curr.board,curr,move)
                child.board.move(move)
                print(visited)
                print(child.getPos())
                has_visited = False
                for states in visited:
                    if states == child.getPos():
                        has_visited = True
                        break
                if not has_visited:
                    if curr.board.is_completed():
                        end_time = time.time_ns()
                        print(child.getPath())
                        print("Time taken:" + str(end_time - start_time))
                        sys.exit("BFS Succeeded")
                    frontier.append(child)