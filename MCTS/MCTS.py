import numpy as np
import rl_util as rlult
from Sokoban import Sokoban

MAX_DEPTH = 10
MAX_EPISODE = 1000

def MCTS_step(board):
    sokoban = Sokoban(board)
    valid_acts = sokoban.valid_moves
    agent = dict()
    for a in valid_acts:
        agent[a] = 0
    
    for episode in range(MAX_EPISODE):
        update_agent(sokoban,agent)

    action = pick_best_action(agent)
    return action


def update_agent(env, agent):
    for step in range(MAX_DEPTH):
        a = random_action(env.valid_moves)
        env.move(a)

def random_action(valid_actions):
    return np.random.choice(valid_actions) 

