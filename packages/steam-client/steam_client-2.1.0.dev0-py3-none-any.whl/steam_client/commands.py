from typing import List
import webbrowser
from enum import StrEnum

SCHEME = 'steam'

class SteamWindows(StrEnum):
    """Enumeration of Steam client windows."""
    MAIN = 'main'
    GAMES = 'games'
    GAMES_DETAILS = 'games/details'
    GAMES_GRID = 'games/grid'
    GAMES_LIST = 'games/list'
    FRIENDS = 'friends'
    CHAT = 'chat'
    BIGPICTURE = 'bigpicture'
    NEWS = 'news'
    SETTINGS = 'settings'
    TOOLS = 'tools'
    CONSOLE = 'console'

class Command():
   
    def __init__(self, scheme: str):
        self._scheme = scheme

    def _create_uri(self, path: List[str], endpoint: str) -> str:
        return f'{self._scheme}://{"/".join(path)}/{endpoint}'

    def __call__(self, path: List[str], endpoint: str) -> None:
        """Executes the command with the specified endpoint."""
        webbrowser.open(self._create_uri(path, endpoint))


class Commands:
    """A collection of commands for the Steam client."""

    def __init__(self):
        self._command = Command(SCHEME)

    def run_game_id(self, app_id: str) -> str:
        """Launches game with the specified ID in the Steam client."""
        self._command(['rungameid'], app_id)

    def store(self, app_id: str) -> str:
        """Opens the game's store page in the Steam client."""
        self._command(['store'], app_id)

    def install(self, app_id: str) -> str:
        """Opens the game's install prompt in the Steam client."""
        self._command(['install'], app_id)

    def uninstall(self, app_id: str) -> str:
        """Opens the game's uninstall prompt in the Steam client."""
        self._command(['uninstall'], app_id)

    def update_news(self, app_id: str) -> str:
        """Opens the game's update news in the Steam client."""
        self._command(['updatenews'], app_id)

    def open(self, window: SteamWindows) -> str:
        """Opens the specified window in the Steam client."""
        self._command(['open'], window)

    def open_url(self, url: str) -> str:
        """Opens the specified URL in the Steam client."""
        self._command(['openurl'], url)


