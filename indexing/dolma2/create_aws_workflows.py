import os

output_dir = "aws_workflows"
os.makedirs(output_dir, exist_ok=True)

rank = 22
with open("aws_workflow_template.sh", "r") as f:
    content = f.read()
content = content.replace("[[RANK]]", str(rank))
with open(f"{output_dir}/rank_{rank:04d}.sh", "w") as f:
    f.write(content)
os.chmod(f"{output_dir}/rank_{rank:04d}.sh", 0o755)