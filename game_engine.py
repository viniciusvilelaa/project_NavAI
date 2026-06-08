import numpy as np

class BattleShipBoard:
    def __init__(self):
        #Inicializa tabuleiro com 10x10 preenchidop com 0(agua)
        self.grid = np.zeros((10,10), dtype=int)

        #Dicionario para estados dos navios
        self.ships = {}

        self._next_ship_id = 1

    def is_valid_placement(self, size, start_row, start_col, orientation):

        #Verifica se coordenadas passadas estao dentro do tabuleiro
        if not (0 <= start_row < 10 and 0 <= start_col < 10):
            return False, "Coordenada inicial fora do tabuleiro."
        
        #Se a orientacao for horizontal o navio se estende para a direita
        if orientation == "H":
            end_col = start_col + size
            if end_col > 10:
                return False, "O navio ultrapassa o limite lateral do tabuleiro."
            
            #Obtendo area ocupada pelo navio
            ship_area = self.grid[start_row, start_col:end_col]
            if np.any(ship_area != 0):
                return False, "O navio se sobrepõe a outro navio existente."
        
        elif orientation == "V":
            end_row = start_row + size
            if end_row > 10:
                return False, "O navio ultrapassa o limite inferior do tabuleiro."
            
            ship_area = self.grid[start_row:end_row, start_col]
            if np.any(ship_area != 0):
                return False, "O navio se sobrepõe a outro navio existente."
            
        else:
            return False, "Orientação inválida. Use 'H' (horizontal) ou 'V' (vertical)."
        
        return True, "Posicionamento válido."
            
