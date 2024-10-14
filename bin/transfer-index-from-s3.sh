#! /bin/bash

INDEX_SOURCE=$1
INDEX_NAME=$2

if [[ -z $INDEX_SOUCE ]]; then 
    echo "INDEX_SOURCE is required"
    exit 1
fi

if [[ -z $INDEX_NAME ]]; then 
    echo "INDEX_NAME is required"
    exit 1
fi

gcloud transfer jobs create $INDEX_SOURCE gs://infinigram/index/$INDEX_NAME \
    --name=infini-gram-transfer-$INDEX_NAME \
    --source-agent-pool=projects/ai2-reviz/agentPools/infini-gram-transfer \
    --source-endpoint=s3.us-east-1.amazonaws.com