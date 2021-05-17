#!/usr/bin/env bash
#
# Set environment variables based on user input or defaults
# 
# USAGE: to set variables in current PID it must be sourced: source ./setenv-index.sh

declare -A SETTINGS TMP_SETTINGS

export DIRNAME="$(dirname $0)"

usage() {
    echo "USAGE: source $0"
}

if [[ "$$" -ne "1" ]]; then
    echo "Source this script instead of running in subshell"
    usage
    exit 1
fi

SETTINGS[INDEX_TABLE]="ltd.noooner.dam.core.index" 
SETTINGS[UPLOAD_BUCKET]="ltd.noooner.dam.core.upload"
SETTINGS[DOWNLOAD_BUCKET]="ltd.noooner.dam.core.download"
SETTINGS[THUMBNAIL_BUCKET]="ltd.noooner.dam.core.thumbnails"
SETTINGS[PRESIGN_ENDPOINT_URL]="https://tm7do0vu9j.execute-api.eu-west-1.amazonaws.com/presign"
SETTINGS[IS_OFFLINE]="true"


read -p "DynamoDB table name for Index data? [default: ${SETTINGS[INDEX_TABLE]}] " TMP_SETTINGS[INDEX_TABLE]
read -p "S3 bucket name for UPLOAD? [default: ${SETTINGS[UPLOAD_BUCKET]}] " TMP_SETTINGS[UPLOAD_BUCKET]
read -p "S3 bucket name for DOWNLOAD? [default: ${SETTINGS[DOWNLOAD_BUCKET]}] " TMP_SETTINGS[DOWNLOAD_BUCKET]
read -p "S3 bucket name for THUMBNAILS? [default: ${SETTINGS[THUMBNAIL_BUCKET]}] " TMP_SETTINGS[THUMBNAIL_BUCKET]
read -p "Presign URL endpoint? [default: ${SETTINGS[PRESIGN_ENDPOINT_URL]}] " TMP_SETTINGS[PRESIGN_ENDPOINT_URL]
read -p "Using LocalStack for backend services? [default: ${SETTINGS[IS_OFFLINE]}] " TMP_SETTINGS[IS_OFFLINE]

for each in ${!SETTINGS[*]}; do
    if [[ "${TMP_SETTINGS[${each}]}" == "${SETTINGS[${each}]}" || "${TMP_SETTINGS[${each}]}" == ""  ]]; then
        echo "Setting default ${each} ${SETTINGS[${each}]}"
    else
        echo "Setting CUSTOM ${each} ${TMP_SETTINGS[${each}]}"
        SETTINGS[${each}]="${TMP_SETTINGS[${each}]}"
    fi
done

export INDEX_TABLE=${SETTINGS[INDEX_TABLE]}
export UPLOAD_BUCKET=${SETTINGS[UPLOAD_BUCKET]}
export DOWNLOAD_BUCKET=${SETTINGS[DOWNLOAD_BUCKET]}
export THUMBNAIL_BUCKET=${SETTINGS[THUMBNAIL_BUCKET]}
export PRESIGN_ENDPOINT_URL=${SETTINGS[PRESIGN_ENDPOINT_URL]}
export IS_OFFLINE=${SETTINGS[IS_OFFLINE]}

if [[ "${SETTINGS[IS_OFFLINE]}" == "true" ]]; then # Only ask to set up Localstack resources if working in isolation
    read -p "Create LocalStack resources? [y/n]" localstack
    if [[ "${localstack}" == "y" ]]; then
        source $(find ../ -name localstack-resources.sh)
    else
        echo "Skipping LocalStack resource creations"
    fi
fi
