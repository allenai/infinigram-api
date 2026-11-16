# make sure poormanray (https://github.com/allenai/poormanray) is installed before running this
# TODO: I manually patched poormanray to fix some issues with SSH key auth. Need to figure out if those changes were necessary with --ssh-key-path on everything

export AWS_DEFAULT_REGION=us-east-1
export NAME=$1
export SSH_KEY_PATH=$3
poormanray create --name ${NAME}@allennlp-aws --number $2 --instance-type i7i.48xlarge --detach --image ami-084568db4383264d4 --storage-size 32 --ssh-key-path=${SSH_KEY_PATH} # ubuntu
poormanray wait --name ${NAME}@allennlp-aws
poormanray setup --name ${NAME}@allennlp-aws -u ubuntu --ssh-key-path=${SSH_KEY_PATH} # setup AWS credentials
poormanray map --name ${NAME}@allennlp-aws --script aws_workflows --spindown -u ubuntu --ssh-key-path=${SSH_KEY_PATH}
