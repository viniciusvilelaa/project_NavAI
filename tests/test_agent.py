import unittest
from agent import NavalAgent

class TestNavalAgent(unittest.TestCase):
    def setUp(self):
        self.agent = NavalAgent(board_size=10)

    def test_initial_state(self):
        self.assertEqual(self.agent.total_shots, 0)
        self.assertEqual(len(self.agent.shots_fired), 0)
        self.assertEqual(self.agent._mode, "HUNT")

    def test_choose_action_hunt(self):
        row, col = self.agent.choose_action()
        self.assertTrue(0 <= row < 10)
        self.assertTrue(0 <= col < 10)

    def test_process_miss(self):
        self.agent.update(0, 0, "MISS")
        self.assertIn((0, 0), self.agent.shots_fired)
        self.assertEqual(self.agent.belief_state[0, 0], 0)
        self.assertEqual(self.agent.total_misses, 1)

    def test_process_hit(self):
        self.agent.update(5, 5, "HIT")
        self.assertEqual(self.agent._mode, "TARGET")
        self.assertIn((5, 5), self.agent._active_hits)
        
        # Check target queue has neighbors
        neighbors = [(4, 5), (6, 5), (5, 4), (5, 6)]
        for n in self.agent._target_queue:
            self.assertIn(n, neighbors)

    def test_process_sunk(self):
        self.agent.update(5, 5, "HIT")
        self.agent.update(5, 6, "SUNK")
        self.assertEqual(self.agent._mode, "HUNT")
        self.assertEqual(len(self.agent._active_hits), 0)
        self.assertEqual(len(self.agent._target_queue), 0)

    def test_no_repeated_shots_in_hunt(self):
        # Fill all but one cell with misses
        for r in range(10):
            for c in range(10):
                if r == 9 and c == 9:
                    continue
                self.agent.update(r, c, "MISS")
        
        row, col = self.agent.choose_action()
        self.assertEqual((row, col), (9, 9))

    def test_failsafe_fallback(self):
        # Fill all cells
        for r in range(10):
            for c in range(10):
                self.agent.update(r, c, "MISS")
        
        row, col = self.agent.choose_action()
        self.assertEqual((row, col), (0, 0)) # Failsafe coordinate

if __name__ == "__main__":
    unittest.main()
