# skiff-template-python-api

## Reference
This application is only made possible by researchers working on this paper:
  Liu, Jiacheng and Min, Sewon and Zettlemoyer, Luke and Choi, Yejin and Hajishirzi, Hannaneh (2024).
  Infini-gram: Scaling Unbounded n-gram Language Models to a Trillion Tokens.
  arXiv preprint arXiv:2401.17377,

## Prerequisites

Make sure that you have the latest version of [Docker 🐳](https://www.docker.com/get-started)
installed on your local machine.

## Getting Started

### Installing Dependencies

If you're on a Mac, you won't be able to install the infini-gram library locally. (It'll work in the docker-compose though!) To install other dependencies, install dependencies from `api/requirements/dev-requirements.txt` instead of from `api/requirements.txt`.

`pip install -r requirements/dev-requirements.txt`

### Adding an index for local development

1. Ensure you have the `aws` cli installed. run `brew install awscli` if you don't.
2. Download the `v4_pileval_llama` index by running `./bin/download-infini-gram-array.sh`

The `infinigram-array` folder is mounted to the Docker container for the API through the `docker-compose`. 

## Adding a new infini-gram index

### On the prod server

#### Transferring indexes from AWS

##### Creating Transfer Agents

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

##### Starting the transfer job
  Run this from infinigram-api root folder:
  `./bin/transfer-index-from-s3.sh <S3_SOURCE> <INDEX_NAME>`

  S3_SOURCE will be prefixed with `s3://`
  INDEX_NAME may need to be shortened to fit GCP requirements!

  You may need to restart the transfer agents in the infini-gram-transfer pool: https://console.cloud.google.com/transfer/agent-pools/pool/infini-gram-transfer/agents?project=ai2-reviz


#### Making a Persistent Disk
  Run this from infinigram-api root folder:
  `./bin/create-infini-gram-writer.sh <INDEX_NAME> <INDEX_SIZE> <Optional:INDEX_BUCKET_NAME>`

  INDEX_NAME should match what you used when starting the transfer job
  INDEX_SIZE needs to be at least the space required by the index and uses K8s Quantity unit: https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/quantity/
  INDEX_BUCKET_NAME is optional, it defaults to the INDEX_NAME
  
  When the copy job is finished, run the script to create the readonly volume claim:
  `./bin/create-readonly-volume-claim.sh <INDEX_NAME> <INDEX_SIZE> <Optional:DISK_NAME>`
  
  INDEX_NAME should match what you used when starting the transfer job and making the disk
  INDEX_SIZE should match what you used when starting the transfer job and making the disk
  DISK_NAME is optional, it defaults to 'infinigram-$INDEX_NAME', which the script above creates.
  
  
#### Adding the volume to webapp.jsonnet
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


#### Updating the transfer docker image
If you update the docker image or script we use in the writer job, you'l need to rebuild the image and push it to GCP. 

run this:
`gcloud builds submit --config ./bin/infini-gram-writer/cloudbuild-infini-gram-writer.yaml`

### Locally

1. Add the ID of the index to `AvailableInfiniGramIndexId` in `api/src/infinigram/index_mappings.py`
2. Add the ID as a string to `IndexMappings` in `api/src/infinigram/index_mappings.py`
3. Add the tokenizer and index directory to `index_mappings` in `api/src/infinigram/index_mappings.py`
4. add a line in /bin/download-local-infini-gram-array.sh to make a new symlink with that array's path. The path will be the `index_dir` you added in `index_mappings` but has `/mnt/infinigram-array` replaced with `$INFINIGRAM_ARRAY_DIR`
5. Add a mount in `docker-compose.yaml`: `- ./infinigram-array/<ARRAY_PATH_NAME>:/mnt/infinigram-array/<ARRAY_PATH_NAME>

## Linting and Formatting

If you installed python packages through `dev-requirements.txt` (see #Installing Dependencies) you'll have `Ruff` and `mypy` available to locally check for code quality compliance. 

### CLI
To check for `Ruff` issues, run `ruff check`. If you want to have it automatically fix issues, run `ruff check --fix`. If you want to have it format your code, run `ruff format`.

To check for `mypy` issues, run `mypy --strict --config ./api/pyproject.toml`

### VSCode
Install the [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) and [mypy](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker) extensions. These are listed in the "Recommended Extensions" for the workspace as well.

## Performance Profiling
We have a middleware set up to profile requests with `pyinstrument`. To enable it, you need to have `PROFILING_ENABLED` set to `true` in your env. Then you need to make a request with the query parameter `?profile=true`. If you want to get an HTML formatted profile, also include the query parameter `profile_format=html`.

After the profiling is finished, you can open the performance profile in `/api/performance-profiles/profile.html`

## Checking index sizes in the k8s pod
```
> gcloud container clusters get-credentials skiff-prod --zone us-west1-b --project ai2-reviz && kubectl exec infinigram-api-prod-8586f77768-vl8vr --namespace infinigram-api -c infinigram-api-prod-api --stdin --tty -- /bin/bash

> cd ../mnt/infinigram-array
> ls -l <the index you want to check>
```