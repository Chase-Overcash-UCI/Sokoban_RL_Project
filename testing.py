import unittest
from Sokoban import Sokoban
from util import Action, CellState

INPUT_PATH = "sample_inputs/sokoban01.txt"


class SokobanTest(unittest.TestCase):
    def setUp(self):
        self.game = Sokoban(INPUT_PATH, False)

    def test_movement_wall(self):
        for _ in range(50):
            self.game.move(Action.RIGHT)
            self.game.move(Action.DOWN)
        self.game.move(Action.UP)
        self.assertEqual(self.game.player_pos, (5, 6))

    def test_movement_general(self):
        for _ in range(50):
            self.game.move(Action.UP)
            self.game.move(Action.LEFT)
            self.game.move(Action.DOWN)
            self.game.move(Action.RIGHT)

        self.assertEqual(self.game.player_pos, (6, 6))

    def test_box_push(self):
        self.game.move(Action.LEFT)
        for _ in range(10):
            self.game.move(Action.UP)
        for _ in range(10):
            self.game.move(Action.LEFT)

        # Box push into walls
        self.assertEqual(self.game.cell_at((1, 5)), CellState.BOX)
        self.assertEqual(self.game.cell_at((2, 1)), CellState.BOX)
        self.assertIn((1, 5), self.game.box_cells)
        self.assertIn((2, 1), self.game.box_cells)
        self.assertEqual(self.game.cell_at((2, 2)), CellState.PLAYER)
        self.assertEqual(self.game.player_pos, (2, 2))

        # Box push into goal
        self.game.move(Action.DOWN)
        self.game.move(Action.LEFT)
        self.game.move(Action.UP)
        self.assertEqual(self.game.player_pos, (2, 1))
        self.assertIn((1, 1), self.game.box_cells)
        self.assertEqual(self.game.cell_at((1, 1)), CellState.BOX_ON_GOAL)

    def test_pos_set_assert(self):
        # Test failed case
        self.assertRaises(AssertionError, self.game.set_box_and_player_pos,
                          [box for box in self.game.goal_cells], (4, 1))
        for i in range(len(self.game.box_cells)):
            self.assertRaises(AssertionError, self.game.set_box_and_player_pos,
                              [box for box in self.game.goal_cells], self.game.goal_cells[i])

    def test_pos_set(self):
        # Test correct case
        new_player_pos = (4, 2)
        self.game.set_box_and_player_pos([box for box in self.game.goal_cells], new_player_pos)
        for box in self.game.box_cells:
            self.assertIn(box, self.game.goal_cells)
            self.assertEqual(self.game.cell_at(box), CellState.BOX_ON_GOAL)
        self.assertEqual(self.game.player_pos, new_player_pos)
        self.assertEqual(self.game.cell_at(new_player_pos), CellState.PLAYER)

    def test_pos_set_1(self):
        new_player_pos = (4, 6)
        new_box_list = [(1, 1), (6, 3), (1, 4)]
        self.game.set_box_and_player_pos(new_box_list, new_player_pos)
        for box in new_box_list:
            self.assertIn(box, self.game.box_cells)
        self.assertEqual(self.game.cell_at((1, 1)), CellState.BOX_ON_GOAL)
        self.assertEqual(self.game.cell_at((6, 3)), CellState.BOX_ON_GOAL)
        self.assertEqual(self.game.cell_at((1, 4)), CellState.BOX)
        self.assertEqual(self.game.player_pos, new_player_pos)
        self.assertEqual(self.game.cell_at(new_player_pos), CellState.PLAYER_ON_GOAL)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(SokobanTest("test_movement_wall"))
    suite.addTest(SokobanTest("test_movement_general"))
    suite.addTest(SokobanTest("test_box_push"))
    suite.addTest(SokobanTest("test_pos_set_assert"))
    suite.addTest(SokobanTest("test_pos_set"))
    suite.addTest(SokobanTest("test_pos_set_1"))

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
