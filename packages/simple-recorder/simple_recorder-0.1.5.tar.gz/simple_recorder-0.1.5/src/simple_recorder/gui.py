import logging

import FreeSimpleGUI as fsg
from clypi import ClypiException

from .start import Start
from .stop import Stop

logger = logging.getLogger(__name__)


class SimpleRecorderWindow(fsg.Window):
    def __init__(self, host, port, password, theme):
        self.logger = logger.getChild(self.__class__.__name__)
        self.host = host
        self.port = port
        self.password = password
        fsg.theme(theme)

        layout = [
            [fsg.Text("Enter recording filename:")],
            [fsg.InputText("", key="-FILENAME-")],
            [fsg.Button("Start Recording"), fsg.Button("Stop Recording")],
            [fsg.Text("Status: Not started", key="-OUTPUT-")],
        ]
        super().__init__("Simple Recorder", layout, finalize=True)
        self["-FILENAME-"].bind("<Return>", " || RETURN")
        self["Start Recording"].bind("<Return>", " || RETURN")
        self["Stop Recording"].bind("<Return>", " || RETURN")

    async def run(self):
        while True:
            event, values = self.read()
            if event == fsg.WIN_CLOSED:
                break

            match event.split(" || "):
                case ["Start Recording", "RETURN" | None] | ["-FILENAME-", "RETURN"]:
                    try:
                        await Start(
                            filename=values["-FILENAME-"],
                            host=self.host,
                            port=self.port,
                            password=self.password,
                        ).run()
                        self["-OUTPUT-"].update(
                            "Recording started successfully", text_color="green"
                        )
                    except ClypiException as e:
                        self["-OUTPUT-"].update(
                            f"Error: {e.raw_message}", text_color="red"
                        )

                case ["Stop Recording", "RETURN" | None]:
                    try:
                        await Stop(
                            host=self.host, port=self.port, password=self.password
                        ).run()
                        self["-OUTPUT-"].update(
                            "Recording stopped successfully", text_color="green"
                        )
                    except ClypiException as e:
                        self["-OUTPUT-"].update(
                            f"Error: {e.raw_message}", text_color="red"
                        )

                case _:
                    self.logger.warning(f"Unhandled event: {event}")

        self.close()
