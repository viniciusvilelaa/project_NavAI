from agent import NavalAgent
from interface import run_cli
from simulation import run_simulation

def main():
    print("=== NavAI: Batalha Naval ===")
    print("1. Jogar contra o Agente (Modo Clássico)")
    print("2. Iniciar Simulação (Agente vs Agente)")
    print("3. Sair")
    
    while True:
        escolha = input("Escolha uma opção [1-3]: ").strip()
        if escolha == '1':
            run_cli(agent=NavalAgent())
            break
        elif escolha == '2':
            run_simulation(agent1=NavalAgent(), agent2=NavalAgent())
            break
        elif escolha == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
