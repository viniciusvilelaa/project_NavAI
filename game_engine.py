import numpy as np

class BattleShipBoard:
    def __init__(self):
        #Inicializa tabuleiro com 10x10 preenchidop com 0(agua)
        self.grid = np.zeros((10,10), dtype=int)

        #Dicionario para estados dos navios
        self.ships = {}

        self._next_ship_id = 1

    def is_valid_placement(self, size, start_row, start_col, orientation):
        if not (0 <= start_row < 10 and 0 <= start_col < 10):
            return False
        
        if orientation == "H":
            end_col = start_col + size
            if end_col > 10:
                return False
