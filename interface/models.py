from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from interface.coordinates import format_coordinate


@dataclass(frozen=True)
class ShotResult:
    attacker: str
    row: int
    col: int
    result: str
    ship_id: int | None = None

    @property
    def coordinate(self) -> str:
        return format_coordinate(self.row, self.col)


@dataclass
class PublicGameState:
    """Snapshot passed to agents without revealing hidden enemy ships."""

    turn: int
    own_grid: Any
    enemy_view: list[list[str]]
    history: list[ShotResult] = field(default_factory=list)
    remaining_ship_sizes: list[int] = field(default_factory=list)
