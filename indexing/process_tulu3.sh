pip install infini-gram zstandard tqdm transformers sentencepiece awscli

python indexing/transform_hf_to_raw_tulu3.py

cd /weka/oe-training-default/jiachengl/he-infinigram-api/raw
mkdir tulu-3-8b-adapt
cd tulu-3-8b-adapt
ln -s ../tulu-3-sft-mixture/0.jsonl tulu-3-sft-mixture.jsonl
ln -s ../llama-3.1-tulu-3-8b-preference-mixture/0.jsonl llama-3.1-tulu-3-8b-preference-mixture.jsonl
ln -s ../RLVR-GSM-MATH-IF-Mixed-Constraints/0.jsonl RLVR-GSM-MATH-IF-Mixed-Constraints.jsonl
cd ..

mkdir tulu-3-70b-adapt
cd tulu-3-70b-adapt
ln -s ../tulu-3-sft-mixture/0.jsonl tulu-3-sft-mixture.jsonl
ln -s ../llama-3.1-tulu-3-70b-preference-mixture/0.jsonl llama-3.1-tulu-3-70b-preference-mixture.jsonl
ln -s ../RLVR-GSM-MATH-IF-Mixed-Constraints/0.jsonl RLVR-GSM-MATH-IF-Mixed-Constraints.jsonl
cd ..

mkdir tulu-3-405b-adapt
cd tulu-3-405b-adapt
ln -s ../tulu-3-sft-mixture/0.jsonl tulu-3-sft-mixture.jsonl
ln -s ../llama-3.1-tulu-3-405b-preference-mixture/0.jsonl llama-3.1-tulu-3-405b-preference-mixture.jsonl
ln -s ../RLVR-MATH/0.jsonl RLVR-MATH.jsonl
cd ..

cd /opt/miniconda3/lib/python3.10/site-packages/infini_gram

python indexing.py \
    --tokenizer llama --cpus 64 --mem 900 --shards 1 --add_metadata --add_unigram --ulimit 524288 \
    --data_dir /weka/oe-training-default/jiachengl/he-infinigram-api/raw/tulu-3-8b-adapt \
    --save_dir /weka/oe-training-default/jiachengl/he-infinigram-api/index/v4_tulu-3-8b-adapt_llama
aws s3 sync /weka/oe-training-default/jiachengl/he-infinigram-api/index/v4_tulu-3-8b-adapt_llama s3://infini-gram/index/v4_tulu-3-8b-adapt_llama

python indexing.py \
    --tokenizer llama --cpus 64 --mem 900 --shards 1 --add_metadata --add_unigram --ulimit 524288 \
    --data_dir /weka/oe-training-default/jiachengl/he-infinigram-api/raw/tulu-3-70b-adapt \
    --save_dir /weka/oe-training-default/jiachengl/he-infinigram-api/index/v4_tulu-3-70b-adapt_llama
aws s3 sync /weka/oe-training-default/jiachengl/he-infinigram-api/index/v4_tulu-3-70b-adapt_llama s3://infini-gram/index/v4_tulu-3-70b-adapt_llama

python indexing.py \
    --tokenizer llama --cpus 64 --mem 900 --shards 1 --add_metadata --add_unigram --ulimit 524288 \
    --data_dir /weka/oe-training-default/jiachengl/he-infinigram-api/raw/tulu-3-405b-adapt \
    --save_dir /weka/oe-training-default/jiachengl/he-infinigram-api/index/v4_tulu-3-405b-adapt_llama
aws s3 sync /weka/oe-training-default/jiachengl/he-infinigram-api/index/v4_tulu-3-405b-adapt_llama s3://infini-gram/index/v4_tulu-3-405b-adapt_llama
