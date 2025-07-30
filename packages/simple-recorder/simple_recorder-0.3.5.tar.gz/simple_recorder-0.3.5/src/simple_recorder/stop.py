import obsws_python as obsws
from clypi import Command, arg
from typing_extensions import override

from .errors import SimpleRecorderError
from .styler import highlight


class Stop(Command):
    """Stop recording."""

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
                    raise SimpleRecorderError("Recording is not active.")

                client.stop_record()
                print(highlight("Recording stopped successfully."))
        except (ConnectionRefusedError, TimeoutError):
            raise SimpleRecorderError("Failed to connect to OBS. Is it running?")
