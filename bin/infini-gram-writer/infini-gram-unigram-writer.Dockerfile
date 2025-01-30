FROM google/cloud-sdk:alpine

ARG INDEX_NAME
ENV INDEX_NAME ${INDEX_NAME}

COPY ./bin/infini-gram-writer/copy-infini-gram-unigrams.sh ./copy-infini-gram-unigrams.sh

CMD ["./copy-infini-gram-unigrams.sh"]