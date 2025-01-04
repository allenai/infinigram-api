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

if [ ! -d $INFINIGRAM_ARRAY_DIR/olmoe-mix-0924-dclm ]; then
    echo "creating a link from v4_pileval_llama to olmoe-mix-0924-dclm"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/olmoe-mix-0924-dclm
fi

if [ ! -d $INFINIGRAM_ARRAY_DIR/olmoe-mix-0924-nodclm ]; then
    echo "creating a link from v4_pileval_llama to olmoe-mix-0924-nodclm"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/olmoe-mix-0924-nodclm
fi

if [ ! -d $INFINIGRAM_ARRAY_DIR/v4-ultrafeedback ]; then
    echo "creating a link from v4_pileval_llama to v4-ultrafeedback"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/v4-ultrafeedback
fi

if [ ! -d $INFINIGRAM_ARRAY_DIR/v4-tulu-v3-1-mix ]; then
    echo "creating a link from v4_pileval_llama to v4-tulu-v3-1-mix"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/v4-tulu-v3-1-mix
fi

if [ ! -d $INFINIGRAM_ARRAY_DIR/v4-olmo-2-1124-13b-anneal-adapt ]; then
    echo "creating a link from v4_pileval_llama to v4-olmo-2-1124-13b-anneal-adapt"
    ln -s $INFINIGRAM_ARRAY_DIR/v4_pileval_llama $INFINIGRAM_ARRAY_DIR/v4-olmo-2-1124-13b-anneal-adapt
fi