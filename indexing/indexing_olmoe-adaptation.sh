#!/usr/bin/env bash

RUN_NAME="index_v4_olmoe-adaptation"

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
        --data_dir /weka/oe-training-default/jiachengl/raw/tulu-v3.1-mix-preview-4096-OLMoE \
        --save_dir /weka/oe-training-default/jiachengl/index/v4_tulu-v3.1-mix-preview-4096-OLMoE_llama ; \
    python indexing.py \
        --tokenizer llama --cpus 64 --mem 900 --shards 1 --add_metadata --ulimit 524288 \
        --data_dir /weka/oe-training-default/jiachengl/raw/ultrafeedback_binarized_cleaned \
        --save_dir /weka/oe-training-default/jiachengl/index/v4_ultrafeedback-binarized-cleaned_llama ; \
    aws s3 sync /weka/oe-training-default/jiachengl/index/v4_tulu-v3.1-mix-preview-4096-OLMoE_llama s3://infini-gram/index/v4_tulu-v3.1-mix-preview-4096-OLMoE_llama ; \
    aws s3 sync /weka/oe-training-default/jiachengl/index/v4_ultrafeedback-binarized-cleaned_llama s3://infini-gram/index/v4_ultrafeedback-binarized-cleaned_llama ; \
    "
