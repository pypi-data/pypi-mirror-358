# simple-recorder

[![pdm-managed](https://img.shields.io/endpoint?url=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2Fpdm-project%2F.github%2Fbadge.json)](https://pdm-project.org)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A simple OBS recorder app. Run it as a CLI or a GUI.

---

## Requirements

-   Python 3.11 or greater
-   [OBS Studio 28+][obs-studio]

## Installation

*with uv*

```console
uv tool install simple-recorder
```

*with pipx*

```console
pipx install simple-recorder
```

*with pyz*

-   Download the pyz file in [Releases](https://github.com/onyx-and-iris/simple-recorder/releases)
-   Optional step: for automatic discovery of the pyz file follow this guide on [Setting Up Windows for Zippapps](https://jhermann.github.io/blog/python/deployment/2020/02/29/python_zippapps_on_windows.html#Setting-Up-Windows-10-for-Zipapps)

Finally run the pyz with python (CLI)/pythonw (GUI):

```console
python simple-recorder.pyz <subcommand>

pythonw simple-recorder.pyz
```

note, the pyz extension won't be required if you followed the optional step and made it discoverable.

## Configuration

Pass --host, --port and --password as flags on the root command:

```console
simple-recorder --host=localhost --port=4455 --password=<websocket password> --help
```

Or load them from your environment:

```env
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=<websocket password>
OBS_THEME=Reds
```

## Use

### CLI

To launch the CLI:

```console
simple-recorder start "File Name"

simple-recorder stop
```

#### Commands:

```shell
Usage: simple-recorder [OPTIONS] COMMAND

┏━ Subcommands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ start      Start recording                                                        ┃
┃ stop       Stop recording                                                         ┃
┃ pause      Pause recording                                                        ┃
┃ resume     Resume recording                                                       ┃
┃ directory  Get or set the recording directory                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ --host <HOST>          OBS WebSocket host                                         ┃
┃ --port <PORT>          OBS WebSocket port                                         ┃
┃ --password <PASSWORD>  OBS WebSocket password                                     ┃
┃ --theme <THEME>        GUI theme (Light Purple, Neutral Blue, Reds, Sandy Beach,  ┃
┃                        Kayak, Light Blue 2)                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### GUI

To launch the GUI:

```console
simple-recorder-gui
```

![simple-recorder](./img/simple-recorder.png)

Just enter the filename and click *Start*.

#### Themes

You can change the colour theme with the --theme option:

```console
simple-recorder-gui --theme="Light Purple"
```

[obs-studio]: https://obsproject.com/