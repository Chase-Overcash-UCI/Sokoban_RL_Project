import sys

from SokobanGame import SokobanGame, SokobanPygame, SokobanTerminal
from Sokoban import Sokoban
import time
import pygame
import random
from State import State
from util import Action
input_file = "sample_inputs/sokoban01.txt"

if __name__ == "__main__":
    # Play with terminal
    # sokoban_game = SokobanTerminal(input_file)
    # sokoban_game.play()

    # Pygame engine
    # sokoban_game = SokobanPygame(input_file)
    # sokoban_game.play()

    # Or if you want to apply MC/DFS/BFS/etc.:

    # DFS TESTING CODE:
    # sokoban_base = Sokoban(input_file)
    # root = State(sokoban_base,None,None)
    # root.DFS(root)
    # sys.exit("DFS")
    # END DFS TESTING CODE.

    # Using this will simulate the game on screen
    # q to quit, w to speed up, s to slow down (or comment out the sleep for unlimited speed)
    sokoban_game = SokobanPygame(input_file)
    base_sleep_time = 0.25
    sleep_factor = 1

    while True:
        # For pygame event trigger
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                elif event.key == pygame.K_w:
                    base_sleep_time /= 2
                elif event.key == pygame.K_s:
                    base_sleep_time *= 2

        # Next valid move way
        # next_valid_moves = sokoban_game.game.get_current_valid_moves()  # get next valid moves
        # next_chosen_move = random.choice(next_valid_moves)              # replace your next move algorithm here
        # sokoban_game.game.move(next_chosen_move)                        # move

        # Next pushable box way
        # Each pushable box contains a list of tuple (Action to push, path from player pos -> pos to push box)
        next_pushable_boxes = sokoban_game.game.get_pushable_box()

        if not next_pushable_boxes:
            print("Random actions couldn't find solution :(")
            break
        next_pushable_box = random.choice(list(next_pushable_boxes))

        action, path_to_action = random.choice(next_pushable_boxes[next_pushable_box])

        # teleport to that location
        sokoban_game.game.set_player_pos(path_to_action[-1])
        sokoban_game.render()
        time.sleep(0.125)
        sokoban_game.game.move(action)

        sokoban_game.render()
        time.sleep(base_sleep_time * sleep_factor)

        if sokoban_game.game.is_completed():
            print("Termination because boxes in corner?")
            time.sleep(10)

        # or move
        # action_sequences = sokoban_game.game.action_from_path(path_to_action)
        # action_sequences.append(action)
        # for action in action_sequences:
        #     sokoban_game.game.move(action)
        #
        #     # render
        #     sokoban_game.render()
        #     time.sleep(base_sleep_time * sleep_factor)
