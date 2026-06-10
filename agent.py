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
    
    #Metodo para enfileiramento de vizinhos
    def _enqueue_neighbors(self, row,col):
        hits_same_line = []
        hits_same_col = []
        candidates = []
        
        #Verificacao de acertos enfileirados
        for r, c in self._active_hits:
            #Retorna acertos que estao apenas na linha do alvo atual
            if r == row:
                hits_same_line.append((r,c))
            #Retorna acertos que estao apenas na coluna do alvo atual
            if c == col:
                hits_same_col.append((r,c))
        
        #Se tem dois acertos na mesma linha o navio esta na horizontal
        if len(hits_same_line) >= 2:
            candidates = [(row, col-1), (row, col+1)]
        
        #Se tem dois acertos na mesma coluna o navio esta na vertical
        elif len(hits_same_col) >= 2:
            candidates = [(row - 1, col), (row + 1, col)]
        else:
            candidates = [
                (row - 1, col), #Cima
                (row + 1, col), #Baixo
                (row, col - 1), #Esquerda
                (row, col + 1)
            ]
        
        #Para cada candidato verifica se esta no shots_fireds e no target_queue caso nao esteja é inserido
        for candidate_row, candidate_col in candidates:
            if 0 <= candidate_row < self.board_size and 0 <= candidate_col < self.board_size:
                if (candidate_row, candidate_col) not in self.shots_fired and (candidate_row, candidate_col) not in self._target_queue:
                    self._target_queue.append((candidate_row, candidate_col))
    
    #Funçao para atualizar o mapa de probabilidade
    def _update_belief_state(self):
        
        #Inicializa um novo mapa
        new_belief = np.zeros((self.board_size, self.board_size), dtype=float)
        
        #Para cada tamanho de barco busca os locais em que o barco caberia horizontalmente
        for size in [5, 4, 3, 3, 2]:
            for r in range(self.board_size):
                for c in range(self.board_size - size + 1):
                    segment = self.knowledge_map[r, c:c + size]
                    #Caso tenha alguma celula -1(miss) o segmento é invalido
                    if not np.any(segment == -1):
                        new_belief[r, c:c + size] += 1
        
        #Para cada tamanho de barco busca os locais em que o barco cabe verticalmente
        for size in [5, 4, 3, 3, 2]:
            for c in range(self.board_size):
                for r in range(self.board_size - size + 1):
                    segment = self.knowledge_map[r:r + size, c]
                    #Caso tenha alguma celula -1(miss) o segmento é invalido
                    if not np.any(segment == -1):
                        new_belief[r:r + size, c] += 1
        
        #Zera todas as probabilidades das casas que ja foram atiradas
        for (row, col) in self.shots_fired:
            new_belief[row,col] = 0
        
        if new_belief.max() > 0:
            new_belief /= new_belief.max()
            
        self.belief_state = new_belief
    
    #Metodo para computar tiro errado
    def _process_miss(self, row,col):
        self.knowledge_map[row,col] = -1
        self.belief_state[row, col] = 0
        self.total_misses += 1
        
    #Metodo para computar tiro acertado
    def _process_hit(self, row, col):
        self.knowledge_map[row,col] = -2
        self.belief_state[row, col] = 0
        self.total_hits += 1
        self._active_hits.append((row,col))

        
        self._mode = "TARGET"
        
        self._enqueue_neighbors(row, col)
    
    #Metodo para computar navio afundado
    def _process_hit_sunk(self, row, col):
        self.knowledge_map[row][col] = -2
        self.belief_state[row][col] = 0.0
        self.total_hits += 1
        
        self._active_hits.clear()
        self._target_queue.clear()
        
        self._mode = "HUNT"

    #Processa o feedback do tabuleiro após cada tiro
    def update(self, row, col, result):
        result = result.upper()
        
        # Registra o tiro
        self.shots_fired.add((row, col))
        self.total_shots += 1

        # Atualiza o knowledge_map
        if result == "MISS":
            self._process_miss(row,col)

        elif result == "HIT":
            self._process_hit(row, col)

        elif result == "SUNK":
            self._process_hit_sunk(row, col)
            
        self._update_belief_state()


    #Modo de target do agente
    def _target_mode_action(self):
        #Enquanto lista de target nao for nula percorre a lista e retorna as coordenadas do proximo alvo
        while self._target_queue:
            row, col = self._target_queue.pop(0)
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                if (row, col) not in self.shots_fired:
                    return (row, col)
        
        return None
    

    #Modo de caça do agente
    def _hunt_mode_action(self):
        #Cria uma copia do grid de probabilidades
        temp_belief = np.copy(self.belief_state)

        #Percorre as casas ja atiradas e atribui probabilidade 0
        for row, col in self.shots_fired:
            temp_belief[row, col] = 0.0

        #Fallback 
        if temp_belief.max() == 0:
            available = [
                (r, c)
                for r in range(self.board_size)
                for c in range(self.board_size)
                if (r, c) not in self.shots_fired
            ]
            return random.choice(available)
    
        #Maior valor de probabilidade presente no belief        
        max_val = np.max(temp_belief)

        #Salva em uma lista todos as casas que possuem valor maximo
        rows, cols = np.where(temp_belief == max_val)
        candidates = list(zip(rows,cols))

        return random.choice(candidates)
        
   
    #Decide qual será a próxima coordenada de disparo
    def choose_action(self):

        #TARGET: tem vizinhos de um hit na fila
        if self._mode == "TARGET":
            action = self._target_mode_action()
            if action is not None:
                return action
            
            self._mode = "HUNT"
        
        return self._hunt_mode_action()