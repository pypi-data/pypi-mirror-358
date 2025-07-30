import logging

from clypi import ClypiConfig, ClypiException, Command, arg, configure
from typing_extensions import override

from .directory import Directory
from .errors import SimpleRecorderError
from .gui import SimpleRecorderWindow
from .pause import Pause
from .resume import Resume
from .start import Start
from .stop import Stop

logger = logging.getLogger(__name__)

config = ClypiConfig(
    nice_errors=(SimpleRecorderError,),
)
configure(config)

themes = [
    "Light Purple",
    "Neutral Blue",
    "Reds",
    "Sandy Beach",
    "Kayak",
    "Light Blue 2",
]


def theme_parser(value: str) -> str:
    """Parse the theme argument."""
    if value not in themes:
        raise ClypiException(
            f"Invalid theme: {value}. Available themes: {', '.join(themes)}"
        )
    return value


class SimpleRecorder(Command):
    subcommand: Start | Stop | Pause | Resume | Directory | None = None
    host: str = arg(default="localhost", env="OBS_HOST", help="OBS WebSocket host")
    port: int = arg(default=4455, env="OBS_PORT", help="OBS WebSocket port")
    password: str | None = arg(
        default=None, env="OBS_PASSWORD", help="OBS WebSocket password"
    )
    theme: str = arg(
        default="Reds",
        parser=theme_parser,
        env="OBS_THEME",
        help=f"GUI theme ({', '.join(themes)})",
    )
    debug: bool = arg(
        default=False,
        env="DEBUG",
        help="Enable debug logging",
        hidden=True,
    )

    @override
    async def run(self):
        """Run the Simple Recorder GUI."""
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

        window = SimpleRecorderWindow(self.host, self.port, self.password, self.theme)
        await window.run()


def run():
    """Run the application."""
    SimpleRecorder.parse().start()
