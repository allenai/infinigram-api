#!/bin/bash
if [ ! -d ./infinigram-array/v4_pileval_llama ]; then
    echo "Downloading v4_pileval_llama array"
    aws s3 cp --no-sign-request --recursive s3://infini-gram-lite/index/v4_pileval_llama ./infinigram-array/v4_pileval_llama
fi

if [ ! -d ./infinigram-array/dolma_1_6_sample ]; then
    echo "Copying v4_pileval_llama to dolma_1_6_sample"
    cp -r v4_pileval_llama ./infinigram-array/dolma_1_6_sample
fi

if [ ! -d ./infinigram-array/dolma_1_7 ]; then
    echo "Copying v4_pileval_llama to dolma_1_7"
    cp -r v4_pileval_llama ./infinigram-array/dolma_1_7
fi