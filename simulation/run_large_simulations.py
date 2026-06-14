import time
from simulation.simulation_cli import SimulationCLI
from agent import NavalAgent
import sys

def main():
    rounds_to_run = [100, 1000, 10000]
    
    for r in rounds_to_run:
        print(f"\n==========================================")
        print(f"Executando {r} partidas...")
        print(f"==========================================")
        
        agent1 = NavalAgent()
        agent2 = NavalAgent()
        cli = SimulationCLI(agent1, agent2)
        
        start_time = time.time()
        
        # Override plot to not save/pop up graphs for this pure headless test
        # We just want to test stability and metrics consistency
        from simulation import metrics_plotter
        original_plot = metrics_plotter.plot_simulation_results
        metrics_plotter.plot_simulation_results = lambda a, b, c: None
        
        try:
            cli.run(headless=True, rounds=r, auto_place=True, continuous=True)
            elapsed = time.time() - start_time
            
            # Validation
            assert len(cli.match_results) == r, f"Esperado {r} resultados, obteve {len(cli.match_results)}"
            ag1_wins = cli.match_results.count("Agent 1")
            ag2_wins = cli.match_results.count("Agent 2")
            assert ag1_wins + ag2_wins == r, "A soma de vitórias não bate com o total de rodadas."
            
            print(f"Sucesso! {r} partidas rodaram sem crash em {elapsed:.2f} segundos.")
            print(f"Vitórias Agente 1: {ag1_wins} ({ag1_wins/r*100:.1f}%)")
            print(f"Vitórias Agente 2: {ag2_wins} ({ag2_wins/r*100:.1f}%)")
            
        except Exception as e:
            print(f"FALHA na execução de {r} partidas: {e}")
            sys.exit(1)
        finally:
            metrics_plotter.plot_simulation_results = original_plot

if __name__ == "__main__":
    main()
