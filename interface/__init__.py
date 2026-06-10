from interface.agent_adapter import RandomAgent
from interface.cli import BattleshipCLI, run_cli
from interface.constants import BOARD_SIZE, DEFAULT_FLEET
from interface.contracts import AgentProtocol, BoardProtocol
from interface.coordinates import format_coordinate, normalize_coordinate, parse_coordinate
from interface.models import PublicGameState, ShotResult
from interface.placement import place_fleet_randomly
from interface.results import normalize_result

__all__ = [
    "BOARD_SIZE",
    "DEFAULT_FLEET",
    "AgentProtocol",
    "BattleshipCLI",
    "BoardProtocol",
    "PublicGameState",
    "RandomAgent",
    "ShotResult",
    "format_coordinate",
    "normalize_coordinate",
    "normalize_result",
    "parse_coordinate",
    "place_fleet_randomly",
    "run_cli",
]
