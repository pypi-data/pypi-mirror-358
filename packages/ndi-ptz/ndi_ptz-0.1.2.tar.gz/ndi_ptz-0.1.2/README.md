# ndi-ptz

This is a CLI to control an NDI-enabled PTZ camera with a joystick.

Currently, everything in here requires a custom cyndilib,
see https://github.com/nocarryr/cyndilib/pull/25.

## Installation

```shell
uv tool install ndi-ptz

# or
pip install ndi-ptz
```

## Quick-Start

```shell
$ ndi-ptz list-sources
Looking for NDI sources in the next 5 seconds
TAIL_AIR_006666 (OBSBOT)

$ ndi-ptz list-joysticks
Looking for joysticks in the next 5 seconds
Nintendo Switch Pro Controller (0)

$ ndi-ptz control --source-name "TAIL_AIR_006666 (OBSBOT)" --joystick-instance 0
```

## Supported Joysticks

Currently only the following joysticks are supported:

- Nintendo Switch Pro Controller

## Development

This project is managed with [UV](https://docs.astral.sh/uv/).

### Build & Publish

```bash
# edit the project version in pyproject.toml
uv sync
git commit -m "Prepare 0.1.0" .
git tag '0.1.0'
rm -rf dist
uv build
uv publish
git push --tags
git push
```
