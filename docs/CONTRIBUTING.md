# How to contribute to Infini-gram API

## Setting up your environment

### Prerequisites

Make sure that you have the latest version of [Docker 🐳](https://www.docker.com/get-started)
installed on your local machine.

### Installing Dependencies

#### Install uv

This repo uses `uv` for Python dependency management. Follow the instructions on https://docs.astral.sh/uv/getting-started/installation to install it.

Run `uv sync --all-packages` to get the packages for every project in this repo.

#### Adding an index for local development

1. Ensure you have the `aws` cli installed. run `brew install awscli` if you don't.
2. Download the `v4_pileval_llama` index by running `./bin/download-infini-gram-array.sh`

The `infinigram-array` folder is mounted to the Docker container for the API through the `docker-compose`. 

## Linting and Formatting

We use `Ruff` and `mypy` to lint, format, and check for type issues.

### CLI
To check for `Ruff` issues, run `uv run ruff check`. If you want to have it automatically fix issues, run `uv run ruff check --fix`. If you want to have it format your code, run `uv run ruff format`.

To check for `mypy` issues, run `uv run mypy --config ./pyproject.toml`

### VSCode
Install the [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) and [mypy](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker) extensions. These are listed in the "Recommended Extensions" for the workspace as well.

## Running the server

### Docker Compose
The easiest way to run the full setup is to use the Docker Compose file. This will start the API, worker, proxy, and queue with all the appropriate connections.

To start with Docker Compose, run `docker compose up` in the root of this repo.


### Outside of Docker
If you want to run applications outside of docker, you'll need to set up a queue yourself. The easiest method is to still go through Compose by just starting the queue. `docker compose up queue`

After that, make sure your environment variables are set correctly through a `.env` file or just environment variables, then run the services.
API: `uv run api/app.py`
Worker: `uv run saq attribution_worker.worker.settings`