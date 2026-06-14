import unittest
from game_engine import BattleShipBoard

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.board = BattleShipBoard()

    def test_valid_placement_horizontal(self):
        is_valid, _ = self.board.is_valid_placement(3, 0, 0, "H")
        self.assertTrue(is_valid)

    def test_invalid_placement_horizontal_out_of_bounds(self):
        is_valid, _ = self.board.is_valid_placement(3, 0, 8, "H")
        self.assertFalse(is_valid)

    def test_valid_placement_vertical(self):
        is_valid, _ = self.board.is_valid_placement(4, 5, 5, "V")
        self.assertTrue(is_valid)

    def test_invalid_placement_vertical_out_of_bounds(self):
        is_valid, _ = self.board.is_valid_placement(4, 7, 5, "V")
        self.assertFalse(is_valid)

    def test_overlap_placement(self):
        self.board.place_ship(3, 0, 0, "H")
        is_valid, _ = self.board.is_valid_placement(3, 0, 1, "V")
        self.assertFalse(is_valid)

    def test_shot_miss(self):
        result, _ = self.board.shot_ship(0, 0)
        self.assertEqual(result, "MISS")

    def test_shot_hit_and_sunk(self):
        self.board.place_ship(2, 0, 0, "H")
        result1, _ = self.board.shot_ship(0, 0)
        self.assertEqual(result1, "HIT")
        result2, _ = self.board.shot_ship(0, 1)
        self.assertEqual(result2, "SUNK")

    def test_repeated_shot(self):
        self.board.shot_ship(0, 0)
        result, _ = self.board.shot_ship(0, 0)
        self.assertEqual(result, "REPEATED")

    def test_all_ships_sunk(self):
        self.assertFalse(self.board.all_ships_sunk())
        self.board.place_ship(2, 0, 0, "H")
        self.board.shot_ship(0, 0)
        self.board.shot_ship(0, 1)
        self.assertTrue(self.board.all_ships_sunk())

    def test_place_ships_randomly_terminates(self):
        self.board.place_ships_randomly()
        self.assertEqual(len(self.board.ships), 5)
        # Verify sizes are 5, 4, 3, 3, 2
        sizes = sorted([s["size"] for s in self.board.ships.values()])
        self.assertEqual(sizes, [2, 3, 3, 4, 5])

if __name__ == "__main__":
    unittest.main()
