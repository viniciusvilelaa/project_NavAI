import numpy as np

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
   
