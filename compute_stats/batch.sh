#!/usr/bin/env bash

RUN_NAME="compute-stats_olmoe-mix-0924"

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
  --no-python \
  --venv base \
  --yes \
  -- /bin/bash -c "\
    pip install zstandard tqdm ; \
    mkdir /weka/oe-training-default/jiachengl/stat ; \
    python compute_stats/batch.py \
        --data_dir /weka/oe-data-default/ai2-llm/pretraining-data/sources/olmo-mix/olmoe-mix-0924/documents \
        --cpus 180 --workers 60 \
        --output_path /weka/oe-training-default/jiachengl/stat/olmoe-mix-0924.json ; \
    "
