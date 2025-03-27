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