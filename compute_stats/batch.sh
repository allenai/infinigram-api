#!/usr/bin/env bash

RUN_NAME="compute-stats_olmoe-mix-0924"

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
  --weka oe-data-default:/weka/oe-data-default \
  --cpus 248 \
  --memory 900GiB \
  --shared-memory 10GiB \
  --no-python \
  --venv base \
  --yes \
  -- /bin/bash -c "\
    pip install zstandard tqdm ; \
    python compute_stats/batch.py \
        --data_dir /weka/oe-data-default/ai2-llm/pretraining-data/sources/olmo-mix/olmoe-mix-0924/documents \
        --cpus 240 --workers 16 \
        --output_path /weka/oe-training-default/jiachengl/stat/olmoe-mix-0924.json ; \
    "
