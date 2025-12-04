NUM_SHARDS=1
NUM_NODES=1
RANK=[[RANK]]
REMOTE_DIR=[[REMOTE_DIR]]

set -e
set -x
exec > >(tee -a ~/script_log.txt) 2>&1

# Mount volumes
echo "Mount volumes: Starting ..."
# Dynamically find the first 8 devices with size 3.4T
DEVICES=($(lsblk -o NAME,SIZE -dn | awk '$2 == "3.4T" {print $1}' | head -8))
if [ ${#DEVICES[@]} -lt 8 ]; then
    echo "Error: Less than 8 NVMe devices with size 3.4T found."
    exit 1
fi
for i in ${!DEVICES[@]}; do
    DEVICE="/dev/${DEVICES[$i]}"
    if [ $i -eq 0 ]; then
        MOUNT_POINT="/data_c"
    elif [ $i -eq 1 ]; then
        MOUNT_POINT="/data_t"
    elif [ $i -eq 2 ]; then
        MOUNT_POINT="/data_i"
    else
        continue
    fi
    sudo mkfs -t ext4 $DEVICE
    sudo mkdir -p $MOUNT_POINT
    sudo mount $DEVICE $MOUNT_POINT
    sudo chown $USER:$USER $MOUNT_POINT
done
echo "Mount volumes: Done"
echo "================================================"

# Clone repo
echo "Clone repo: Starting ..."
git clone https://github.com/allenai/infinigram-api.git -b dolma2
cd infinigram-api/indexing/dolma2
echo "Clone repo: Done"
echo "================================================"

# Install conda
echo "Install conda: Starting ..."
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh --quiet
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
# NEED TO FIGURE OUT A WAY TO AUTO ACCEPT THE TOS
rm -rf ~/miniconda3/miniconda.sh
# ~/miniconda3/bin/conda init bash
# source /home/ubuntu/.bashrc
eval "$(~/miniconda3/bin/conda 'shell.bash' 'hook' 2> /dev/null)"
conda config --system --remove channels defaults || true
conda config --system --add channels conda-forge
conda config --system --set channel_priority strict
conda env create -f environment.yml -y
conda activate he-indexing-dolma2
pip install datasets transformers tokenizers sentencepiece
wget https://github.com/peak/s5cmd/releases/download/v2.2.2/s5cmd_2.2.2_Linux-64bit.tar.gz
mkdir -p s5cmd_2.2.2
tar -xvzf s5cmd_2.2.2_Linux-64bit.tar.gz -C s5cmd_2.2.2
sudo mv s5cmd_2.2.2/s5cmd /usr/local/bin
rm -r s5cmd_2.2.2
rm s5cmd_2.2.2_Linux-64bit.tar.gz
echo "Install conda: Done"
echo "================================================"

# Set cache directories to larger volume
export HF_HOME="/data_t/hf_home"
export HF_DATASETS_CACHE="/data_t/hf_cache"
export TMPDIR="/data_t/tmp"
mkdir -p $HF_HOME
mkdir -p $HF_DATASETS_CACHE
mkdir -p $TMPDIR

# Run workflow
echo "Prepare data: Starting ..."
# Ensure the transform script is available.
mkdir -p /data_c/raw
time python ../transform_hf_to_raw_dolci.py --output_dir /data_c/raw
echo "Prepare data: Done"

DATASETS=("Dolci-Think-SFT-7B" "Dolci-Think-SFT-32B" "Dolci-Instruct-SFT-7B")

for DS_NAME in "${DATASETS[@]}"; do
    echo "Indexing $DS_NAME: Starting ..."
    INDEX_NAME="v6_${DS_NAME}_u32"
    
    time python indexing_v6.py --data_dir "/data_c/raw/${DS_NAME}" --temp_dir "/data_t/${INDEX_NAME}" --save_dir "/data_i/${INDEX_NAME}" --token_dtype u32 --cpus 192 --mem 1800 --add_metadata --tokenizer "allenai/dolma2-tokenizer"
    
    echo "Upload data: Starting ..."
    time s5cmd cp -sp "/data_i/${INDEX_NAME}/*" "${REMOTE_DIR}/${DS_NAME}/"
    echo "Upload data: Done"
    echo "------------------------------------------------"
    
    # Cleanup to save space? These are small, so maybe not needed.
    # rm -r /data_t/${INDEX_NAME}
    # rm -r /data_i/${INDEX_NAME}
done

screen -X hardcopy -h ~/screen_output.txt
echo "All Done"

