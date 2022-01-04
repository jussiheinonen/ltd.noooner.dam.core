# ltd.noooner.dam.core

Upload, Index, Search and Download endpoints

# Setting up local dev environment

Local dev environment consists of 2 components

* [Wiren](https://github.com/jussiheinonen/wiren) front-end
* [Localstack](https://github.com/localstack/localstack) backend

## Starting front-end

`core/docker_run.sh` + select option 2.


### Set environment variables

```
$ source core/setenv.sh
DynamoDB table name for Index data? [default: ltd.noooner.dam.core]  
S3 bucket name? [default: ltd.noooner.dam.core] 
Using LocalStack for backend services? [default: true] 
Setting default INDEX_TABLE ltd.noooner.dam.core
Setting default IS_OFFLINE true
Setting default BUCKET_NAME ltd.noooner.dam.core
```

## Starting backend

`core/docker_run.sh` + select option 1.

# Command line actions

## CURL

Example commands on how to interact with API using curl

### Uploading and indexing a file

On Wiren dev runtime...
```
cd core/index
./index-invoke.py --filename ../uploads/${file}

```

## AWS CLI

A list of commands to manage LocalStack resources using `aws` command line utility

First of all set up AWS credentials file for localhost activity
```
$ aws configure
AWS Access Key ID [None]: test
AWS Secret Access Key [None]: test
Default region name [None]: localhost
Default output format [None]: 
```

### Creating DynamoDB table
```
$ aws dynamodb create-table \
    --table-name ${INDEX_TABLE} \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --endpoint-url http://localhost:4566
```

### Deleting DynamoDB table
```
$ aws dynamodb delete-table \
    --table-name ${INDEX_TABLE} \
    --endpoint-url http://localhost:4566
```

### List all items in DynamoDB table
```
$ aws dynamodb scan \
    --table-name ${INDEX_TABLE} \
    --endpoint-url http://localhost:4566
```

### List items in DynamoDB table based on field n_search
```
$ aws dynamodb scan \
    --table-name ${INDEX_TABLE} \
    --filter-expression 'contains(n_search,:key)' \
    --expression-attribute-values '{":key":{"S":"madrid"}}' \
    --endpoint-url http://localhost:4566
```

### List select fields in DynamoDB table based on field n_search
```
$ aws dynamodb scan \
    --table-name ${INDEX_TABLE} \
    --projection-expression "id, n_search, headline,original_filename" \
    --filter-expression 'contains(n_search,:key)' \
    --expression-attribute-values '{":key":{"S":"madrid"}}' \
    --endpoint-url http://localhost:4566
```

### List items newer than 10 minutes

Field upload_time indicates Unix time when item was added to the database.

```
# Show Unix time 10 minutes ago
$ expr $(date +%s) - 600
1618570726
```
Specify Unix time in --expression-attribute-value
```
aws dynamodb scan \
    --table-name ${INDEX_TABLE} \
    --projection-expression "id, upload_time, original_filename" \
    --filter-expression 'upload_time >= :t' \
    --expression-attribute-values '{":t":{"N":"1618570726"}}' \
    --endpoint-url http://localhost:4566
```

### Creating S3 bucket
```
$ aws s3 mb s3://${BUCKET_NAME} --endpoint-url http://localhost:4566
make_bucket: ltd.noooner.dam.core.dev
```

### Deleting S3 bucket, with force
```
aws s3 rb --force s3://${BUCKET_NAME} --endpoint-url http://localhost:4566
```

### Copying file to the bucket
```
$ aws s3 cp package.json s3://${BUCKET_NAME} --endpoint-url http://localhost:4566
upload: ./package.json to s3://ltd.noooner.dam.core.dev/package.json 
```

### Listing files in the bucket
```
$ aws s3 ls s3://${BUCKET_NAME} --endpoint-url http://localhost:4566
2021-02-24 14:44:00        155 package.json
```

### Copy objects between buckets

```
$ aws s3 sync s3://ltd.noooner.dam.core.download.ltd-noooner-index s3://ltd.noooner.dam.core.upload.ltd-noooner-index
```

# Credits & ThankU's
* [Localstack](https://github.com/localstack/localstack) test/mocking framework for developing Cloud applications
* [Serverless Framework](https://www.serverless.com/plugins/serverless-wsgi) WSGI server
* [DILLINGER](https://dillinger.io/) markdown editor used to create this very README