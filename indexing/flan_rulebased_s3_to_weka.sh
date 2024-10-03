#!/usr/bin/env bash

set -ex

NUM_NODES=1
RUN_NAME="copy_flan_rulebased_to_weka"

gantry run \
  --allow-dirty \
  --name ${RUN_NAME} \
  --task-name ${RUN_NAME} \
  --description ${RUN_NAME} \
  --workspace ai2/hb-wolf-olmo \
  --budget ai2/oe-training \
  --beaker-image petew/olmo-torch23-gantry \
  --cluster ai2/jupiter-cirrascale-2 \
  --priority high \
  --preemptible \
  --no-nfs \
  --weka oe-training-default:/weka/oe-training-default \
  --shared-memory 10GiB \
  --no-python \
  --env LOG_FILTER_TYPE=local_rank0_only \
  --env OMP_NUM_THREADS=8 \
  --env OLMO_TASK=model \
  --env WANDB__SERVICE_WAIT=300 \
  --env WANDB_HTTP_TIMEOUT=60 \
  --env-secret WANDB_API_KEY=WANDB_API_KEY \
  --env-secret AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID \
  --env-secret AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY \
  --yes \
  -- /bin/bash -c "\
    conda shell.bash activate base; \
    pip install awscli; \
    aws s3 cp --recursive s3://ai2-llm/preprocessed/tulu_flan/v1-decontaminated-60M-shots_all-upweight_1-dialog_false-sep_rulebased /weka/oe-training-default/ai2-llm/preprocessed/tulu_flan/v1-decontaminated-60M-shots_all-upweight_1-dialog_false-sep_rulebased; \
    "
