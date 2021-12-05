from MCTS import *
from Sokoban import Sokoban

if __name__ == '__main__':
    file = 'sample_inputs\sokoban01.txt'
    game = Sokoban(file)
    
    while True:
        b = game.board
        #print(b)
        action = MCTS_step(b)
        game.move(action)
        #input()