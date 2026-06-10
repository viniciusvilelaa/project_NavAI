from __future__ import annotations

from interface.contracts import BoardProtocol


def build_public_view(board: BoardProtocol) -> list[list[str]]:
    view: list[list[str]] = []
    row_count, col_count = board.grid.shape
    for row in range(int(row_count)):
        line = []
        for col in range(int(col_count)):
            value = int(board.grid[row, col])
            if value == -1:
                line.append("agua")
            elif value == -2:
                line.append("acerto")
            else:
                line.append("desconhecido")
        view.append(line)
    return view
