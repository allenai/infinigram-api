# Dolma2 indexing (aka Dolma3)

1. make a file like `indexing/dolma2/dolma2-0625-v01.csv` (example script `python scripts/generate_dolma3_csv.py --output indexing/dolma2/dolma3-dolmino-official-100b.csv --prefix s3://ai2-llm/preprocessed/dolma3-dolmino-official/100B-v2/`)
2. `python make_s5cmd_files.py --csv-path dolma3-dolmino-official-100b.csv --output-dir s5cmd_files_dolmino`
3. `python create_aws_workflows.py --num-nodes 1 --remote-dir "s3://infini-gram/index/dolma3-dolmino-official-100B" --s5cmd-files-dir s5cmd_files_dolmino` (adust num ranks as needed) and push these to git
4. `source aws_launch.sh dolma3-indexing 1`
5. progress monitoring `poormanray run --name ${NAME} --command 's=$(screen -ls 2>/dev/null | awk "/Detached|Attached/{print \$1}" | tail -n1); [ -n "$s" ] && screen -r "$s" -X hardcopy -h /tmp/screen.out && tail -n 200 /tmp/screen.out || echo "no screen session"'`
6. dump log when done `poormanray run --name ${NAME} --command 'tail -n 10 ~/screen_output.txt' > my_logs.log`
6. when finished `poormanray terminate --name ${NAME} --region us-east-1 --detach`

## Dolci SFT Indexing

To index the Dolci SFT datasets (7B/32B/Instruct):

1. Generate the AWS workflow scripts (make sure you have committed `indexing/transform_hf_to_raw_dolci.py`):
   ```bash
   python create_aws_workflows.py --dolci --remote-dir s3://infini-gram/index/dolci
   ```
2. Launch the job (1 node):
   ```bash
   source aws_launch.sh dolci-indexing 1
   ```
3. Monitor progress:
   ```bash
   poormanray run --name ${NAME} --command 's=$(screen -ls 2>/dev/null | awk "/Detached|Attached/{print \$1}" | tail -n1); [ -n "$s" ] && screen -r "$s" -X hardcopy -h /tmp/screen.out && tail -n 200 /tmp/screen.out || echo "no screen session"'
   ```
