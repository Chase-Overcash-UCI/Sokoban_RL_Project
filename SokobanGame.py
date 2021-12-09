import pygame
from Sokoban import Sokoban
from util import *
from abc import abstractmethod


class SokobanGame:
    def __init__(self, input_file, debug=True):
        self.game = Sokoban(input_file, debug=debug)
        self.input_file = input_file
        self.debug = debug

    def reset_game(self):
        self.game = Sokoban(self.input_file)

    # Core Sokoban playing loop
    def play(self):
        self.render()
        num_moves = 0
        move_selected = []
        completed, failed = False, False

        while not completed:
            if self.debug:
                print(f"Current player pos: {self.game.player_pos}")
                print("Next valid move:", [move.name for move in self.game.valid_moves])
                print("Pushable boxes: ", self.game.get_pushable_box())
                print("Boxes in corner: ", self.game.boxes_in_corner)
            action, reset, game_exit = self.get_input()
            if reset:
                print("Resetting...")
                self.reset_game()
                num_moves = 0
            elif game_exit:
                break
            else:
                self.game.move(action)
                move_selected.append(action.name)
            self.render()
            completed, failed = self.game.is_completed()

            if self.game.is_completed():
                print(f"Game is completed in {num_moves} moves!!!")
                print(f"Move selected: {move_selected}")
            else:
                num_moves += 1

    @abstractmethod
    def render(self):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_input():
        raise NotImplementedError()


class SokobanPygame(SokobanGame):
    def __init__(self, input_file, debug=True, grid_size=50):
        super().__init__(input_file, debug=debug)
        self.grid_size = grid_size
        self.__init_config()
        self.__init_pygame_engine()
        self.last_tick = pygame.time.get_ticks()

    def __init_config(self):
        self.COLOR_MAP = {
            CellState.EMPTY: (255, 255, 255),
            CellState.GOAL: (214, 232, 101),
            CellState.BOX: (139, 69, 19),
            CellState.BOX_ON_GOAL: (139, 69, 19),
            CellState.PLAYER: (0, 128, 128),
            CellState.PLAYER_ON_GOAL: (0, 128, 128),
            CellState.WALL: (87, 0, 0)
        }

        self.window_width = self.grid_size * self.game.n_col
        self.window_height = self.grid_size * self.game.n_row

    def __init_pygame_engine(self):
        pygame.init()
        self.screen = pygame.display.set_mode([self.window_width, self.window_height])
        pygame.display.set_caption("Sokoban")

    # Pygame coordinate ---x
    #                   |
    #                   y
    def __draw_board(self, goal_line_width=3):
        for r in range(self.game.n_row):
            for c in range(self.game.n_col):
                cell_state = self.game.board[r, c]
                on_goal = False
                if cell_state is CellState.PLAYER_ON_GOAL or cell_state is CellState.BOX_ON_GOAL:
                    on_goal = True
                x = c * self.grid_size
                y = r * self.grid_size

                pygame.draw.rect(self.screen, self.COLOR_MAP[cell_state], [x, y, self.grid_size, self.grid_size])
                if on_goal:
                    pygame.draw.rect(self.screen, self.COLOR_MAP[CellState.GOAL],
                                     [x, y, self.grid_size, self.grid_size], goal_line_width)
                    pygame.draw.line(self.screen, self.COLOR_MAP[CellState.GOAL],
                                     (x, y), (x + self.grid_size, y + self.grid_size), goal_line_width)
                    pygame.draw.line(self.screen, self.COLOR_MAP[CellState.GOAL],
                                     (x + self.grid_size, y), (x, y + self.grid_size), goal_line_width)

    # Drawing thin grid in between cells
    def __draw_grid(self, grid_width=1):
        # Horizontal line
        black = (0, 0, 0)
        for r in range(self.game.n_row):
            pygame.draw.line(self.screen, black, (0, r * self.grid_size),
                             (self.window_width, r * self.grid_size), grid_width)
        # Vertical line
        for c in range(self.game.n_col):
            pygame.draw.line(self.screen, black, (c * self.grid_size, 0),
                             (c * self.grid_size, self.window_height), grid_width)

    # get input from keyboard
    @staticmethod
    def get_input():
        action = None
        reset = False
        game_exit = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        action = Action.UP
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        action = Action.LEFT
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        action = Action.DOWN
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        action = Action.RIGHT
                    elif event.key == pygame.K_r:  # reset action
                        reset = True
                    elif event.key == pygame.K_q:
                        game_exit = True
                elif event.type == pygame.QUIT:
                    game_exit = True

                if action is not None or reset | game_exit is True:
                    return action, reset, game_exit

    # Render the game
    def render(self):
        self.__draw_board()
        self.__draw_grid()
        pygame.display.flip()


class SokobanTerminal(SokobanGame):
    def __init__(self, input_file):
        super().__init__(input_file)

    @staticmethod
    def get_input():
        input_map = {
            "w": Action.UP,
            "s": Action.DOWN,
            "a": Action.LEFT,
            "d": Action.RIGHT
        }
        while True:
            action = None
            reset = False
            game_exit = False
            user_input = input("Next move: ")

            if user_input in input_map:
                action = input_map[user_input]
            elif user_input == "r":
                reset = True
            elif user_input == "q":
                game_exit = True
            else:
                print("Not a valid input. Use wasd to move, r to reset, q to quit")
                continue

            if action is not None or reset | game_exit is True:
                return action, reset, game_exit

    def render(self):
        print_board(self.game.board)

