#!/usr/bin/env bash

RUN_NAME="index_v4_olmoe-mix-0924-dclm_llama"

gantry run \
  --allow-dirty \
  --name ${RUN_NAME} \
  --task-name ${RUN_NAME} \
  --description ${RUN_NAME} \
  --workspace ai2/hb-wolf-olmo \
  --budget ai2/oe-training \
  --beaker-image shanea/olmo-torch2.2-gantry \
  --cluster ai2/jupiter-cirrascale-2 \
  --priority high \
  --preemptible \
  --no-nfs \
  --weka oe-training-default:/weka/oe-training-default \
  --weka oe-data-default:/weka/oe-data-default \
  --cpus 186 \
  --memory 1912GiB \
  --shared-memory 10GiB \
  --replicas 10 \
  --host-networking \
  --leader-selection \
  --propagate-failure \
  --propagate-preemption \
  --synchronized-start-timeout 48h \
  --no-python \
  --venv base \
  --env-secret HF_TOKEN=HF_TOKEN \
  --yes \
  -- /bin/bash -c "\
    pip install infini-gram zstandard tqdm transformers sentencepiece ; \
    cd /opt/miniconda3/lib/python3.10/site-packages/infini_gram ; \
    python indexing.py \
        --tokenizer llama --cpus 186 --mem 1912 --shards 10 --workers 10 --worker_id \$BEAKER_REPLICA_RANK --add_metadata --ulimit 524288 \
        --data_dir /weka/oe-data-default/ai2-llm/pretraining-data/sources/olmo-mix/olmoe-mix-0924/documents/dclm \
        --save_dir /weka/oe-training-default/jiachengl/index/v4_olmoe-mix-0924-dclm_llama ; \
    "
