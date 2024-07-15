# skiff-template-python-api

## Reference
This application is only made possible by researchers working on this paper:
  Liu, Jiacheng and Min, Sewon and Zettlemoyer, Luke and Choi, Yejin and Hajishirzi, Hannaneh (2024).
  Infini-gram: Scaling Unbounded n-gram Language Models to a Trillion Tokens.
  arXiv preprint arXiv:2401.17377,

## Prerequisites

Make sure that you have the latest version of [Docker 🐳](https://www.docker.com/get-started)
installed on your local machine.

## Getting Started

### Installing Dependencies

If you're on a Mac, you won't be able to install the infini-gram library locally. (It'll work in the docker-compose though!) To install other dependencies, install dependencies from `api/requirements/dev-requirements.txt` instead of from `api/requirements.txt`.

`pip install -r requirements/dev-requirements.txt`

### Adding an index for local development

1. Ensure you have the `aws` cli installed. run `brew install awscli` if you don't.
2. Download the `v4_pileval_llama` index by running `./bin/download-infini-gram-array.sh`

The `infinigram-array` folder is mounted to the Docker container for the API through the `docker-compose`. 

## Adding a new infini-gram index

### On the prod server

TODO

### Locally

1. Add the ID of the index to `AvailableInfiniGramIndexId` in `api/src/infinigram/index_mappings.py`
2. Add the ID as a string to `IndexMappings` in `api/src/infinigram/index_mappings.py`
3. Add the tokenizer and index directory to `index_mappings` in `api/src/infinigram/index_mappings.py`
4. add a line in /bin/download-infini-gram-array.sh to make a new symlink with that array's path. The path will be the `index_dir` you added in `index_mappings` but has `/mnt/infinigram-array` replaced with `$INFINIGRAM_ARRAY_DIR`
5. Add a mount in `docker-compose.yaml`: `- ./infinigram-array/<ARRAY_PATH_NAME>:/mnt/infinigram-array/<ARRAY_PATH_NAME>

## Linting and Formatting

If you installed python packages through `dev-requirements.txt` (see #Installing Dependencies) you'll have `Ruff` and `mypy` available to locally check for code quality compliance. 

### CLI
To check for `Ruff` issues, run `ruff check`. If you want to have it automatically fix issues, run `ruff check --fix`. If you want to have it format your code, run `ruff format`.

To check for `mypy` issues, run `mypy --strict --config ./api/pyproject.toml`

### VSCode
Install the [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) and [mypy](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker) extensions. These are listed in the "Recommended Extensions" for the workspace as well.