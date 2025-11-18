#! /bin/bash

declare -a shards=("19" "21" "22" "23")

for shard in "${shards[@]}"
do
    files=($(gcloud storage ls "gs://infinigram/index/dolma2-0625-v01/${shard}"))

    suffix=($((10#${shard})))

    for file in "${files[@]}"
    do
        basename=$(basename ${file})
        name_with_suffix="$basename.$suffix"

        gcloud storage cp $file "gs://infinigram/index/dolma2-0625-v01-7b/$name_with_suffix"
    done
    
done