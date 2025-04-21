# aal-backend

REST api for the audio-analyses-app. Written in python. Only for generic, persistant logic.

---

## Features

-   [FastAPI](https://fastapi.tiangolo.com/) rest api in python
-   [mypy](https://mypy.readthedocs.io/en/latest/) for static typing
-   [uv](https://docs.astral.sh/uv/) for managing installs, dependency management and virtual envs
-   [docker](https://www.docker.com/) for containering and production deployment
-   [unittest](https://docs.python.org/3/library/unittest.html) for unit testing

---

## Prerequisites

Install:

-   [python](https://www.python.org/) v3.12
-   [uv](https://docs.astral.sh/uv/getting-started/installation/)
-   [docker](https://www.docker.com/)

---

## Installation

1. Clone the repo

```shell
git clone https://github.com/AudioAnalyseApp/aal-backend.git
cd aal-backend
```

2. Sync dependencies

```shell
uv sync
```

3. Run the app

```shell
uv run fastapi dev src/main.py
```

---

## Project Structure

**TODO**

---

## Usefull commands

Installing dependencies:

```shell
uv add library
```

Checking types:

```shell
uv run mypy . --strict
```

---

## Contributing

1. Branch of `development`
2. Work on your branch
3. Make sure all tests pass and mypy finds no type errors.
4. Create a PR to `development`

---

## Required VS Code extensions

-   https://marketplace.visualstudio.com/items/?itemName=ms-python.python
-   https://marketplace.visualstudio.com/items/?itemName=ms-python.mypy-type-checker
