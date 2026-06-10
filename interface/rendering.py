from __future__ import annotations

import time
from typing import Any

from interface.constants import CELL_WIDTH
from interface.contracts import BoardProtocol
from interface.models import ShotResult
from interface.results import display_result

try:
    from rich import box
    from rich.align import Align
    from rich.columns import Columns
    from rich.console import Console
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.console import Group
    from rich.table import Table
except ImportError:
    Align = None
    box = None
    Columns = None
    Console = None
    Group = None
    Live = None
    Panel = None
    Table = None
    Text = None


class ConsoleRenderer:
    def __init__(self, use_rich: bool = True) -> None:
        self.console = Console() if use_rich and Console else None

    @property
    def supports_live(self) -> bool:
        return self.console is not None

    def print_title(self) -> None:
        if self.console and Panel:
            self.console.print(Panel("Batalha Naval contra Agente", title="NavAI"))
        else:
            print("NavAI - Batalha Naval contra Agente")

    def render(
        self,
        human_board: BoardProtocol,
        agent_board: BoardProtocol,
        history: list[ShotResult],
        show_enemy: bool = True,
    ) -> None:
        if self.console:
            self.console.clear()
            self.console.print(self.make_screen(human_board, agent_board, history, show_enemy=show_enemy))
            return

        print("\n" * 2)
        print(format_board_plain("Sua frota", human_board, reveal_ships=True))
        if show_enemy:
            print(format_board_plain("Águas inimigas", agent_board, reveal_ships=False))
        self._render_history_plain(history)

    def write(self, message: str) -> None:
        if self.console:
            self.console.print(message)
        else:
            print(message)

    def make_screen(
        self,
        human_board: BoardProtocol,
        agent_board: BoardProtocol,
        history: list[ShotResult],
        selection: tuple[str, int, int] | None = None,
        selection_active: bool = True,
        placement_preview: tuple[str, int, int, int, str, bool] | None = None,
        status: str | None = None,
        show_enemy: bool = True,
        flash_attacker: str | None = None,
        flash_active: bool = False,
    ) -> Any:
        if not self.console:
            return format_board_plain("Sua frota", human_board, reveal_ships=True)

        board_rows = max(board_shape(human_board)[0], board_shape(agent_board)[0])
        panels = [
            make_board_table(
                "Sua frota",
                human_board,
                reveal_ships=True,
                selection=selection if selection and selection[0] == "human" else None,
                selection_active=selection_active,
                placement_preview=placement_preview if placement_preview and placement_preview[0] == "human" else None,
            )
        ]
        if show_enemy:
            panels.append(
                make_board_table(
                    "Águas inimigas",
                    agent_board,
                    reveal_ships=False,
                    selection=selection if selection and selection[0] == "agent" else None,
                    selection_active=selection_active,
                    placement_preview=placement_preview if placement_preview and placement_preview[0] == "agent" else None,
                )
            )
        panels.append(make_side_panel(history, board_rows, flash_attacker=flash_attacker, flash_active=flash_active))

        body = Columns(panels, equal=False, expand=True) if Columns else panels
        if Panel and Group:
            return Group(Panel(status or "Aguardando ação.", title="Controle"), body)
        return body

    def animate_agent_target(
        self,
        human_board: BoardProtocol,
        agent_board: BoardProtocol,
        history: list[ShotResult],
        start: tuple[int, int],
        target: tuple[int, int],
    ) -> None:
        if not self.console or Live is None:
            time.sleep(1)
            return

        path = cursor_path(start, target)
        delay = min(0.045, max(0.012, 0.35 / max(len(path), 1)))
        with Live(
            self.make_screen(
                human_board,
                agent_board,
                history,
                selection=("human", path[0][0], path[0][1]),
                selection_active=True,
                status="Agente mirando...",
            ),
            console=self.console,
            screen=True,
            transient=True,
            refresh_per_second=20,
        ) as live:
            for row, col in path:
                live.update(
                    self.make_screen(
                        human_board,
                        agent_board,
                        history,
                        selection=("human", row, col),
                        selection_active=True,
                        status="Agente mirando...",
                    )
                )
                time.sleep(delay)
            time.sleep(0.08)

    def flash_result(
        self,
        human_board: BoardProtocol,
        agent_board: BoardProtocol,
        history: list[ShotResult],
        attacker: str,
    ) -> None:
        if not self.console or Live is None:
            return

        with Live(
            self.make_screen_with_flash(human_board, agent_board, history, attacker, True),
            console=self.console,
            screen=True,
            transient=True,
            refresh_per_second=10,
        ) as live:
            for active in (True, False, True, False, True):
                live.update(self.make_screen_with_flash(human_board, agent_board, history, attacker, active))
                time.sleep(0.14)
        self.render(human_board, agent_board, history)

    def make_screen_with_flash(
        self,
        human_board: BoardProtocol,
        agent_board: BoardProtocol,
        history: list[ShotResult],
        attacker: str,
        flash_active: bool,
    ) -> Any:
        return self.make_screen(
            human_board,
            agent_board,
            history,
            status="Resultado do tiro.",
            flash_attacker=attacker,
            flash_active=flash_active,
        )

    def show_outcome(
        self,
        title: str,
        subtitle: str,
        human_board: BoardProtocol | None = None,
        agent_board: BoardProtocol | None = None,
        history: list[ShotResult] | None = None,
    ) -> None:
        if not self.console or not Panel or Live is None:
            if human_board is not None and agent_board is not None:
                print(format_board_plain("Sua frota", human_board, reveal_ships=True))
                print(format_board_plain("Águas inimigas", agent_board, reveal_ships=False))
            print(title)
            print(subtitle)
            return

        lines = outcome_ascii(title)
        frames = reveal_from_edges(lines)
        with Live(
            self.make_outcome_screen(frames[0], title, subtitle, human_board, agent_board, history),
            console=self.console,
            screen=False,
            transient=False,
            refresh_per_second=12,
        ) as live:
            for frame in frames:
                live.update(self.make_outcome_screen(frame, title, subtitle, human_board, agent_board, history))
                time.sleep(0.08)

            for visible in [False, True, False, True, False, True]:
                live.update(
                    self.make_outcome_screen(
                        lines if visible else blank_like(lines),
                        title,
                        subtitle,
                        human_board,
                        agent_board,
                        history,
                    )
                )
                time.sleep(0.22)

            live.update(self.make_outcome_screen(lines, title, subtitle, human_board, agent_board, history))
            time.sleep(0.7)

    def make_outcome_screen(
        self,
        lines: list[str],
        title: str,
        subtitle: str,
        human_board: BoardProtocol | None,
        agent_board: BoardProtocol | None,
        history: list[ShotResult] | None,
    ) -> Any:
        outcome = make_outcome_panel(lines, title, subtitle)
        if human_board is None or agent_board is None:
            return outcome

        summary = self.make_screen(human_board, agent_board, history or [])
        return Group(summary, outcome) if Group else outcome


    def _render_history_plain(self, history: list[ShotResult]) -> None:
        if not history:
            return

        print("Últimos tiros:")
        for item in history[-5:]:
            print(f"  {item.attacker}: {item.coordinate} -> {display_result(item.result)}")


def make_board_table(
    title: str,
    board: BoardProtocol,
    reveal_ships: bool,
    selection: tuple[str, int, int] | None = None,
    selection_active: bool = True,
    placement_preview: tuple[str, int, int, int, str, bool] | None = None,
) -> Any:
    row_count, col_count = board_shape(board)
    preview_cells = preview_coordinates(placement_preview, row_count, col_count)
    preview_valid = placement_preview[5] if placement_preview else True
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
        box=box.SQUARE if box else None,
        pad_edge=False,
    )
    table.add_column("", justify="right", width=3, no_wrap=True)
    for col in range(col_count):
        table.add_column(chr(ord("A") + col), justify="center", width=CELL_WIDTH, no_wrap=True)

    for row in range(row_count):
        cells = [
            render_cell(
                int(board.grid[row, col]),
                reveal_ships,
                checker=(row + col) % 2 == 0,
                selected=bool(selection and selection[1] == row and selection[2] == col),
                selection_active=selection_active,
                preview=(row, col) in preview_cells,
                preview_valid=preview_valid,
            )
            for col in range(col_count)
        ]
        table.add_row(str(row + 1), *cells)
    return table


def make_side_panel(
    history: list[ShotResult],
    board_rows: int,
    flash_attacker: str | None = None,
    flash_active: bool = False,
) -> Any:
    if not Group:
        return make_history_panel(history)
    board_height = 2 * board_rows + 5
    result_height = 8
    history_height = max(6, board_height - (2 * result_height) - 1)
    return Group(
        make_history_panel(history, height=history_height),
        Text("") if Text else "",
        make_player_result_panel(
            history,
            attacker="human",
            title="Seu tiro",
            flash_active=flash_attacker == "human" and flash_active,
            height=result_height,
        ),
        make_player_result_panel(
            history,
            attacker="agent",
            title="Agente",
            flash_active=flash_attacker == "agent" and flash_active,
            height=result_height,
        ),
    )


def make_history_panel(history: list[ShotResult], height: int | None = None) -> Any:
    lines = [f"{item.attacker}: {item.coordinate} -> {display_result(item.result)}" for item in history[-12:]]
    content = "\n".join(lines) if lines else "Sem tiros ainda."
    if Panel:
        return Panel(content, title="Histórico", width=32, height=height)
    return content

def make_player_result_panel(
    history: list[ShotResult],
    attacker: str,
    title: str,
    flash_active: bool = False,
    height: int | None = None,
) -> Any:
    latest = latest_for_attacker(history, attacker)
    if latest is None:
        content = "Aguardando tiro."
        return Panel(content, title=title, width=32, height=height) if Panel else content

    lines = result_ascii(latest.result)
    color = "bold yellow" if flash_active else result_color(latest.result)
    label = f"{latest.coordinate} -> {display_result(latest.result)}"
    if Text:
        text = Text("\n".join(lines), style=color)
        text.append(f"\n{label}", style="bold white")
        content = Align.center(text) if Align else text
    else:
        content = "\n".join(lines + [label])
    return Panel(content, title=title, width=32, height=height, border_style=color) if Panel else content


def latest_for_attacker(history: list[ShotResult], attacker: str) -> ShotResult | None:
    for item in reversed(history):
        if item.attacker == attacker:
            return item
    return None


def format_board_plain(title: str, board: BoardProtocol, reveal_ships: bool) -> str:
    row_count, col_count = board_shape(board)
    lines = [title, "    " + " ".join(chr(ord("A") + col) for col in range(col_count))]
    for row in range(row_count):
        cells = [render_cell_plain(int(board.grid[row, col]), reveal_ships) for col in range(col_count)]
        lines.append(f"{row + 1:>2}  " + " ".join(cells))
    return "\n".join(lines)


def render_cell(
    value: int,
    reveal_ships: bool,
    checker: bool = False,
    selected: bool = False,
    selection_active: bool = True,
    preview: bool = False,
    preview_valid: bool = True,
) -> Any:
    text_value = " " * CELL_WIDTH
    if Text:
        return Text(
            text_value,
            style=cell_style(value, reveal_ships, checker, selected, selection_active, preview, preview_valid),
        )
    if preview:
        style = "black on green bold" if preview_valid else "white on red bold"
        return f"[{style}]{text_value}[/]"
    if selected and selection_active:
        style = "black on yellow bold"
        return f"[{style}]{text_value}[/]"
    if value == -1:
        return f"[on blue]{text_value}[/]"
    if value == -2:
        return f"[on red]{text_value}[/]"
    if value > 0 and reveal_ships:
        return f"[on green]{text_value}[/]"
    background = "on grey19" if checker else "on grey11"
    return f"[{background}]{text_value}[/]"


def render_cell_plain(value: int, reveal_ships: bool) -> str:
    if value == -1:
        return "o"
    if value == -2:
        return "X"
    if value > 0 and reveal_ships:
        return "S"
    return "~"


def cell_style(
    value: int,
    reveal_ships: bool,
    checker: bool,
    selected: bool,
    selection_active: bool,
    preview: bool,
    preview_valid: bool,
) -> str:
    if preview:
        return "on green" if preview_valid else "on red"
    if selected and selection_active:
        return "on yellow"
    if value == -1:
        return "on blue"
    if value == -2:
        return "on red"
    if value > 0 and reveal_ships:
        return "on green"
    return "on grey23" if checker else "on grey15"


def result_ascii(result: str) -> list[str]:
    normalized = result.strip().lower()
    if normalized == "agua":
        return [
            "M   M  III   SSS   SSS ",
            "MM MM   I   S     S    ",
            "M M M   I    SSS   SSS ",
            "M   M   I       S     S",
            "M   M  III  SSS   SSS ",
        ]
    if normalized == "acerto":
        return [
            "H   H  III  TTTTT",
            "H   H   I     T  ",
            "HHHHH   I     T  ",
            "H   H   I     T  ",
            "H   H  III    T  ",
        ]
    if normalized == "afundado":
        return [
            " SSS  U   U  N   N  K  K",
            "S     U   U  NN  N  K K ",
            " SSS  U   U  N N N  KK  ",
            "    S U   U  N  NN  K K ",
            "SSS    UUU   N   N  K  K",
        ]
    return [
        "R R   EEE  SSS ",
        "RR    E    S   ",
        "R R   EEE   SSS",
    ]


def result_color(result: str) -> str:
    normalized = result.strip().lower()
    if normalized == "agua":
        return "bold blue"
    if normalized == "acerto":
        return "bold red"
    if normalized == "afundado":
        return "bold magenta"
    return "bold yellow"


def board_shape(board: BoardProtocol) -> tuple[int, int]:
    return int(board.grid.shape[0]), int(board.grid.shape[1])


def cursor_path(start: tuple[int, int], target: tuple[int, int]) -> list[tuple[int, int]]:
    row, col = start
    target_row, target_col = target
    path = [(row, col)]

    while row != target_row:
        row += 1 if target_row > row else -1
        path.append((row, col))

    while col != target_col:
        col += 1 if target_col > col else -1
        path.append((row, col))

    return path


def preview_coordinates(
    placement_preview: tuple[str, int, int, int, str, bool] | None,
    row_count: int,
    col_count: int,
) -> set[tuple[int, int]]:
    if not placement_preview:
        return set()

    _, row, col, size, orientation, _ = placement_preview
    cells = set()
    for offset in range(size):
        preview_row = row + offset if orientation == "V" else row
        preview_col = col + offset if orientation == "H" else col
        if 0 <= preview_row < row_count and 0 <= preview_col < col_count:
            cells.add((preview_row, preview_col))
    return cells


def outcome_ascii(title: str) -> list[str]:
    normalized = title.strip().upper()
    if normalized == "WINNER":
        return [
            "W       W  IIIIIII  N     N  N     N  EEEEEEE  RRRRRR ",
            "W       W     I     NN    N  NN    N  E        R     R",
            "W       W     I     N N   N  N N   N  E        R     R",
            "W   W   W     I     N  N  N  N  N  N  EEEEE    RRRRRR ",
            "W  W W  W     I     N   N N  N   N N  E        R   R  ",
            "W W   W W     I     N    NN  N    NN  E        R    R ",
            "WW     WW  IIIIIII  N     N  N     N  EEEEEEE  R     R",
        ]
    if normalized == "LOSER":
        return [
            "L        OOOOO   SSSSSS  EEEEEEE  RRRRRR ",
            "L       O     O  S       E        R     R",
            "L       O     O  S       E        R     R",
            "L       O     O  SSSSS   EEEEE    RRRRRR ",
            "L       O     O       S  E        R   R  ",
            "L       O     O       S  E        R    R ",
            "LLLLLLL  OOOOO   SSSSS   EEEEEEE  R     R",
        ]
    return [normalized]


def reveal_from_edges(lines: list[str]) -> list[list[str]]:
    width = max(len(line) for line in lines)
    padded = [line.ljust(width) for line in lines]
    frames: list[list[str]] = []
    for step in range((width + 1) // 2):
        frame = []
        for line in padded:
            chars = [" "] * width
            for index in range(step + 1):
                chars[index] = line[index]
                chars[width - 1 - index] = line[width - 1 - index]
            frame.append("".join(chars).rstrip())
        frames.append(frame)
    return frames


def blank_like(lines: list[str]) -> list[str]:
    width = max(len(line) for line in lines)
    return [" " * width for _ in lines]


def make_outcome_panel(lines: list[str], title: str, subtitle: str) -> Any:
    color = "bold green" if title.upper() == "WINNER" else "bold red"
    content = "\n".join(lines)
    if Text:
        text = Text(content, style=color)
        if subtitle:
            text.append(f"\n\n{subtitle}", style="bold white")
        renderable = Align.center(text, vertical="middle") if Align else text
    else:
        renderable = content
    return Panel(renderable, title=title, border_style=color)
