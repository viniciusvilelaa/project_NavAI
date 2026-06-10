from __future__ import annotations

from typing import Any, Protocol

from interface.models import PublicGameState, ShotResult


class BoardProtocol(Protocol):
    grid: Any
    ships: dict[int, dict[str, Any]]

    def is_valid_placement(self, size: int, start_row: int, start_col: int, orientation: str) -> tuple[bool, str]:
        ...

    def place_ship(self, size: int, start_row: int, start_col: int, orientation: str) -> int:
        ...

    def shot_ship(self, row: int, col: int) -> tuple[str, int | None]:
        ...

    def all_ships_sunk(self) -> bool:
        ...


class AgentProtocol(Protocol):
    def choose_shot(self, state: PublicGameState) -> tuple[int, int]:
        ...

    def observe_result(self, result: ShotResult, state: PublicGameState) -> None:
        ...
