import numpy as np


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

    def get_summary(self):
        
        if not self.history:
            return "Nenhuma partida registrada ainda."

        shots_list = [p["total_shots"] for p in self.history]
        accuracy_list = [p["accuracy"] for p in self.history]

        return {
            "partidas_jogadas": len(self.history),

            # Eficiência
            "media_tiros": round(np.mean(shots_list), 2),
            "menor_tiros": int(np.min(shots_list)),

            # Precisão
            "media_acerto": round(np.mean(accuracy_list), 3),
            "maior_acerto": round(np.max(accuracy_list), 3),

            # Consistência
            "desvio_padrao_tiros": round(np.std(shots_list), 2),
    }

    def format_summary(self) -> str:
        summary = self.get_summary()
        if isinstance(summary, str):
            return summary
        return (
            f"Tiros disparados : {summary['media_tiros']}\n"
            f"Taxa de acerto   : {summary['media_acerto'] * 100:.1f}%\n"
            f"Melhor partida   : {summary['menor_tiros']} tiros\n"
            f"Desvio padrão    : {summary['desvio_padrao_tiros']}"
    )