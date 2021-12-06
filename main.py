import sys

from SokobanGame import SokobanGame, SokobanPygame, SokobanTerminal
from Sokoban import Sokoban
import time
import pygame
import random
from State import State
input_file = "sample_inputs/sokoban01.txt"

if __name__ == "__main__":
    # Play with terminal
    # sokoban_game = SokobanTerminal(input_file)
    # sokoban_game.play()

    # Pygame engine
    # sokoban_game = SokobanPygame(input_file)
    # sokoban_game.play()

    # Or if you want to apply MC/DFS/BFS/etc.:

    # BFS TESTING CODE:
    # sokoban_base = Sokoban(input_file)
    # root = State(sokoban_base,None,None)
    # root.BFS(root)
    # sys.exit("BFS")
    # END BFS TESTING CODE.

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

        # get next valid moves
        next_valid_moves = sokoban_game.game.get_current_valid_moves()

        # replace your next move algorithm here
        next_chosen_move = random.choice(next_valid_moves)

        # move
        sokoban_game.game.move(next_chosen_move)

        # render
        sokoban_game.render()
        time.sleep(base_sleep_time * sleep_factor)
