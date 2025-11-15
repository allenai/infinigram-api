#! /bin/bash

declare -a shards=("00" "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" "13" "14" "15" "16" "17" "18")

for shard in "${shards[@]}"
do
   gcloud storage cp -r "gs://infinigram/index/dolma2-0625-v01/${shard}/" "gs://infinigram/index/v6-dolma2-0625-v01-7b/${shard}"
    
done