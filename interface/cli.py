from __future__ import annotations

from typing import Any, Iterable

from game_engine import BattleShipBoard
from metrics import Metrics
from interface.agent_adapter import AgentAdapter, RandomAgent
from interface.agent_adapter import to_agent_result
from interface.constants import DEFAULT_FLEET
from interface.contracts import BoardProtocol
from interface.controls import CoordinateSelector, DebugOutcome
from interface.models import PublicGameState, ShotResult
from interface.placement import place_fleet_randomly
from interface.rendering import ConsoleRenderer
from interface.results import display_result, normalize_result
from interface.views import build_public_view


class BattleshipCLI:
    def __init__(
        self,
        agent: Any | None = None,
        board_factory: type[BoardProtocol] = BattleShipBoard,
        fleet: Iterable[tuple[str, int]] = DEFAULT_FLEET,
        renderer: ConsoleRenderer | None = None,
    ) -> None:
        self.agent_adapter = AgentAdapter(agent or RandomAgent())
        self.board_factory = board_factory
        self.fleet = list(fleet)
        self.renderer = renderer or ConsoleRenderer()
        self.coordinate_selector = CoordinateSelector(self.renderer)
        self.human_board = self.board_factory()
        self.agent_board = self.board_factory()
        self.history: list[ShotResult] = []
        self.human_metrics = Metrics()
        self.agent_metrics = Metrics()
        self.last_selection = {"human": (0, 0), "agent": (0, 0)}
        self.last_placement_orientation = "H"
        self.turn = 1

    def run(self) -> str:
        self.renderer.print_title()
        try:
            self._setup_boards()
        except DebugOutcome as outcome:
            return self._finish_debug_outcome(outcome.winner)

        while True:
            self.renderer.render(self.human_board, self.agent_board, self.history)

            try:
                self._human_turn()
            except DebugOutcome as outcome:
                return self._finish_debug_outcome(outcome.winner)

            if self.agent_board.all_ships_sunk():
                self.renderer.show_outcome(
                    "WINNER",
                    f"Você venceu em {self.turn} turnos.",
                    self.human_board,
                    self.agent_board,
                    self.history,
                )
                return "human"

            self._agent_turn()
            if self.human_board.all_ships_sunk():
                self.renderer.show_outcome(
                    "LOSER",
                    f"O agente venceu em {self.turn} turnos.",
                    self.human_board,
                    self.agent_board,
                    self.history,
                )
                return "agent"

            self.turn += 1

    def _finish_debug_outcome(self, winner: str) -> str:
        if winner == "human":
            self.renderer.show_outcome(
                "WINNER",
                "Vitória forçada por debug.",
                self.human_board,
                self.agent_board,
                self.history,
            )
            return "human"

        self.renderer.show_outcome(
            "LOSER",
            "Derrota forçada por debug.",
            self.human_board,
            self.agent_board,
            self.history,
        )
        return "agent"

    def _setup_boards(self) -> None:
        if self._ask_yes_no("Posicionar sua frota automaticamente?", default=True):
            place_fleet_randomly(self.human_board, self.fleet)
        else:
            self._place_human_fleet()

        if not self.agent_adapter.place_fleet(self.agent_board, self.fleet):
            place_fleet_randomly(self.agent_board, self.fleet)

    def _place_human_fleet(self) -> None:
        for name, size in self.fleet:
            while True:
                row, col, orientation = self._select_ship_placement(
                    f"Posicione {name} tamanho {size}: setas movem, espaço rotaciona, Enter confirma",
                    size,
                )
                try:
                    self.human_board.place_ship(size, row, col, orientation)
                    self.last_selection["human"] = (row, col)
                    self.last_placement_orientation = orientation
                    break
                except ValueError as exc:
                    self.renderer.write(f"Posicionamento inválido: {exc}")

    def _human_turn(self) -> ShotResult:
        while True:
            row, col = self._select_coordinate("Seu tiro: use setas e Enter", "agent")
            try:
                result, ship_id = self.agent_board.shot_ship(row, col)
            except ValueError as exc:
                self.renderer.write(str(exc))
                continue

            shot = ShotResult("human", row, col, normalize_result(result), ship_id)
            if shot.result == "tiro repetido":
                self.renderer.write(f"{shot.coordinate} já foi atacada. Escolha outra coordenada.")
                continue

            self.history.append(shot)
            self.human_metrics.record_shot(to_agent_result(shot.result))
            self.renderer.flash_result(self.human_board, self.agent_board, self.history, "human")
            self.renderer.write(f"Você atirou em {shot.coordinate}: {display_result(shot.result)}.")
            return shot

    def _agent_turn(self) -> ShotResult:
        for _ in range(100):
            row, col = self.agent_adapter.choose_shot(self._build_agent_state())
            self.renderer.animate_agent_target(
                self.human_board,
                self.agent_board,
                self.history,
                start=self.last_selection.get("human", (0, 0)),
                target=(row, col),
            )
            self.last_selection["human"] = (row, col)
            try:
                result, ship_id = self.human_board.shot_ship(row, col)
            except ValueError:
                continue

            shot = ShotResult("agent", row, col, normalize_result(result), ship_id)
            self.agent_adapter.observe_result(shot, self._build_agent_state())
            if shot.result == "tiro repetido":
                continue

            self.history.append(shot)
            self.agent_metrics.record_shot(to_agent_result(shot.result))
            self.renderer.flash_result(self.human_board, self.agent_board, self.history, "agent")
            self.renderer.write(f"Agente atirou em {shot.coordinate}: {display_result(shot.result)}.")
            return shot

        raise RuntimeError("O agente não conseguiu gerar um tiro válido.")

    def _build_agent_state(self) -> PublicGameState:
        return PublicGameState(
            turn=self.turn,
            own_grid=self.agent_board.grid.copy(),
            enemy_view=build_public_view(self.human_board),
            history=list(self.history),
            remaining_ship_sizes=[size for _, size in self.fleet],
        )

    def _select_coordinate(self, label: str, target_board: str, show_enemy: bool = True) -> tuple[int, int]:
        coordinate = self.coordinate_selector.select(
            label,
            self.human_board,
            self.agent_board,
            self.history,
            target_board=target_board,
            initial=self.last_selection.get(target_board, (0, 0)),
            show_enemy=show_enemy,
        )
        self.last_selection[target_board] = coordinate
        return coordinate

    def _select_ship_placement(self, label: str, ship_size: int) -> tuple[int, int, str]:
        row, col, orientation = self.coordinate_selector.select_placement(
            label,
            self.human_board,
            self.agent_board,
            self.history,
            ship_size=ship_size,
            initial=self.last_selection.get("human", (0, 0)),
            initial_orientation=self.last_placement_orientation,
        )
        self.last_selection["human"] = (row, col)
        self.last_placement_orientation = orientation
        return row, col, orientation

    def _ask_yes_no(self, label: str, default: bool = True) -> bool:
        suffix = "[S/n]" if default else "[s/N]"
        while True:
            value = input(f"{label} {suffix}: ").strip().lower()
            if value == "win":
                raise DebugOutcome("human")
            if value == "loss":
                raise DebugOutcome("agent")
            if not value:
                return default
            if value in {"s", "sim", "y", "yes"}:
                return True
            if value in {"n", "nao", "não", "no"}:
                return False
            self.renderer.write("Entrada inválida. Responda s ou n.")


def run_cli(agent: Any | None = None) -> str:
    cli = BattleshipCLI(agent=agent)
    try:
        return cli.run()
    except KeyboardInterrupt:
        cli.renderer.write("Jogo interrompido subitamente.")
        return "interrupted"
