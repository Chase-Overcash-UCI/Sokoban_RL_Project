import numpy as np
import rl_util as rlult
from Sokoban import Sokoban

MAX_DEPTH = 5
MAX_EPISODE = 10000

def MCTS_step(board):
    
    sokoban = Sokoban('XD', True, 1, np.copy(board))

    valid_acts = sokoban.valid_moves
    agent = dict()
    action_counter = dict()

    # Build a value board for valid next actions
    for a in valid_acts:
        agent[a] = 0
        action_counter[a] = 0

    # Do MCTS to update the value board
    for episode in range(MAX_EPISODE):
        first_a, r = MCTS_episode(sokoban)
        agent[first_a] += r
        sokoban = Sokoban('XD', True, 1, np.copy(board))
    
    for a in agent.keys():
        if action_counter[a] == 0:
            action_counter[a] += 1
        agent[a] /= action_counter[a]

    action = pick_best_action(agent)
    return action


def MCTS_episode(env):
    first_a = random_action(env.valid_moves)
    done, r = make_move(env, first_a, 0)
    if done:
        return first_a, r
    
    for step in range(1,MAX_DEPTH):
        a = random_action(env.valid_moves)
        done, r = make_move(env, a, step)
        if done:
            return first_a, r

    return first_a, r

def make_move(env, a, step):
    num_on_goal = env.num_on_goal

    env.move(a,False)
    on_off_goal = num_on_goal - env.num_on_goal
    if (on_off_goal == 0):
        push_on_goal = False
        push_off_goal = False
    elif (on_off_goal == 1):
        push_on_goal = True
        push_off_goal = False
    elif (on_off_goal == -1):
        push_on_goal = False
        push_off_goal = True
        
    done = env.is_completed()
    r = rlult.get_reward(env.box_cells, env.goal_cells, step, push_on_goal, push_off_goal, done)
    return done, r

def random_action(valid_actions):
    return np.random.choice(valid_actions)

def pick_best_action(agent):
    m = float('-inf')
    action = None
    for a in agent.keys():
        if agent[a]>=m:
            action = a
            m = agent[a]
    return action

