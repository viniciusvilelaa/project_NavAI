import unittest
from simulation.simulation_cli import SimulationCLI
from agent import NavalAgent

class TestSimulation(unittest.TestCase):
    def test_simulation_headless_match(self):
        # Setup agents and simulation
        agent1 = NavalAgent()
        agent2 = NavalAgent()
        
        cli = SimulationCLI(agent1, agent2)
        
        # Run 10 matches headless
        cli.run(headless=True, rounds=10, auto_place=True, continuous=True)
        
        # Verify 10 matches were played
        self.assertEqual(len(cli.match_results), 10)
        
        # Verify metrics constraints
        for p in cli.agent1_metrics.history:
            self.assertTrue(0 <= p["total_shots"] <= 100)
            self.assertTrue(0.0 <= p["accuracy"] <= 1.0)
            
        for p in cli.agent2_metrics.history:
            self.assertTrue(0 <= p["total_shots"] <= 100)
            self.assertTrue(0.0 <= p["accuracy"] <= 1.0)

        # Verify win counts add up
        ag1_wins = cli.match_results.count("Agent 1")
        ag2_wins = cli.match_results.count("Agent 2")
        self.assertEqual(ag1_wins + ag2_wins, 10)

if __name__ == "__main__":
    unittest.main()
