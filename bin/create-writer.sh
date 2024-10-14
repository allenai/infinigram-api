#! /bin/bash

INDEX_NAME=$1
INDEX_SIZE=$2
INDEX_BUCKET_NAME=${3:-$INDEX_NAME}

if [[ -z $INDEX_NAME ]]; then 
    echo "INDEX_NAME is required"
    exit 1
fi

if [[ -z $INDEX_SIZE ]]; then 
    echo "INDEX_SIZE is required"
    exit 1
fi

INDEX_NAME=$INDEX_NAME INDEX_SIZE=$INDEX_SIZE INDEX_BUCKET_NAME=$INDEX_BUCKET_NAME envsubst '$INDEX_NAME:$INDEX_SIZE:$INDEX_BUCKET_NAME' < ./volume-claims/writer-pod.yaml.template | kubectl apply --namespace=infinigram-api -f -