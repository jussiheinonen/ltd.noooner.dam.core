#!/usr/bin/env bash
#
# Set environment variables based on user input or defaults
# 
# USAGE: to set variables in current PID it must be sourced: source ./setenv-index.sh

declare -A SETTINGS TMP_SETTINGS

SETTINGS[INDEX_TABLE]="ltd.noooner.dam.core" 
SETTINGS[BUCKET_NAME]="ltd.noooner.dam.core" 
SETTINGS[IS_OFFLINE]="true"


read -p "DynamoDB table name for Index data? [default: ${SETTINGS[INDEX_TABLE]}] " TMP_SETTINGS[INDEX_TABLE]
read -p "S3 bucket name? [default: ${SETTINGS[BUCKET_NAME]}] " TMP_SETTINGS[BUCKET_NAME]
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
export BUCKET_NAME=${SETTINGS[BUCKET_NAME]}
export IS_OFFLINE=${SETTINGS[IS_OFFLINE]}



