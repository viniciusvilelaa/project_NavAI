import os
import matplotlib.pyplot as plt
from metrics import Metrics

def plot_simulation_results(agent1_metrics: Metrics, agent2_metrics: Metrics, match_results: list[str]) -> None:
    if not match_results:
        print("Nenhuma partida para plotar.")
        return

    # Criar pasta para salvar os gráficos se não existir
    output_dir = "simulation_results"
    os.makedirs(output_dir, exist_ok=True)

    rounds = len(match_results)
    ag1_wins = match_results.count("Agent 1")
    ag2_wins = match_results.count("Agent 2")

    # 1. Gráfico de Taxa de Vitórias (Win Rate)
    labels = ['Agente 1', 'Agente 2']
    sizes = [ag1_wins, ag2_wins]
    colors = ['#ff9999', '#66b3ff']
    
    plt.figure(figsize=(6, 6))
    if ag1_wins == 0 and ag2_wins == 0:
        plt.text(0.5, 0.5, "Sem vitórias", ha='center')
    else:
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Taxa de Vitórias (Win Rate)')
    plt.savefig(os.path.join(output_dir, 'win_rate.png'))
    plt.close()

    # Extrair dados históricos
    ag1_shots = [p["total_shots"] for p in agent1_metrics.history]
    ag2_shots = [p["total_shots"] for p in agent2_metrics.history]
    
    ag1_acc = [p["accuracy"] * 100 for p in agent1_metrics.history]
    ag2_acc = [p["accuracy"] * 100 for p in agent2_metrics.history]
    
    x = list(range(1, rounds + 1))

    # 2. Gráfico de Tiros por Rodada
    plt.figure(figsize=(10, 5))
    plt.plot(x, ag1_shots, marker='o', label='Agente 1')
    plt.plot(x, ag2_shots, marker='s', label='Agente 2')
    plt.title('Tiros disparados por Rodada')
    plt.xlabel('Rodada')
    plt.ylabel('Quantidade de Tiros')
    plt.xticks(x)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(output_dir, 'shots_per_round.png'))
    plt.close()

    # 3. Gráfico de Precisão (Accuracy)
    plt.figure(figsize=(10, 5))
    plt.plot(x, ag1_acc, marker='o', label='Agente 1')
    plt.plot(x, ag2_acc, marker='s', label='Agente 2')
    plt.title('Precisão (Acurácia) por Rodada (%)')
    plt.xlabel('Rodada')
    plt.ylabel('Acertos (%)')
    plt.xticks(x)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(output_dir, 'accuracy_per_round.png'))
    plt.close()

    print(f"\nGráficos de métricas gerados com sucesso na pasta '{output_dir}'.")
