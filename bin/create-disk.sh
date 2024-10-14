#! /bin/bash

INDEX_NAME=$1
INDEX_SIZE=$2

if [[ -z $INDEX_NAME ]]; then 
    echo "INDEX_NAME is required"
    exit 1
fi

if [[ -z $INDEX_SIZE ]]; then 
    echo "INDEX_SIZE is required"
    exit 1
fi

gcloud compute disks create infinigram-$INDEX_NAME \
    --project=ai2-reviz \
    --type=pd-balanced \
    --size=$INDEX_SIZE \
    --labels=project=infini-gram \
    --zone=us-west1-b