import numpy as np
import rl_util as rlult
import Sokoban

MAX_DEPTH = 10
MAX_EPISODE = 1000

def MCTS_step(board, boxes, tars):
    sokoban = Sokoban(board) # not implemented yet
    b = np.copy(board)

    agent = dict()
    for episode in range(MAX_EPISODE):
        update_agent(b,agent)

def update_agent(board, agent):
    a = random_action(get_valid_actions(board))

def random_action(valid_actions):
    return np.random.choice(valid_actions) 

