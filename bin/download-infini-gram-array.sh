#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
INFINIGRAM_ARRAY_DIR=$SCRIPT_DIR/../infinigram-array

# If you add an array here make sure you add it to docker-compose.yaml too

echo $INFINIGRAM_ARRAY_DIR
if [ ! -d $INFINIGRAM_ARRAY_DIR/v4_pileval_llama ]; then
    echo "Downloading v4_pileval_llama array"
    aws s3 cp --no-sign-request --recursive s3://infini-gram-lite/index/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/v4_pileval_llama
fi

if [ ! -d $INFINIGRAM_ARRAY_DIR/dolma_1_7 ]; then
    echo "creating a link from v4_pileval_llama to dolma_1_7"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/dolma_1_7
fi

if [ ! -d $INFINIGRAM_ARRAY_DIR/olmoe-mix-0924 ]; then
    echo "creating a link from v4_pileval_llama to olmoe-mix-0924"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/olmoe-mix-0924
fi

if [ ! -d $INFINIGRAM_ARRAY_DIR/olmoe-adapt ]; then
    echo "creating a link from v4_pileval_llama to olmoe-adapt"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/olmoe-adapt
fi