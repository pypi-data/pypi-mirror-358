import logging

import FreeSimpleGUI as fsg
import obsws_python as obsws

from .directory import Directory
from .errors import SimpleRecorderError
from .pause import Pause
from .resume import Resume
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

        try:
            with obsws.ReqClient(
                host=self.host, port=self.port, password=self.password, timeout=3
            ) as client:
                resp = client.get_version()
                status_message = f"Connected to OBS {resp.obs_version} ✓"
                resp = client.get_record_directory()
                current_directory = resp.record_directory
        except (ConnectionRefusedError, TimeoutError):
            status_message = "Failed to connect to OBS. Is it running?"
            current_directory = ""

        recorder_layout = [
            [fsg.Text("Enter recording filename:", key="-PROMPT-")],
            [fsg.InputText("default_name", key="-FILENAME-", focus=True)],
            [
                fsg.Button("Start", key="Start Recording", size=(20, 1)),
                fsg.Button("Stop", key="Stop Recording", size=(20, 1)),
            ],
            [
                fsg.Button("Pause", key="Pause Recording", size=(20, 1)),
                fsg.Button("Resume", key="Resume Recording", size=(20, 1)),
            ],
            [
                fsg.Button("Split", key="Split Recording", size=(20, 1)),
                fsg.Button("Add Chapter", key="Add Chapter", size=(20, 1)),
            ],
        ]

        frame = fsg.Frame(
            "",
            recorder_layout,
            relief=fsg.RELIEF_SUNKEN,
        )

        recorder_tab = fsg.Tab(
            "Recorder",
            [
                [frame],
                [
                    fsg.Text(
                        f"Status: {status_message}",
                        key="-OUTPUT-RECORDER-",
                        text_color="white"
                        if status_message.startswith("Connected")
                        else "red",
                    )
                ],
            ],
        )

        settings_layout = [
            [fsg.Text("Enter the filepath for the recording:")],
            [fsg.InputText(current_directory, key="-FILEPATH-", size=(45, 1))],
            [
                fsg.Button("Get Current", key="-GET-CURRENT-", size=(10, 1)),
                fsg.Button("Update", key="-UPDATE-", size=(10, 1)),
            ],
            [fsg.Text("", key="-OUTPUT-SETTINGS-", text_color="white")],
        ]

        settings_tab = fsg.Tab("Settings", settings_layout)

        mainframe = [
            [fsg.TabGroup([[recorder_tab, settings_tab]])],
        ]

        super().__init__("Simple Recorder", mainframe, finalize=True)
        self["-FILENAME-"].bind("<Return>", " || RETURN")
        self["Start Recording"].bind("<Return>", " || RETURN")
        self["Stop Recording"].bind("<Return>", " || RETURN")
        self["Pause Recording"].bind("<Return>", " || RETURN")
        self["Resume Recording"].bind("<Return>", " || RETURN")

        self["-FILENAME-"].bind("<KeyPress>", " || KEYPRESS")
        self["-FILENAME-"].update(select=True)
        self["Add Chapter"].bind("<FocusIn>", " || FOCUS")
        self["Add Chapter"].bind("<Enter>", " || FOCUS")
        self["Add Chapter"].bind("<FocusOut>", " || LEAVE")
        self["Add Chapter"].bind("<Leave>", " || LEAVE")
        self["Add Chapter"].bind("<Button-3>", " || RIGHT_CLICK")

        self["-GET-CURRENT-"].bind("<Return>", " || RETURN")
        self["-UPDATE-"].bind("<Return>", " || RETURN")

    async def run(self):
        while True:
            event, values = self.read()
            self.logger.debug(f"Event: {event}, Values: {values}")
            if event == fsg.WIN_CLOSED:
                break

            match e := event.split(" || "):
                case ["Start Recording"] | ["Start Recording" | "-FILENAME-", "RETURN"]:
                    try:
                        await Start(
                            filename=values["-FILENAME-"],
                            host=self.host,
                            port=self.port,
                            password=self.password,
                        ).run()
                        self["-OUTPUT-RECORDER-"].update(
                            "Recording started successfully", text_color="green"
                        )
                    except SimpleRecorderError as e:
                        self["-OUTPUT-RECORDER-"].update(
                            f"Error: {e.raw_message}", text_color="red"
                        )

                case ["Stop Recording"] | ["Stop Recording", "RETURN"]:
                    try:
                        await Stop(
                            host=self.host, port=self.port, password=self.password
                        ).run()
                        self["-OUTPUT-RECORDER-"].update(
                            "Recording stopped successfully", text_color="green"
                        )
                    except SimpleRecorderError as e:
                        self["-OUTPUT-RECORDER-"].update(
                            f"Error: {e.raw_message}", text_color="red"
                        )

                case ["Pause Recording"] | ["Pause Recording", "RETURN"]:
                    try:
                        await Pause(
                            host=self.host, port=self.port, password=self.password
                        ).run()
                        self["-OUTPUT-RECORDER-"].update(
                            "Recording paused successfully", text_color="green"
                        )
                    except SimpleRecorderError as e:
                        self["-OUTPUT-RECORDER-"].update(
                            f"Error: {e.raw_message}", text_color="red"
                        )

                case ["Resume Recording"] | ["Resume Recording", "RETURN"]:
                    try:
                        await Resume(
                            host=self.host, port=self.port, password=self.password
                        ).run()
                        self["-OUTPUT-RECORDER-"].update(
                            "Recording resumed successfully", text_color="green"
                        )
                    except SimpleRecorderError as e:
                        self["-OUTPUT-RECORDER-"].update(
                            f"Error: {e.raw_message}", text_color="red"
                        )

                case ["Add Chapter", "FOCUS" | "LEAVE" as focus_event]:
                    if focus_event == "FOCUS":
                        self["-OUTPUT-RECORDER-"].update(
                            "Right-click to set a chapter name", text_color="white"
                        )
                    else:
                        self["-OUTPUT-RECORDER-"].update("", text_color="white")

                case ["Add Chapter", "RIGHT_CLICK"]:
                    _ = fsg.popup_get_text(
                        "Enter chapter name:",
                        "Add Chapter",
                        default_text="unnamed",
                    )

                case ["Split Recording" | "Add Chapter"]:
                    self["-OUTPUT-RECORDER-"].update(
                        "This feature is not implemented yet", text_color="orange"
                    )

                case ["-GET-CURRENT-"] | ["-GET-CURRENT-", "RETURN"]:
                    try:
                        current_directory = await Directory(
                            host=self.host, port=self.port, password=self.password
                        ).run()
                        self["-FILEPATH-"].update(current_directory)
                    except SimpleRecorderError as e:
                        self["-OUTPUT-SETTINGS-"].update(
                            f"Error: {e.raw_message}", text_color="red"
                        )

                case ["-UPDATE-"] | ["-UPDATE-", "RETURN"]:
                    filepath = values["-FILEPATH-"]
                    if not filepath:
                        self["-OUTPUT-SETTINGS-"].update(
                            "Filepath cannot be empty", text_color="red"
                        )
                    else:
                        try:
                            await Directory(
                                directory=filepath,
                                host=self.host,
                                port=self.port,
                                password=self.password,
                            ).run()
                            self["-OUTPUT-SETTINGS-"].update(
                                "Recording directory updated successfully.",
                                text_color="green",
                            )
                        except SimpleRecorderError as e:
                            self["-OUTPUT-SETTINGS-"].update(
                                f"Error: {e.raw_message}", text_color="red"
                            )

                case _:
                    self.logger.debug(f"Unhandled event: {e}")

        self.close()
