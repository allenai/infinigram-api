#! /bin/bash

echo Copying infini-gram array $INDEX_NAME
gcloud storage cp --recursive gs://infini-gram/index/${INDEX_NAME} /mnt/infini-gram-array/
echo Finished copying infini-gram array $INDEX_NAME