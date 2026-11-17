#! /bin/bash

INDEX_NAME=$1
INDEX_SIZE=$2
DISK_NAME=${3:-infinigram-$INDEX_NAME}

if [[ -z $INDEX_NAME ]]; then 
    echo "INDEX_NAME is required"
    exit 1
fi

if [[ -z $INDEX_SIZE ]]; then 
    echo "INDEX_SIZE is required"
    exit 1
fi

VOLUME_CLAIM_YAML_FILE=./infra/k8s/volumes/$INDEX_NAME.yaml

INDEX_NAME=$INDEX_NAME INDEX_SIZE=$INDEX_SIZE DISK_NAME=$DISK_NAME envsubst '$INDEX_NAME:$INDEX_SIZE:$INDEX_BUCKET_NAME:$DISK_NAME' < ./volume-claims/volume-claim.yaml.template > $VOLUME_CLAIM_YAML_FILE

cd ./infra/k8s/volumes
kustomize edit add resource $INDEX_NAME.yaml