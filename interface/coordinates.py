from __future__ import annotations

import re
from typing import Any

from interface.constants import BOARD_SIZE


def parse_coordinate(value: str, board_size: int = BOARD_SIZE) -> tuple[int, int]:
    text = value.strip().upper()
    match = re.fullmatch(r"([A-Z])\s*(\d{1,2})", text)
    if match:
        col = ord(match.group(1)) - ord("A")
        row = int(match.group(2)) - 1
        return validate_coordinate(row, col, board_size)

    match = re.fullmatch(r"(\d{1,2})\s*[,; ]\s*(\d{1,2})", text)
    if match:
        row = int(match.group(1)) - 1
        col = int(match.group(2)) - 1
        return validate_coordinate(row, col, board_size)

    raise ValueError(
        f"Coordenada inválida. Use A1 até {format_coordinate(board_size - 1, board_size - 1)}, "
        "ou linha,coluna."
    )


def normalize_coordinate(value: Any, board_size: int | None = None) -> tuple[int, int]:
    if isinstance(value, str):
        return parse_coordinate(value, board_size or BOARD_SIZE)

    if isinstance(value, dict):
        row = value.get("row", value.get("linha", value.get("x")))
        col = value.get("col", value.get("column", value.get("coluna", value.get("y"))))
        if row is None or col is None:
            raise ValueError("Dicionário de tiro precisa ter row/col ou linha/coluna.")
        return validate_coordinate(int(row), int(col), board_size)

    if isinstance(value, (tuple, list)) and len(value) >= 2:
        return validate_coordinate(int(value[0]), int(value[1]), board_size)

    row = getattr(value, "row", getattr(value, "linha", None))
    col = getattr(value, "col", getattr(value, "column", getattr(value, "coluna", None)))
    if row is not None and col is not None:
        return validate_coordinate(int(row), int(col), board_size)

    raise ValueError("Tiro do agente deve ser string, tupla, lista, dict ou objeto com row/col.")


def validate_coordinate(row: int, col: int, board_size: int | None = None) -> tuple[int, int]:
    if board_size is not None and not (0 <= row < board_size and 0 <= col < board_size):
        raise ValueError(f"Coordenada fora do tabuleiro: ({row}, {col}).")
    return row, col


def format_coordinate(row: int, col: int) -> str:
    return f"{chr(ord('A') + col)}{row + 1}"
