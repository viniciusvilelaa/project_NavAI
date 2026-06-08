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

    #Posiciona navio dada a coordenada       
    def place_ship(self, size, start_row, start_col, orientation):
        
        #Verifica se o posicionamento é valido 
        is_valid, reason = self.is_valid_placement(size, start_row, start_col, orientation)
        
        if not is_valid:
            raise ValueError(reason)
        
        ship_id = self._next_ship_id
        coordinates = []

        #Preenche o grid com o navio e gera a lista das coordenadas
        if orientation == "H":
            end_col = start_col + size
            self.grid[start_row, start_col:end_col] = ship_id
            coordinates = [(start_row,col) for col in range(start_col, end_col)]
        
        elif orientation == "V":
            end_row = start_row + size
            self.grid[start_row:end_row, start_col] = ship_id
            coordinates = [(row, start_col) for row in range(start_row, end_row)]

        #Registra o navio no dicionario de navios
        self.ships[ship_id] = {
            "size": size,
            "hits": 0,
            "coordinates": coordinates
        }

        self._next_ship_id += 1

        return ship_id