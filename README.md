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

If you're on a Mac, you won't be able to install the infini-gram library locally. (It'll work in the docker-compose though!) To install other dependencies, install dependencies from `api/requirements/common-requirements.txt` instead of from `api/requirements.txt`.

`pip install -r requirements/common-requirements.txt`

### Adding an index for local development

1. Ensure you have the `aws` cli installed. run `brew install awscli` if you don't.
2. Download the `v4_pileval_llama` index by running `aws s3 cp --no-sign-request --recursive s3://infini-gram-lite/index/v4_pileval_llama <this repo's folder location>/infinigram-array`

The `infinigram-array` folder is mounted to the Docker container for the API through the `docker-compose`. 
