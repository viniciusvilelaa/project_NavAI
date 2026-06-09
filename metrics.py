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

    