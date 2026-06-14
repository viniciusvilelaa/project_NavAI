from __future__ import annotations

import time
from typing import Any, Iterable

from game_engine import BattleShipBoard
from metrics import Metrics
from interface.agent_adapter import AgentAdapter, RandomAgent, to_agent_result
from interface.constants import DEFAULT_FLEET
from interface.contracts import BoardProtocol
from interface.controls import CoordinateSelector
from interface.models import PublicGameState, ShotResult
from interface.placement import place_fleet_randomly
from interface.rendering import ConsoleRenderer
from interface.results import display_result, normalize_result
from interface.views import build_public_view
from simulation.metrics_plotter import plot_simulation_results


class SimulationCLI:
    def __init__(
        self,
        agent1: Any,
        agent2: Any,
        board_factory: type[BoardProtocol] = BattleShipBoard,
        fleet: Iterable[tuple[str, int]] = DEFAULT_FLEET,
        renderer: ConsoleRenderer | None = None,
    ) -> None:
        self.agent1_adapter = AgentAdapter(agent1)
        self.agent2_adapter = AgentAdapter(agent2)
        self.board_factory = board_factory
        self.fleet = list(fleet)
        self.renderer = renderer or ConsoleRenderer()
        self.coordinate_selector = CoordinateSelector(self.renderer)

        self.agent1_metrics = Metrics()
        self.agent2_metrics = Metrics()
        self.match_results: list[str] = []
        
        self.last_selection = {"agent1": (0, 0), "agent2": (0, 0)}
        self.last_placement_orientation = "H"

    def run(self, headless: bool = False, rounds: int = 1, auto_place: bool = True, continuous: bool = True, turbo: bool = False) -> None:
        if not headless:
            self.renderer.print_title()
            self.renderer.write("=== MODO SIMULAÇÃO (AGENTE VS AGENTE) ===\n")
            rounds = self._ask_integer("Quantas rodadas deseja simular?", default=1)
            auto_place = self._ask_yes_no("Gerar tabuleiros aleatoriamente?", default=True)
            continuous = self._ask_yes_no("Executar as rodadas automaticamente sem pausa?", default=False)
            if continuous:
                turbo = self._ask_yes_no("Habilitar Modo Turbo (Sem atrasos visuais)?", default=True)
        
        for i in range(1, rounds + 1):
            if not headless:
                self.renderer.write(f"\n--- Iniciando Rodada {i} de {rounds} ---\n")
            
            winner = self._run_match(auto_place, continuous, headless, turbo)
            self.match_results.append(winner)
            
            if not continuous and not headless and i < rounds:
                input(f"Rodada {i} finalizada. Pressione Enter para continuar para a próxima rodada...")

        if not headless:
            self.renderer.write("\n=== SIMULAÇÃO CONCLUÍDA ===\n")
            self._show_final_summary()
            plot_simulation_results(self.agent1_metrics, self.agent2_metrics, self.match_results)

    def _run_match(self, auto_place: bool, continuous: bool, headless: bool = False, turbo: bool = False) -> str:
        self.board1 = self.board_factory()
        self.board2 = self.board_factory()
        self.history: list[ShotResult] = []
        self.turn = 1

        self.agent1_adapter.reset()
        self.agent2_adapter.reset()

        self._setup_boards(auto_place)

        if not headless:
            self.renderer.write("\n=== POSIÇÃO INICIAL DOS TABULEIROS ===\n")
            self.renderer.render(self.board1, self.board2, self.history)
            if continuous and not turbo:
                time.sleep(1.0) # Pausa dramática breve para ver o inicial

        while True:
            if not continuous and not headless:
                self.renderer.render(self.board1, self.board2, self.history)
                time.sleep(0.1)

            # Turno Agente 1
            try:
                self._agent_turn(self.agent1_adapter, self.board2, self.board1, "agent1", "agent2", self.agent1_metrics, continuous, headless)
            except RuntimeError:
                self.agent1_metrics.end_game()
                self.agent2_metrics.end_game()
                return "Agent 2" # Agente 1 travou, Agente 2 vence
                
            if self.board2.all_ships_sunk():
                self.agent1_metrics.end_game()
                self.agent2_metrics.end_game()
                if not headless:
                    self.renderer.write(f"\n=== POSIÇÃO FINAL (Agente 1 venceu em {self.turn} turnos) ===\n")
                    self.renderer.render(self.board1, self.board2, self.history)
                    if continuous and not turbo:
                        time.sleep(1.5)
                return "Agent 1"

            # Turno Agente 2
            try:
                self._agent_turn(self.agent2_adapter, self.board1, self.board2, "agent2", "agent1", self.agent2_metrics, continuous, headless)
            except RuntimeError:
                self.agent1_metrics.end_game()
                self.agent2_metrics.end_game()
                return "Agent 1" # Agente 2 travou, Agente 1 vence
                
            if self.board1.all_ships_sunk():
                self.agent1_metrics.end_game()
                self.agent2_metrics.end_game()
                if not headless:
                    self.renderer.write(f"\n=== POSIÇÃO FINAL (Agente 2 venceu em {self.turn} turnos) ===\n")
                    self.renderer.render(self.board1, self.board2, self.history)
                    if continuous and not turbo:
                        time.sleep(1.5)
                return "Agent 2"

            self.turn += 1

    def _setup_boards(self, auto_place: bool) -> None:
        if auto_place:
            if not self.agent1_adapter.place_fleet(self.board1, self.fleet):
                place_fleet_randomly(self.board1, self.fleet)
            if not self.agent2_adapter.place_fleet(self.board2, self.fleet):
                place_fleet_randomly(self.board2, self.fleet)
        else:
            self.renderer.write("\nPosicione a frota para o Agente 1:\n")
            self._place_human_fleet(self.board1)
            self.renderer.write("\nPosicione a frota para o Agente 2:\n")
            self._place_human_fleet(self.board2)

    def _place_human_fleet(self, board: BattleShipBoard) -> None:
        for name, size in self.fleet:
            while True:
                row, col, orientation = self.coordinate_selector.select_placement(
                    f"Posicione {name} tamanho {size}: setas movem, espaço rotaciona, Enter confirma",
                    board,
                    self.board_factory(), # Dummy board for enemy
                    [],
                    ship_size=size,
                    initial=self.last_selection.get("agent1", (0, 0)),
                    initial_orientation=self.last_placement_orientation,
                )
                try:
                    board.place_ship(size, row, col, orientation)
                    self.last_selection["agent1"] = (row, col)
                    self.last_placement_orientation = orientation
                    break
                except ValueError as exc:
                    self.renderer.write(f"Posicionamento inválido: {exc}")

    def _agent_turn(
        self,
        agent: AgentAdapter,
        target_board: BattleShipBoard,
        own_board: BattleShipBoard,
        shooter_name: str,
        target_name: str,
        metrics: Metrics,
        continuous: bool,
        headless: bool = False
    ) -> ShotResult:
        for _ in range(100):
            state = PublicGameState(
                turn=self.turn,
                own_grid=own_board.grid.copy(),
                enemy_view=build_public_view(target_board),
                history=[h for h in self.history if h.attacker == shooter_name or h.attacker == target_name],
                remaining_ship_sizes=[size for _, size in self.fleet],
            )
            row, col = agent.choose_shot(state)
            
            if not continuous and not headless:
                self.renderer.animate_agent_target(
                    own_board,
                    target_board,
                    self.history,
                    start=self.last_selection.get(shooter_name, (0, 0)),
                    target=(row, col),
                )
            
            self.last_selection[shooter_name] = (row, col)
            
            try:
                result, ship_id = target_board.shot_ship(row, col)
            except ValueError:
                continue

            shot = ShotResult(shooter_name, row, col, normalize_result(result), ship_id)
            agent.observe_result(shot, state)
            
            if shot.result == "tiro repetido":
                continue

            self.history.append(shot)
            metrics.record_shot(to_agent_result(shot.result))
            
            if not continuous and not headless:
                self.renderer.flash_result(own_board, target_board, self.history, shooter_name)
                self.renderer.write(f"{shooter_name.capitalize()} atirou em {shot.coordinate}: {display_result(shot.result)}.")
            
            return shot

        raise RuntimeError(f"{shooter_name.capitalize()} não conseguiu gerar um tiro válido.")

    def _ask_integer(self, label: str, default: int = 1) -> int:
        while True:
            value = input(f"{label} [{default}]: ").strip()
            if not value:
                return default
            try:
                return int(value)
            except ValueError:
                self.renderer.write("Por favor, digite um número inteiro válido.")

    def _ask_yes_no(self, label: str, default: bool = True) -> bool:
        suffix = "[S/n]" if default else "[s/N]"
        while True:
            value = input(f"{label} {suffix}: ").strip().lower()
            if not value:
                return default
            if value in {"s", "sim", "y", "yes"}:
                return True
            if value in {"n", "nao", "não", "no"}:
                return False
            self.renderer.write("Entrada inválida. Responda s ou n.")

    def _show_final_summary(self) -> None:
        ag1_wins = self.match_results.count("Agent 1")
        ag2_wins = self.match_results.count("Agent 2")
        
        self.renderer.write("\n=== RESULTADO FINAL ===")
        self.renderer.write(f"Partidas jogadas: {len(self.match_results)}")
        self.renderer.write(f"Vitórias Agente 1: {ag1_wins}")
        self.renderer.write(f"Vitórias Agente 2: {ag2_wins}\n")
        
        self.renderer.write("Métricas do Agente 1:")
        self.renderer.write(self.agent1_metrics.format_summary())
        self.renderer.write("\nMétricas do Agente 2:")
        self.renderer.write(self.agent2_metrics.format_summary())


def run_simulation(agent1: Any, agent2: Any) -> None:
    cli = SimulationCLI(agent1=agent1, agent2=agent2)
    try:
        cli.run()
    except KeyboardInterrupt:
        cli.renderer.write("\nSimulação interrompida subitamente.")
