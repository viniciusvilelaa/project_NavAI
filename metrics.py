class Metrics: 
    def __init__(self):
        self.total_shots = 0
        self.total_hits = 0
        self.total_misses = 0;

        self.history = []
    

    def record_shot(self, result):
        self.total_shots += 1

        if result == "HIT" or result == "SUNK":
            self.total_hits += 1
        elif result == "MISS":
            self.total_misses += 1

    def end_game(self):
        #Salva os dados da partida atual no histórico
        if self.total_shots == 0:
            accuracy = 0.0
        else:
            accuracy = self.total_hits / self.total_shots

        partida = {
            "total_shots": self.total_shots,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "accuracy": round(accuracy, 3)
        }

        self.history.append(partida)

        # Reseta para a próxima partida
        self.total_shots = 0
        self.total_hits = 0
        self.total_misses = 0