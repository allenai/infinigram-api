#! /bin/bash

echo Copying infini-gram unigrams $INDEX_NAME
gcloud storage cp gs://infinigram/index/${INDEX_NAME}/unigram.* /mnt/infini-gram-array/
echo Finished copying infini-gram array $INDEX_NAME