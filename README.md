# aal-backend

REST api for the audio-analyses-app. Written in python. Only for generic, persistant logic.

---

## Features

-   [FastAPI](https://fastapi.tiangolo.com/) rest api in python
-   [mypy](https://mypy.readthedocs.io/en/latest/) for static typing
-   [uv](https://docs.astral.sh/uv/) for managing installs, dependency management and virtual envs
-   [docker](https://www.docker.com/) for containering and production deployment
-   [pytest](https://docs.pytest.org/en/stable/#) for unit testing
-   [python-socketio](https://python-socketio.readthedocs.io/en/latest/index.html) for bidirectional realtime messaging
-   [python-dotenv](https://pypi.org/project/python-dotenv/) for management of env vars
-   [sqlmodel](https://sqlmodel.tiangolo.com/tutorial/) for sql connection

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

```bash
src/
  api/              # Api router, models, endpoints
    endpoints/      # Api endpoints without business logic
    models/         # Outward facing api models
    router.py       # Router configuration
  database/         # DB access code and models
    models/         # DB ORM models
  models/           # Internal models / DTOs
  services/         # Business logic
  sio/              # Socket.io logic and events
  tests/            # Pytest unit tests
  main.py           # Entry point
```

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

Run unit tests:

```shell
uv run pytest
```

---

## Contributing

1. Branch of `development`
2. Work on your branch
3. Make sure all tests pass and mypy finds no type errors.
4. Create a PR to `development`

### Branch Naming Conventions:

Branch name should always start with `feature/`, `fix/`, `chore/` or `refactor/`, continued with the content of the branch. For example: `feature/microphone-impl`

---

## Required VS Code extensions

-   https://marketplace.visualstudio.com/items/?itemName=ms-python.python
-   https://marketplace.visualstudio.com/items/?itemName=ms-python.mypy-type-checker
