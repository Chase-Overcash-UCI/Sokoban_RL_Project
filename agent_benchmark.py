from agent import agent
from Sokoban import Sokoban
from util import print_board, soln_to_str
from os import listdir
import time

if __name__ == '__main__':
    path = 'sample_inputs\\benchmarks\\'
    counter = 0
    for f in listdir(path):
        start = time.time()
        file = path+f
        print(file)
        counter += 1
        game = Sokoban(file)
        my_agent = agent(file)

        solution = my_agent.TD()
        print('DONE level ' + str(counter) + '____________________________________')
        string = soln_to_str(solution)
        print('solution length:', len(string))
        print('solution: ', string)
        print(time.time() - start)