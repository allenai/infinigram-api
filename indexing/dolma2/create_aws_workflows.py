import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--num-nodes", type=int, default=1)
parser.add_argument("--remote-dir", type=str, default="s3://infini-gram/index/dolma2-0625-v02")
args = parser.parse_args()

num_nodes = args.num_nodes
output_dir = "aws_workflows"
remote_dir = args.remote_dir
os.makedirs(output_dir, exist_ok=True)

for rank in range(num_nodes):
    with open(f"aws_workflow_template.sh", "r") as f:
        content = f.read()
    content = content.replace("[[RANK]]", str(rank))
    content = content.replace("[[REMOTE_DIR]]", remote_dir)
    with open(f"{output_dir}/rank_{rank:04d}.sh", "w") as f:
        f.write(content)
    os.chmod(f"{output_dir}/rank_{rank:04d}.sh", 0o755)