from __future__ import annotations

import inspect
import random
from typing import Any

from interface.coordinates import normalize_coordinate
from interface.models import PublicGameState, ShotResult


SHOT_METHODS = ("choose_shot", "get_shot", "next_shot", "select_target", "act", "play")
OBSERVE_METHODS = ("observe_result", "register_result", "update", "feedback", "observe")
PLACEMENT_METHODS = ("place_fleet", "place_ships", "setup_board")


class RandomAgent:
    """Fallback agent used while the real agent.py is still empty."""

    def __init__(self, board_size: int | None = None) -> None:
        self.board_size = board_size
        self.available: list[tuple[int, int]] = []
        if board_size is not None:
            self._reset_available(board_size)

    def choose_shot(self, state: PublicGameState | None = None) -> tuple[int, int]:
        if not self.available and state is not None:
            self._reset_available(len(state.enemy_view))
        if not self.available:
            raise RuntimeError("Nao ha tiros disponiveis.")
        return self.available.pop(random.randrange(len(self.available)))

    def observe_result(self, result: ShotResult, state: PublicGameState | None = None) -> None:
        return None

    def _reset_available(self, board_size: int) -> None:
        self.available = [(row, col) for row in range(board_size) for col in range(board_size)]


class AgentAdapter:
    """Keeps the CLI independent from the concrete agent implementation."""

    def __init__(self, agent: Any) -> None:
        self.agent = agent

    def choose_shot(self, state: PublicGameState) -> tuple[int, int]:
        for method_name in SHOT_METHODS:
            method = getattr(self.agent, method_name, None)
            if callable(method):
                return normalize_coordinate(
                    call_with_supported_args(method, state=state),
                    board_size=len(state.enemy_view),
                )

        raise AttributeError(
            "Agente precisa implementar choose_shot(state), get_shot(state), "
            "next_shot(state), select_target(state), act(state) ou play(state)."
        )

    def observe_result(self, result: ShotResult, state: PublicGameState) -> None:
        for method_name in OBSERVE_METHODS:
            method = getattr(self.agent, method_name, None)
            if callable(method):
                call_with_supported_args(method, result=result, state=state)
                return

    def place_fleet(self, board: Any, fleet: list[tuple[str, int]]) -> bool:
        for method_name in PLACEMENT_METHODS:
            method = getattr(self.agent, method_name, None)
            if callable(method):
                call_with_supported_args(method, board=board, fleet=fleet)
                return bool(getattr(board, "ships", None))
        return False


def call_with_supported_args(method: Any, **kwargs: Any) -> Any:
    signature = inspect.signature(method)
    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        return method(**kwargs)

    accepted = {
        name: value
        for name, value in kwargs.items()
        if name in signature.parameters
    }
    if accepted:
        return method(**accepted)

    if "state" in kwargs and len(signature.parameters) == 1:
        return method(kwargs["state"])

    return method()
