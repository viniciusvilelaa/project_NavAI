from __future__ import annotations

import random
from typing import Iterable

from interface.contracts import BoardProtocol


def place_fleet_randomly(board: BoardProtocol, fleet: Iterable[tuple[str, int]]) -> None:
    row_count, col_count = board.grid.shape
    for _, size in fleet:
        for _ in range(1000):
            row = random.randrange(int(row_count))
            col = random.randrange(int(col_count))
            orientation = random.choice(("H", "V"))
            try:
                board.place_ship(size, row, col, orientation)
                break
            except ValueError:
                continue
        else:
            raise RuntimeError("Nao foi possivel posicionar a frota automaticamente.")
