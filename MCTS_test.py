from agent import agent
from Sokoban import Sokoban
from util import print_board

if __name__ == '__main__':
    file = 'sample_inputs\sokoban01.txt'
    game = Sokoban(file)
    my_agent = agent(file)
    
    print_board(my_agent.game.board)
    while True:
        solution = my_agent.MCTS()
        print('\n\n\nDONE__________________________________________')
        counter = 0
        for a in solution:
            counter += 1
            game.move(a)
            input('PAUSE')