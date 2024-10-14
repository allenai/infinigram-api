
# Adding a new infini-gram index

## On the prod server

### Transferring indexes from AWS

#### Creating Agents

1. Create VMs in google compute engine
  * Google recommends 4vCPU and 8GB of memory per agent. Three VMs with the appropriate specs seems to be the most cost-effective
  * Example gcloud command:
    ```
    gcloud compute instances create infini-gram-transfer-agent-1 \
      --project=ai2-reviz \
      --zone=us-west1-a \
      --machine-type=n2-standard-4 \
      --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=main \
      --maintenance-policy=MIGRATE \
      --provisioning-model=STANDARD \
      --service-account=infini-gram-transfer@ai2-reviz.iam.gserviceaccount.com \
      --scopes=https://www.googleapis.com/auth/cloud-platform \
      --create-disk=auto-delete=yes,boot=yes,device-name=instance-20240716-154927,image=projects/debian-cloud/global/images/debian-12-bookworm-v20240709,mode=rw,size=10,type=projects/ai2-reviz/zones/us-west1-a/diskTypes/pd-balanced \
      --no-shielded-secure-boot \
      --shielded-vtpm \
      --shielded-integrity-monitoring \
      --labels=name=infini-gram-transfer-agent-1,project=infini-gram,goog-ec-src=vm_add-gcloud \
      --reservation-affinity=any
    ```
2. Upload your SSH key to the VMs
3. Copy the infini-gram service account json to the vm: `scp -i <your private ssh key location> ./infini-gram-transfer-account.json taylorb@10.115.0.81:~`
4. SSH into the VM: `ssh <VM IP>`
5. Set up the agent and attach it to the agent pool
  *  Run these commands, replacing values where needed:
      ```
      export AWS_ACCESS_KEY_ID=<AWS_ACCES_KEY_ID>
      export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
      curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo systemctl enable docker
      gcloud transfer agents install --pool=infini-gram-transfer  \
        --creds-file=~/infini-gram-transfer-account.json
      ```

#### Starting the transfer job
  Run this from infinigram-api root folder:
  `./bin/transfer-index-from-s3.sh <S3_SOURCE> <INDEX_NAME>`

  S3_SOURCE will be prefixed with `s3://`
  INDEX_NAME may need to be shortened to fit GCP requirements!

  You may need to restart the transfer agents in the infini-gram-transfer pool: https://console.cloud.google.com/transfer/agent-pools/pool/infini-gram-transfer/agents?project=ai2-reviz

### Making a Persistent Disk
  Run this from infinigram-api root folder:
  `./bin/create-infini-gram-writer.sh <INDEX_NAME> <INDEX_SIZE> <Optional:INDEX_BUCKET_NAME>`

  INDEX_NAME should match what you used when starting the transfer job
  INDEX_SIZE needs to be at least the space required by the index and uses K8s Quantity unit: https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/quantity/
  INDEX_BUCKET_NAME is optional, it defaults to the INDEX_NAME

### Adding the volume to webapp.jsonnet
  1. Add a volume to the deployment
     ```
      {
        name: "infinigram-array-<ARRAY_NAME>>",
        persistentVolumeClaim: {
            claimName: "infinigram-<ARRAY_NAME>",
            readOnly: true,
        }
      }
     ```
  2. Add a volumeMount to the -api container
     ```
      {
          mountPath: "/mnt/infinigram-array/<VOLUME_NAME>",
          name: "infinigram-array-<ARRAY_NAME>",
          readOnly: true,
      }
     ```

## Locally

1. Add the ID of the index to `AvailableInfiniGramIndexId` in `api/src/infinigram/index_mappings.py`
2. Add the ID as a string to `IndexMappings` in `api/src/infinigram/index_mappings.py`
3. Add the tokenizer and index directory to `index_mappings` in `api/src/infinigram/index_mappings.py`
4. add a line in /bin/download-infini-gram-array.sh to make a new symlink with that array's path. The path will be the `index_dir` you added in `index_mappings` but has `/mnt/infinigram-array` replaced with `$INFINIGRAM_ARRAY_DIR`
5. Add a mount in `docker-compose.yaml`: `- ./infinigram-array/<ARRAY_PATH_NAME>:/mnt/infinigram-array/<ARRAY_PATH_NAME>