#!/usr/bin/env bash

RUN_NAME="index_v4_olmo2-anneal-adapt"

gantry run \
  --allow-dirty \
  --name ${RUN_NAME} \
  --task-name ${RUN_NAME} \
  --description ${RUN_NAME} \
  --workspace ai2/attribution \
  --budget ai2/oe-training \
  --beaker-image shanea/olmo-torch2.2-gantry \
  --cluster ai2/neptune-cirrascale \
  --priority normal \
  --preemptible \
  --no-nfs \
  --weka oe-data-default:/weka/oe-data-default \
  --weka oe-training-default:/weka/oe-training-default \
  --cpus 248 \
  --memory 900GiB \
  --shared-memory 10GiB \
  --no-python \
  --venv base \
  --env-secret HF_TOKEN=HF_TOKEN \
  --env-secret AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID \
  --env-secret AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY \
  --yes \
  -- /bin/bash -c "\
    pip install infini-gram zstandard tqdm transformers sentencepiece awscli ; \
    cd /opt/miniconda3/lib/python3.10/site-packages/infini_gram ; \
    python indexing.py \
        --tokenizer llama --cpus 64 --mem 900 --shards 1 --add_metadata --ulimit 524288 \
        --data_dir /weka/oe-training-default/jiachengl/raw/olmo-2-1124-13b-anneal-adapt \
        --save_dir /weka/oe-training-default/jiachengl/index/v4_olmo-2-1124-13b-anneal-adapt_llama ; \
    aws s3 sync /weka/oe-training-default/jiachengl/index/v4_olmo-2-1124-13b-anneal-adapt_llama s3://infini-gram/index/v4_olmo-2-1124-13b-anneal-adapt_llama ; \
    "
