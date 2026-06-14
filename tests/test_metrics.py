import unittest
from metrics import Metrics

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.metrics = Metrics()

    def test_record_shot(self):
        self.metrics.record_shot("MISS")
        self.assertEqual(self.metrics.total_shots, 1)
        self.assertEqual(self.metrics.total_misses, 1)

        self.metrics.record_shot("HIT")
        self.assertEqual(self.metrics.total_hits, 1)

        self.metrics.record_shot("SUNK")
        self.assertEqual(self.metrics.total_hits, 2)

    def test_end_game_validation(self):
        # Mínimo de 17 tiros para afundar todos os navios (5+4+3+3+2) 
        # para vencer, mas no teste isolado de métricas não checamos a regra de negócio do jogo,
        # e sim as constraints das métricas.
        for _ in range(17):
            self.metrics.record_shot("HIT")
        self.metrics.end_game()
        
        self.assertEqual(len(self.metrics.history), 1)
        self.assertEqual(self.metrics.history[0]["accuracy"], 1.0)

    def test_accuracy_over_one(self):
        self.metrics.total_hits = 50
        self.metrics.total_shots = 20
        with self.assertRaises(ValueError):
            self.metrics.end_game()

    def test_shots_over_100(self):
        self.metrics.total_shots = 101
        with self.assertRaises(ValueError):
            self.metrics.end_game()

if __name__ == "__main__":
    unittest.main()
