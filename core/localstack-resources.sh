#!/usr/bin/env bash
#
# Create localstack resources for local development
# 
# USAGE: This script is sourced from setenv.sh https://github.com/jussiheinonen/ltd.noooner.dam.core/blob/main/core/setenv.sh
#        Script can be called directly from CLI assuming environment variables are set.

awsConfig() {
    test -d ${HOME}/.aws || mkdir -p ${HOME}/.aws
    echo '[default]' > ${HOME}/.aws/config
    echo 'region = localhost' >> ${HOME}/.aws/config
}

awsCredentials() {
    echo '[default]' > ${HOME}/.aws/credentials
    echo 'aws_access_key_id = whatever' >> ${HOME}/.aws/credentials
    echo 'aws_secret_access_key = whatever' >> ${HOME}/.aws/credentials
}

createIndexTable() {
    aws dynamodb create-table \
    --table-name ${INDEX_TABLE} \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --endpoint-url http://localhost:4566
}

createBucket() {
    for each in $*; do
        aws s3 mb s3://${each} --endpoint-url http://localhost:4566
    done
}
if [[ -f ${HOME}/.aws/credentials ]]; then
    read -p "WARNING! ${HOME}/.aws/credentials already exist. Overwrite ? [y/n]" overwrite
fi
if [[ "${overwrite}" == "y" ]]; then
    awsConfig
    awsCredentials
else
    echo "Skipping aws cli config"
fi

createIndexTable
createBucket "${UPLOAD_BUCKET}" "${DOWNLOAD_BUCKET}"

