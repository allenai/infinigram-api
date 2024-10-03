#!/usr/bin/env bash

# Default values
CLUSTER="ai2/jupiter-cirrascale-2"
PRIORITY="high"
WORKSPACE="ai2/hb-wolf-olmo"
BUDGET="ai2/oe-training"

# Parse command line arguments and options
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--cluster)
            CLUSTER="$2"
            shift 2
            ;;
        -w|--workspace)
            WORKSPACE="$2"
            BUDGET="$WORKSPACE"
            shift 2
            ;;
        -p|--priority)
            PRIORITY="$2"
            shift 2
            ;;
        -b|--budget)
            BUDGET="$2"
            shift 2
            ;;
        *)
            if [ -z "$S3_PREFIX" ]; then
                S3_PREFIX="$1"
            elif [ -z "$WEKA_BUCKET" ]; then
                WEKA_BUCKET="$1"
            elif [ -z "$WEKA_PATH" ]; then
                WEKA_PATH="$1"
            else
                echo "Error: Unexpected argument '$1'"
                echo "Usage: $0 <s3-prefix> <weka-bucket> [-c|--cluster <cluster>] [-w|--workspace <workspace>] [-p|--priority <priority>] [-b|--budget <budget>]"
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$S3_PREFIX" ] || [ -z "$WEKA_BUCKET" ] || [ -z "$WEKA_PATH" ]; then
    echo "Error: S3 prefix and Weka bucket are required"
    echo "Usage: $0 <s3-prefix> <weka-bucket> [-c|--cluster <cluster>] [-w|--workspace <workspace>] [-p|--priority <priority>]"
    exit 1
fi

# Shift the parsed options out of the argument list
shift $((OPTIND-1))

# strip trailing slash from S3_PREFIX
S3_PREFIX=$(echo "$S3_PREFIX" | sed 's|/$||')

# create a command to install required packages and the AWS CLI
AWS_CLI_INSTALL_CMD="set -x; \
apt-get update && \
apt-get install -y curl unzip && \
curl \"https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip\" -o \"awscliv2.zip\" && \
unzip awscliv2.zip && \
./aws/install"

WEKA_PREFIX="/${WEKA_BUCKET}/${WEKA_PATH}"

# create a command to sync the S3 prefix to the Weka bucket
SYNC_CMD="/usr/local/bin/aws s3 sync '${WEKA_PREFIX}' '${S3_PREFIX}'"


gantry run \
    --description "Syncing '${WEKA_PREFIX}' to '${S3_PREFIX}'" \
    --allow-dirty \
    --workspace "${WORKSPACE}" \
    --priority "${PRIORITY}" \
    --gpus 8 \
    --preemptible \
    --cluster "${CLUSTER}" \
    --budget "${BUDGET}" \
    --weka "${WEKA_BUCKET}:/${WEKA_BUCKET}" \
    --replicas 10 \
    --host-networking \
    --leader-selection \
    --synchronized-start-timeout 48h \
    --env-secret AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID \
    --env-secret AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY \
    --install "${AWS_CLI_INSTALL_CMD}" \
    --yes \
    -- /bin/bash -c "/usr/local/bin/aws s3 cp --recursive --only-show-errors '${WEKA_PREFIX}' '${S3_PREFIX}' --exclude '*' --include \"*.\$BEAKER_REPLICA_RANK\""