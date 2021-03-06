import numpy as np

def get_reward(boxes, tars, step_counter, push_on_tar, push_off_tar, done):
    '''
    boxes   : set of tuples, {(x1,y1),(x2,y2),...}
    tars : set of tuples, {(x1,y1),(x2,y2),...}
    step_counter: int, number of actions performed
    push_on_tar: bool, if the last step push a box on a target
    push_off_tar: bool, if the last step push a box off a target
    '''
    return (step_counter+1) * (-0.1) +  int(push_on_tar) * (10.0) + int(push_off_tar) * (-10.0) + int(done) * (100.0)
