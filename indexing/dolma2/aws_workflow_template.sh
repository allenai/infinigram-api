INSTANCE_TYPE="i7i"
NUM_SHARDS=25
NUM_NODES=25
RANK=0
REMOTE_DIR="s3://infini-gram/index/dolma2-0625-v01"

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
rm -rf ~/miniconda3/miniconda.sh
# ~/miniconda3/bin/conda init bash
# source /home/ubuntu/.bashrc
eval "$(~/miniconda3/bin/conda 'shell.bash' 'hook' 2> /dev/null)"
conda env create -f environment.yml
conda activate he-indexing-dolma2
wget https://github.com/peak/s5cmd/releases/download/v2.2.2/s5cmd_2.2.2_Linux-64bit.tar.gz
mkdir -p s5cmd_2.2.2
tar -xvzf s5cmd_2.2.2_Linux-64bit.tar.gz -C s5cmd_2.2.2
sudo mv s5cmd_2.2.2/s5cmd /usr/local/bin
rm -r s5cmd_2.2.2
rm s5cmd_2.2.2_Linux-64bit.tar.gz
echo "Install conda: Done"
echo "================================================"

# # Compile things
# echo "Compile things: Starting ..."
# cp ~/miniconda3/envs/hg-dedup/lib/python3.12/site-packages/infini_gram/rust_indexing .
# c++ -std=c++20 -O3 -shared -fPIC $(python3 -m pybind11 --includes) cpp_engine_dedup.cpp -o cpp_engine_dedup$(python3-config --extension-suffix)
# echo "Compile things: Done"
# echo "================================================"

# Run workflow
for ((shard=$RANK; shard<$NUM_SHARDS; shard+=$NUM_NODES)); do

    echo "Run workflow for shard $shard: Starting ..."
    export NAME=$(printf "%02d" $shard)
    export INDEX_NAME="v6_${NAME}_u32"

    echo "Download data: Starting ..."
    time s5cmd run ./s5cmd_files/${NAME}.s5cmd
    time python make_raw_s5cmd_file.py
    time s5cmd run ./s5cmd_files/raw.s5cmd
    echo "Download data: Done"
    echo "------------------------------------------------"

    echo "Indexing: Starting ..."
    time python indexing_v6.py --data_dir /data_c/tokenized --temp_dir /data_t/${INDEX_NAME} --save_dir /data_i/${INDEX_NAME} --pretokenized --token_dtype u32 --cpus 192 --num_batches 16 --add_metadata
    echo "Indexing: Done"
    echo "------------------------------------------------"

    echo "Upload data: Starting ..."
    time s5cmd cp -sp /data_i/${INDEX_NAME} ${REMOTE_DIR}/${NAME}
    echo "Upload data: Done"
    echo "------------------------------------------------"

    rm -r /data_c/tokenized
    rm -r /data_c/raw
    rm -r /data_t/${INDEX_NAME}
    rm -r /data_i/${INDEX_NAME}
    echo "Run workflow for shard $shard: Done"
    echo "================================================"

done
