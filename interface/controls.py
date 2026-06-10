from __future__ import annotations

import os
import sys
import time
from contextlib import contextmanager
from typing import Iterator

from interface.contracts import BoardProtocol
from interface.models import ShotResult
from interface.rendering import ConsoleRenderer

try:
    from rich.live import Live
except ImportError:
    Live = None


class CoordinateSelector:
    def __init__(self, renderer: ConsoleRenderer) -> None:
        self.renderer = renderer

    def select(
        self,
        label: str,
        human_board: BoardProtocol,
        agent_board: BoardProtocol,
        history: list[ShotResult],
        target_board: str,
        initial: tuple[int, int] = (0, 0),
        show_enemy: bool = True,
    ) -> tuple[int, int]:
        if not self.renderer.supports_live or Live is None:
            return self._prompt_coordinate_fallback(label, target_size(human_board, agent_board, target_board))

        row_count, col_count = target_shape(human_board, agent_board, target_board)
        row = min(max(0, initial[0]), row_count - 1)
        col = min(max(0, initial[1]), col_count - 1)
        blink_on = True
        last_blink = time.monotonic()
        debug_buffer = ""
        with Live(
            self.renderer.make_screen(
                human_board,
                agent_board,
                history,
                selection=(target_board, row, col),
                selection_active=blink_on,
                status=label,
                show_enemy=show_enemy,
            ),
            console=self.renderer.console,
            screen=True,
            refresh_per_second=20,
        ) as live:
            while True:
                key = read_key(timeout=0.08)
                now = time.monotonic()
                if now - last_blink >= 0.35:
                    blink_on = not blink_on
                    last_blink = now

                if key == "up":
                    row = max(0, row - 1)
                elif key == "down":
                    row = min(row_count - 1, row + 1)
                elif key == "left":
                    col = max(0, col - 1)
                elif key == "right":
                    col = min(col_count - 1, col + 1)
                elif key == "enter":
                    if debug_buffer == "win":
                        raise DebugOutcome("human")
                    if debug_buffer == "loss":
                        raise DebugOutcome("agent")
                    if debug_buffer:
                        debug_buffer = ""
                        continue
                    return row, col
                elif key in {"q", "esc"}:
                    raise KeyboardInterrupt("Selecao cancelada.")
                elif key and key.isalpha():
                    debug_buffer = update_debug_buffer(debug_buffer, key)

                live.update(
                    self.renderer.make_screen(
                        human_board,
                        agent_board,
                        history,
                        selection=(target_board, row, col),
                        selection_active=blink_on,
                        status=label,
                        show_enemy=show_enemy,
                    )
                )

    def select_placement(
        self,
        label: str,
        human_board: BoardProtocol,
        agent_board: BoardProtocol,
        history: list[ShotResult],
        ship_size: int,
        initial: tuple[int, int] = (0, 0),
        initial_orientation: str = "H",
    ) -> tuple[int, int, str]:
        if not self.renderer.supports_live or Live is None:
            row, col = self._prompt_coordinate_fallback(label, target_size(human_board, agent_board, "human"))
            orientation = input("Orientacao [H/V]: ").strip().lower()
            if orientation == "win":
                raise DebugOutcome("human")
            if orientation == "loss":
                raise DebugOutcome("agent")
            return row, col, orientation.upper()

        row_count, col_count = target_shape(human_board, agent_board, "human")
        row = min(max(0, initial[0]), row_count - 1)
        col = min(max(0, initial[1]), col_count - 1)
        orientation = initial_orientation if initial_orientation in {"H", "V"} else "H"
        blink_on = True
        last_blink = time.monotonic()
        debug_buffer = ""
        status = label

        with Live(
            self.renderer.make_screen(
                human_board,
                agent_board,
                history,
                selection=("human", row, col),
                selection_active=blink_on,
                placement_preview=build_placement_preview(human_board, row, col, ship_size, orientation),
                status=status,
                show_enemy=False,
            ),
            console=self.renderer.console,
            screen=True,
            refresh_per_second=20,
        ) as live:
            while True:
                key = read_key(timeout=0.08)
                now = time.monotonic()
                if now - last_blink >= 0.35:
                    blink_on = not blink_on
                    last_blink = now

                if key == "up":
                    row = max(0, row - 1)
                elif key == "down":
                    row = min(row_count - 1, row + 1)
                elif key == "left":
                    col = max(0, col - 1)
                elif key == "right":
                    col = min(col_count - 1, col + 1)
                elif key == " ":
                    orientation = "V" if orientation == "H" else "H"
                elif key == "enter":
                    if debug_buffer == "win":
                        raise DebugOutcome("human")
                    if debug_buffer == "loss":
                        raise DebugOutcome("agent")
                    is_valid, reason = human_board.is_valid_placement(ship_size, row, col, orientation)
                    if is_valid:
                        return row, col, orientation
                    status = f"{label} | Posicao invalida: {reason}"
                    debug_buffer = ""
                    live.update(
                        self.renderer.make_screen(
                            human_board,
                            agent_board,
                            history,
                            selection=("human", row, col),
                            selection_active=blink_on,
                            placement_preview=build_placement_preview(human_board, row, col, ship_size, orientation),
                            status=status,
                            show_enemy=False,
                        )
                    )
                    continue
                elif key in {"q", "esc"}:
                    raise KeyboardInterrupt("Selecao cancelada.")
                elif key and key.isalpha():
                    debug_buffer = update_debug_buffer(debug_buffer, key)

                status = label

                live.update(
                    self.renderer.make_screen(
                        human_board,
                        agent_board,
                        history,
                        selection=("human", row, col),
                        selection_active=blink_on,
                        placement_preview=build_placement_preview(human_board, row, col, ship_size, orientation),
                        status=status,
                        show_enemy=False,
                    )
                )

    def _prompt_coordinate_fallback(self, label: str, board_size: int) -> tuple[int, int]:
        from interface.coordinates import parse_coordinate

        while True:
            value = input(f"{label} (ex: A1, J10): ").strip()
            if value.lower() == "win":
                raise DebugOutcome("human")
            if value.lower() == "loss":
                raise DebugOutcome("agent")
            try:
                return parse_coordinate(value, board_size)
            except ValueError as exc:
                self.renderer.write(str(exc))


def target_shape(human_board: BoardProtocol, agent_board: BoardProtocol, target_board: str) -> tuple[int, int]:
    board = human_board if target_board == "human" else agent_board
    return int(board.grid.shape[0]), int(board.grid.shape[1])


def target_size(human_board: BoardProtocol, agent_board: BoardProtocol, target_board: str) -> int:
    rows, cols = target_shape(human_board, agent_board, target_board)
    return min(rows, cols)


def build_placement_preview(
    board: BoardProtocol,
    row: int,
    col: int,
    ship_size: int,
    orientation: str,
) -> tuple[str, int, int, int, str, bool]:
    is_valid, _ = board.is_valid_placement(ship_size, row, col, orientation)
    return "human", row, col, ship_size, orientation, is_valid


def update_debug_buffer(current: str, key: str) -> str:
    candidate = f"{current}{key.lower()}"
    if "win".startswith(candidate) or "loss".startswith(candidate):
        return candidate
    if "win".startswith(key.lower()) or "loss".startswith(key.lower()):
        return key.lower()
    return ""


class DebugOutcome(Exception):
    def __init__(self, winner: str) -> None:
        super().__init__(winner)
        self.winner = winner


def read_key(timeout: float | None = None) -> str:
    if os.name == "nt":
        return read_windows_key(timeout)
    return read_posix_key(timeout)


def read_windows_key(timeout: float | None = None) -> str:
    import msvcrt

    if timeout is not None:
        deadline = time.monotonic() + timeout
        while not msvcrt.kbhit():
            if time.monotonic() >= deadline:
                return ""
            time.sleep(0.01)

    char = msvcrt.getwch()
    if char in ("\x00", "\xe0"):
        code = msvcrt.getwch()
        return {
            "H": "up",
            "P": "down",
            "K": "left",
            "M": "right",
        }.get(code, "")
    if char == "\r":
        return "enter"
    if char == "\x1b":
        return "esc"
    return char.lower()


def read_posix_key(timeout: float | None = None) -> str:
    import select

    with raw_terminal():
        if timeout is not None:
            ready, _, _ = select.select([sys.stdin], [], [], timeout)
            if not ready:
                return ""

        char = sys.stdin.read(1)
        if char == "\n":
            return "enter"
        if char != "\x1b":
            return char.lower()

        sequence = sys.stdin.read(2)
        return {
            "[A": "up",
            "[B": "down",
            "[D": "left",
            "[C": "right",
        }.get(sequence, "esc")


@contextmanager
def raw_terminal() -> Iterator[None]:
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
