import obsws_python as obsws
from clypi import Command, Positional, arg
from typing_extensions import override

from .errors import SimpleRecorderError
from .styler import highlight


class Directory(Command):
    """Get or set the recording directory."""

    directory: Positional[str] = arg(
        default=None,
        help="Directory to set for recordings. If not provided, the current directory will be displayed.",
    )
    host: str = arg(inherited=True)
    port: int = arg(inherited=True)
    password: str = arg(inherited=True)

    @override
    async def run(self):
        try:
            with obsws.ReqClient(
                host=self.host, port=self.port, password=self.password, timeout=3
            ) as client:
                if self.directory:
                    client.set_record_directory(self.directory)
                    print(f"Recording directory set to: {highlight(self.directory)}")
                else:
                    resp = client.get_record_directory()
                    print(
                        f"Current recording directory: {highlight(resp.record_directory)}"
                    )
                    return resp.record_directory
        except (ConnectionRefusedError, TimeoutError):
            raise SimpleRecorderError("Failed to connect to OBS. Is it running?")
