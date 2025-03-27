
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

  1. Go to the [create a transfer job page](https://console.cloud.google.com/transfer/create?project=ai2-reviz)
  2. Set the Source type to "S3-compatible object storage". Destination type should be "Google Cloud Storage"
  3. Fill in data for the source.
    * Bucket or folder will be the bucket path. If copying from an s3 URL like `s3://infini-gram-lite/index/v4_pileval_llama` you can take off the `s3://` part, resulting in `infini-gram-lite/index/v4_pileval_llama`
    * Endpoint depends on the bucket. Most of the time it'll be `s3.us-east-1.amazonaws.com`
    * Signing region should be the region the bucket is in
  4. The destination should be `infinigram/index/<index name>`
  5. The job should run once, starting now
  6. The rest of the settings can stay the same
    * I do fine it nice to name the transfer job. Something like `infini-gram-transfer-<index name>`
    * Make sure you don't change the Storage class and don't delete from the source

### Making a Persistent Disk
  1. ```
     gcloud compute disks create infini-gram-<index name> \
       --project=ai2-reviz \
       --type=pd-balanced \
       --size=<index size in GB> \
       --labels=project=infini-gram \
       --zone=us-west1-b
       ```
  2. Change names in `volume-claims/writer-pod.yaml` to match the disk you created and the index name
  3. Create a writer pod: `kubectl apply -f volume-claims/writer-pod.yaml --namespace=infinigram-api`
    * (TODO) Set up a baseline image to use for transferring files. Needs to have python3 and gcloud tools
  4. connect to the pod and set it up with python3 and gcloud
    * kubectl exec --stdin --tty infini-gram-writer --namespace=infinigram-api -- /bin/ash
    * apk add python3 curl which bash
    * curl -sSL https://sdk.cloud.google.com | bash
    * bash
  4. Download the files from the bucket into /mnt/infini-gram-array
    * `gcloud storage cp gs://infinigram/index/<index name>/* /mnt/infini-gram-array/`

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