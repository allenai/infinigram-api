FROM google/cloud-sdk:alpine

ARG INDEX_NAME
ENV INDEX_NAME ${INDEX_NAME}

COPY ./bin/infini-gram-writer/copy-infini-gram-array.sh ./copy-infini-gram-array.sh

CMD ["./copy-infini-gram-array.sh"]