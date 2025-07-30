import obsws_python as obsws
from clypi import Command, arg
from typing_extensions import override

from .errors import SimpleRecorderError


class Pause(Command):
    """Pause recording."""

    host: str = arg(inherited=True)
    port: int = arg(inherited=True)
    password: str = arg(inherited=True)

    @override
    async def run(self):
        try:
            with obsws.ReqClient(
                host=self.host, port=self.port, password=self.password, timeout=3
            ) as client:
                resp = client.get_record_status()
                if not resp.output_active:
                    raise SimpleRecorderError("No active recording to pause.")
                if resp.output_paused:
                    raise SimpleRecorderError("Recording is already paused.")

                client.pause_record()
                print("Recording paused successfully.")
        except (ConnectionRefusedError, TimeoutError):
            raise SimpleRecorderError("Failed to connect to OBS. Is it running?")
