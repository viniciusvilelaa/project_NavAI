import numpy as np
import random

class NavalAgent:
    def __init__(self , board_size=10):
        #Definindo o tamanho do tabuleiro
        self.board_size = board_size

        #Inicializando mapa de conhecimento
        self.knowledge_map = np.zeros((self.board_size,self.board_size), dtype=int)
        
        #Inicializando mapa de probabilidade
        self.belief_state = np.ones((self.board_size, self.board_size), dtype=float)

        #Alimentando o belief_state para o padrao xadrez. Aumenta a probabilidade para 2 casas intercaladas ja que o minimo de
        #casas utilizadas por um navio é 2
        for row in range(self.board_size):
            for col in range(self.board_size):
                if(row + col) % 2 == 0:
                    self.belief_state[row, col] = 2.0
        
        #Lista de tiros dados
        self.shots_fired = set()

        # Metricas de perfomace do agente
        self.total_shots = 0
        self.total_hits = 0
        self.total_misses = 0

        #Controle do modo do agente HUNT ou TARGET
        self._mode = "HUNT"
        self._target_queue = []
        self._active_hits = []


    #Retorna as estatísticas de desempenho do agente atual
    def get_metrics(self):
        if self.total_shots == 0:
            accuracy = 0.0
        else: 
            #Calcula a taxa de acerto (Hits / Total)
            accuracy = self.total_hits / self.total_shots

        return {
            "total_shots": self.total_shots,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "accuracy": round(accuracy, 3)
        }
    
    
    #Retorna as cordenadas dos vizinhos a um ponto
    def _get_neighbors(self, row, col): 
        candidates = [
            (row - 1, col), #Cima
            (row + 1, col), #Baixo
            (row, col - 1), #Esquerda
            (row, col + 1), #Direita 
        ]

        neighbors = [] 

        for r, c in candidates: 
            #Verifica se alguma coordenada não cai pra fora do tabuleiro
            if 0 <= r < self.board_size and 0 <= c < self.board_size:

                #Só adiciona se o agente já não tiver atirado 
                if (r, c) not in self.shots_fired:
                    neighbors.append((r, c))

        return neighbors
    

    #Processa o feedback do tabuleiro após cada tiro
    def update(self, row, col, result):
        
        # Registra o tiro
        self.shots_fired.add((row, col))
        self.total_shots += 1

        # Atualiza o knowledge_map
        if result == "MISS":
            self.total_misses += 1
            self.knowledge_map[row, col] = -1

        elif result == "HIT":
            self.total_hits += 1
            self.knowledge_map[row, col] = -2
            self._active_hits.append((row, col))

            #Acertou um navio/muda para TARGET
            self._mode = "TARGET"

            #Adiciona os vizinhos na fila de alvos
            for neighbor in self._get_neighbors(row, col):
                if neighbor not in self._target_queue:
                    self._target_queue.append(neighbor)

        elif result == "SUNK":
            self.total_hits += 1
            self.knowledge_map[row, col] = -2

            #Limpa o estado de caça
            self._active_hits.clear()
            self._target_queue.clear()

            #Retorna para HUNT 
            self._mode = "HUNT"

        #Zera a probabilidade da casa atirada
        self.belief_state[row, col] = 0.0

    def _target_mode_action(self):
        while self._target_queue:
            row, col = self._target_queue.pop(0)
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                if (row, col) not in self.shots_fired:
                    return (row, col)
        
        return None
    
    def _hunt_mode_action(self):
        temp_belief = np.copy(self.belief_state)
        for row, col in self.shots_fired:
            temp_belief[row, col] = 0.0
        
        max_val = np.max(temp_belief)
        rows, cols = np.where(temp_belief == max_val)
        candidates = list(zip(rows,cols))

        return random.choice(candidates)
        
   
    #Decide qual será a próxima coordenada de disparo
    def choose_action(self):

        #TARGET: tem vizinhos de um hit na fila
        if self._mode == "TARGET" and self._target_queue:
            return self._target_queue.pop(0)

        # Modo HUNT: escolhe a casa com maior probabilidade
        max_prob = -1
        best_action = None

        #Percorre todas as linhas e colunas do tabuleiro
        for row in range(self.board_size):
            for col in range(self.board_size):
                #Ignora as coordenadas onde o agente já atirou
                if (row, col) not in self.shots_fired:

                    #Compara o valor da célula atual com o maior valor salvo
                    if self.belief_state[row, col] > max_prob:
                        max_prob = self.belief_state[row, col]
                        best_action = (row, col)

        # Retorna a coordenada que tem maior chance de ter um navio
        return best_action