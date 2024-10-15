#! /bin/bash

INDEX_NAME=$1
INDEX_SIZE=$2
INDEX_BUCKET_NAME=${3:-$INDEX_NAME}
DISK_NAME=${4:-infinigram-$INDEX_NAME}

if [[ -z $INDEX_NAME ]]; then 
    echo "INDEX_NAME is required"
    exit 1
fi

if [[ -z $INDEX_SIZE ]]; then 
    echo "INDEX_SIZE is required"
    exit 1
fi

echo "Creating disk $DISK_NAME"
gcloud compute disks create $DISK_NAME \
    --project=ai2-reviz \
    --type=pd-balanced \
    --size=$INDEX_SIZE \
    --labels=project=infini-gram \
    --zone=us-west1-b

echo "Creating writer job for $INDEX_NAME"
# we use envsubst to replace variables in the kubectl yaml template
INDEX_NAME=$INDEX_NAME \
 INDEX_SIZE=$INDEX_SIZE \
 INDEX_BUCKET_NAME=$INDEX_BUCKET_NAME \
 DISK_NAME=$DISK_NAME \
 envsubst '$INDEX_NAME:$INDEX_SIZE:$INDEX_BUCKET_NAME:$DISK_NAME' < ./bin/infini-gram-writer/writer-job.yaml.template | kubectl apply --namespace=infinigram-api -f -

