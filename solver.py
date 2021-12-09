from SokobanGame import SokobanPygame
from Sokoban import Sokoban
from util import print_board
from collections import deque
import pygame
import time


def input_wait():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                time.sleep(5)
            elif event.key == pygame.K_q:
                exit(0)
        elif event.type == pygame.QUIT:
            exit(0)


def solve(game: Sokoban):
    queue = []
    visited_states = set()
    first_state = (*sorted(game.box_cells), game.player_pos)
    queue.append(first_state)
    search_step = 0
    while queue:
        current_state = queue.pop()
        boxes = current_state[:-1]
        player_pos = current_state[-1]
        game.set_box_and_player_pos(boxes, player_pos)

        pushable_boxes = game.get_pushable_box()
        current_box_state = list(game.box_cells)
        for box in pushable_boxes:
            for action, path in pushable_boxes[box]:
                input_wait()
                game.set_box_and_player_pos(current_box_state, path[-1])
                game.move(action)
                sokoban_game.render()
                # time.sleep(0.01)

                # condition check
                completed, failed = game.is_completed()
                if completed and not failed:
                    print("Found")
                    return
                elif completed and failed:
                    print("Boxes in corner")
                    continue

                next_state = (*sorted(game.box_cells), game.player_pos)
                if next_state not in visited_states:
                    queue.append(next_state)
                visited_states.add(next_state)

                search_step += 1
                print(search_step)


# input_file = "sample_inputs/sokoban01.txt"
input_file = "sample_inputs/benchmarks/sokoban-01.txt"
sokoban_game = SokobanPygame(input_file, False)
sleep_factor = 1

solve(sokoban_game.game)
