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

An executable pyz has been included in [Releases](https://github.com/onyx-and-iris/simple-recorder/releases) which you can run in Windows. Follow the steps in this [Setting up Windows for Zipapps](https://jhermann.github.io/blog/python/deployment/2020/02/29/python_zippapps_on_windows.html#Setting-Up-Windows-10-for-Zipapps) guide.

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

### GUI

To launch the GUI run the root command without any subcommands:

```console
simple-recorder
```

![simple-recorder](./img/simple-recorder.png)

Just enter the filename and click *Start Recording*.

#### Themes

However, passing flags is fine, for example to set the theme:

```console
simple-recorder --theme="Light Purple"
```

### CLI

```shell
Usage: simple-recorder [OPTIONS] COMMAND

┏━ Subcommands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ start   Start recording                                                             ┃
┃ stop    Stop recording                                                              ┃
┃ pause   Pause recording                                                             ┃
┃ resume  Resume recording                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ --host <HOST>          OBS WebSocket host                                           ┃
┃ --port <PORT>          OBS WebSocket port                                           ┃
┃ --password <PASSWORD>  OBS WebSocket password                                       ┃
┃ --theme <THEME>        GUI theme (Light Purple, Neutral Blue, Reds, Sandy Beach,    ┃
┃                        Kayak, Light Blue 2)                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

To launch the CLI pass any subcommand (start/stop etc...), for example:

```console
simple-recorder start "File Name"

simple-recorder stop
```

-   If no filename is passed to start then you will be prompted for one. 
    -   A default_name will be used if none is supplied to the prompt.

[obs-studio]: https://obsproject.com/