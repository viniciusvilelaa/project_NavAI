# NavAI: Projeto de Agente de Inteligência Artificial para Batalha Naval

O **NavAI** é um projeto que implementa um jogo clássico de Batalha Naval, onde o jogador pode enfrentar um Agente Inteligente, ou então, iniciar um ambiente de Simulação em que dois agentes jogam um contra o outro. O sistema conta com tabuleiros de 10x10, diversos navios, métricas de desempenho e gráficos comparativos gerados ao final de cada série de simulações.

## Arquitetura do Projeto

O projeto é dividido em diferentes módulos focados em responsabilidades específicas:
- `game_engine.py`: Lógica principal do jogo, manipulação do tabuleiro (`BattleShipBoard`), posicionamento de frotas e validação de tiros (Hit, Miss, Sunk).
- `agent.py`: Implementação do Agente Inteligente (`NavalAgent`) baseada em modelos probabilísticos e estratégias de Caça (Hunt) e Alvo (Target).
- `metrics.py`: Classes para coletar e armazenar dados sobre o desempenho (tiros dados, acertos, taxa de acurácia) de cada partida.
- `interface/`: Módulo contendo a linha de comando clássica (CLI) para interação Humano vs Agente, renderização via console e captura de coordenadas.
- `simulation/`: Novo módulo focado no Modo Simulação. Inclui o executor de partidas autônomas `simulation_cli.py` e o gerador de gráficos `metrics_plotter.py` que usa `matplotlib` para exibir os resultados das rodadas (Taxa de Vitórias, Tiros por Rodada, Acurácia).
- `main.py`: Ponto de entrada do sistema que disponibiliza o menu interativo de seleção de modos de jogo.

---

## Modelo de Inteligência do Agente (Agent Model)

A inteligência do `NavalAgent` foi modelada em duas fases ou "Modos de Operação", utilizando uma matriz de probabilidade (*Belief State*) para guiar as decisões, maximizando a chance de acerto. 

### 1. Estado de Crença (Belief State) e Mapa de Conhecimento
O agente mapeia o tabuleiro 10x10 por meio de dois grids:
- **Knowledge Map:** Registra com certeza o estado das células (Água Desconhecida, Água Vazia (Miss), Navio Atingido).
- **Belief State:** Uma matriz de probabilidade que calcula a chance matemática de existir um navio em uma determinada célula. Para isso, o agente testa todas as posições horizontais e verticais possíveis onde os navios restantes (de tamanhos 5, 4, 3, 3, 2) podem caber, dado os tiros que já foram dados. Essa matriz é atualizada iterativamente após cada tiro para recalcular o local de maior chance. Adicionalmente, utiliza um padrão xadrez (*Checkerboard*) no início do jogo, intercalando as casas com peso maior, dado que o menor navio do jogo ocupa no mínimo 2 casas (reduz o tempo de busca cega).

### 2. Modo Caça (HUNT)
Este é o modo padrão de exploração do agente. 
- Durante o `HUNT`, o agente varre a matriz do *Belief State* e seleciona a coordenada que contém o **maior valor de probabilidade** entre todas as casas ainda não reveladas. Em caso de empate, escolhe uma destas coordenadas aleatoriamente.
- O objetivo do modo Hunt é "varrer" eficientemente o tabuleiro até encontrar a primeira parte de qualquer navio. 

### 3. Modo Alvo (TARGET)
Quando o agente acerta um tiro (resultado `HIT`), o estado muda imediatamente para `TARGET`.
- O algoritmo enfileira os vizinhos ortogonais da célula atingida (cima, baixo, esquerda, direita).
- Se existirem múltiplos acertos alinhados (ex: dois na mesma linha), a inteligência restringe as opções para tentar apenas as extremidades daquela mesma linha/coluna, assumindo com altíssima probabilidade a orientação do navio (horizontal ou vertical).
- O agente permanece neste modo, atirando nas coordenadas enfileiradas, até que o navio correspondente afunde (`SUNK`). Ao afundar, ele limpa a fila de vizinhos, zera as probabilidades para a área do navio destruído e retorna ao modo `HUNT`.

---

## Como Executar o Projeto

1. **Pré-requisitos**: Ter Python 3.x instalado.
2. **Instalar Dependências**: Crie um ambiente virtual (opcional) e execute:
   ```bash
   pip install -r requirements.txt
   ```
3. **Rodar o Jogo**:
   ```bash
   python main.py
   ```
4. **Modos Disponíveis no Menu**:
   - `[1] Jogar contra o Agente (Modo Clássico)`: Você monta sua frota (ou gera aleatoriamente) e joga pelo terminal.
   - `[2] Iniciar Simulação (Agente vs Agente)`: Configura um torneio entre dois agentes. Você pode estipular um número de rodadas, decidir posicionar a frota manualmente ou aleatoriamente, e escolher passar turno a turno pressionando "Enter" ou de forma contínua e rápida.
   - `[3] Sair`: Encerra o aplicativo.

### Análise de Simulações
Após concluir as partidas no Modo Simulação, o sistema salvará três gráficos (`win_rate.png`, `shots_per_round.png`, `accuracy_per_round.png`) dentro da pasta `/simulation_results/`, os quais poderão ser abertos e analisados para estudar a eficiência dos algoritmos sob as circunstâncias selecionadas.
