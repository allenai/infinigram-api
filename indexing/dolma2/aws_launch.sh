# clone the [olmo-cookbook](https://github.com/allenai/olmo-cookbook) repo, and in the [pmr cli](https://github.com/allenai/olmo-cookbook/blob/main/src/cookbook/cli/pmr.py), change user to ubuntu

export AWS_DEFAULT_REGION=us-east-1
export NAME="infini-gram_dolma2"
poormanray create --name ${NAME} --number 25 --instance-type i7i.48xlarge --detach --ami-id ami-084568db4383264d4 --storage-size 32 # ubuntu
sleep 60
poormanray setup --name ${NAME} # setup AWS credentials
poormanray map --name ${NAME} --script aws_workflows --spindown
