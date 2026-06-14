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

        #Se a orientacao for vertical o navio se estende para a direita
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

    def shot_ship(self, row, col):
        
        #Verifica se a coordenada é valida
        if not (0 <= row < 10 and 0 <= col < 10):
            raise ValueError("Coordenada de disparo fora do tabuleiro")
        
        #Atribui o valor da casa, podendo ser -1(miss), -2(navio afundado), 0(agua) e positivos para os navios
        current_value = self.grid[row,col]

        #Verifica situacao do tiro
        if current_value == -1 or current_value == -2:
            return "REPEATED", None
        
        if current_value == 0:
            self.grid[row, col] = -1
            return "MISS", None
        
        #Se acertar um navio atualiza o contador de hits do mesmo
        ship_id = current_value
        self.grid[row, col] = -2
        self.ships[ship_id]["hits"] += 1

        #Se o navio afundou com o tiro retorna SUNK
        if self.ships[ship_id]["hits"] == self.ships[ship_id]["size"]:
            return "SUNK", ship_id
        
        return "HIT", ship_id

    #Verificacao de estado terminal, todos os navios foram afundados?
    def all_ships_sunk(self):

        if not self.ships:
            return False
        
        return all(ship["hits"] == ship["size"] for ship in self.ships.values())

    #Adiciona navios no tabuleiro de forma automatica
    def place_ships_randomly(self):
        ship_sizes = [5, 4, 3, 3, 2]

        for _ in range(100): # max 100 board restarts
            self.grid = np.zeros((10,10), dtype=int)
            self.ships = {}
            self._next_ship_id = 1
            
            success_all = True
            for size in ship_sizes:
                placed = False
                for _ in range(100): # max 100 retries per ship
                    row = np.random.randint(0,10)
                    col = np.random.randint(0, 10)
                    orientation = np.random.choice(['H','V'])

                    is_valid, _ = self.is_valid_placement(size, row, col, orientation)
                    if is_valid:
                        self.place_ship(size, row, col, orientation)
                        placed = True
                        break
                
                if not placed:
                    success_all = False
                    break
            
            if success_all:
                return
        
        raise RuntimeError("Não foi possível posicionar os navios aleatoriamente.")