# ltd.noooner.dam.core

Upload, Index, Search and Download endpoints

# Setting up local dev environment

Local dev environment consists of 2 components
* [serverless-wsgi](https://www.serverless.com/plugins/serverless-wsgi) front-end 
* [Localstack](https://github.com/localstack/localstack) backend

## Starting front-end

Serverless WSGI is provided by [Wiren dev environment](https://github.com/jussiheinonen/wiren)

Once Docker image is built you can start the container it by running the command

`sudo docker run --rm --entrypoint /bin/bash -v $(pwd)/core:/usr/app/core --net=host -it wiren:alpine`

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

### Start WSGI server
```
cd core
sls wsgi serve
```

## Starting backend

`sudo docker run --rm -p 4566:4566 -p 4571:4571 localstack/localstack`

# Command line actions

## CURL

Example commands on how to interact with API using curl

### Uploading a file

`curl -i -X POST -F file=@core/uploads/elisa.jpg http://localhost:5000/upload`

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

### List items in DynamoDB table based on keyword
```
$ aws dynamodb scan \
    --table-name ${INDEX_TABLE} \
    --filter-expression 'contains(keywords,:key)' \
    --expression-attribute-values '{":key":{"S":"Toyota"}}' \
    --endpoint-url http://localhost:4566
```

### List select fields in DynamoDB table based on keyword
```
$ aws dynamodb scan \
    --table-name ${INDEX_TABLE} \
    --projection-expression "headline,original_filename" \
    --filter-expression 'contains(keywords,:key)' \
    --expression-attribute-values '{":key":{"S":"Toyota"}}' \
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



# Credits & ThankU's
* [Localstack](https://github.com/localstack/localstack) test/mocking framework for developing Cloud applications
* [Serverless Framework](https://www.serverless.com/plugins/serverless-wsgi) WSGI server
* [DILLINGER](https://dillinger.io/) markdown editor used to create this very README