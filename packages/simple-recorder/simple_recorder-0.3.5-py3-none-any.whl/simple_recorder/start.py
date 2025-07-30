from datetime import datetime

import obsws_python as obsws
from clypi import Command, Positional, arg
from typing_extensions import override

from .errors import SimpleRecorderError
from .styler import highlight


class Start(Command):
    """Start recording."""

    filename: Positional[str] = arg(
        default="default_name",
        help="Name of the recording",
        prompt="Enter the name for the recording",
    )
    host: str = arg(inherited=True)
    port: int = arg(inherited=True)
    password: str = arg(inherited=True)

    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    @override
    async def run(self):
        if not self.filename:
            raise SimpleRecorderError("Recording name cannot be empty.")

        try:
            with obsws.ReqClient(
                host=self.host, port=self.port, password=self.password, timeout=3
            ) as client:
                resp = client.get_record_status()
                if resp.output_active:
                    raise SimpleRecorderError("Recording is already active.")

                filename = f"{self.filename} {self.get_timestamp()}"
                client.set_profile_parameter(
                    "Output",
                    "FilenameFormatting",
                    filename,
                )
                client.start_record()
                print(f"Recording started with filename: {highlight(filename)}")
        except (ConnectionRefusedError, TimeoutError):
            raise SimpleRecorderError("Failed to connect to OBS. Is it running?")
