# ltd.noooner.dam.core

Upload, Index, Search and Download endpoints

# Setting up local dev environment

Local dev environment consists of 2 components
* [serverless-wsgi](https://www.serverless.com/plugins/serverless-wsgi) front-end 
* [Localstack](https://github.com/localstack/localstack) backend

### Starting front-end

Serverless WSGI is provided by [Wiren dev environment](https://github.com/jussiheinonen/wiren)

Once Docker image is built you can start the container it by running the command
`sudo docker runc --rm --entrypoint /bin/bash -v $(pwd)/core:/usr/app/core --net=host -it wiren:alpine`

Then start WSGI server
```
cd core
sls wsgi serve
```

### Starting backend

`sudo docker run --rm -v $(pwd):$(pwd) -p 4566:4566 -p 4571:4571 localstack/localstack`

# Command line actions
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
    --table-name users-table-dev \
    --attribute-definitions AttributeName=userId,AttributeType=S \
    --key-schema AttributeName=userId,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --endpoint-url http://localhost:4566
```
### List items in DynamoDB table
```
aws dynamodb scan \
    --table-name ltd.nooonert.dam.core.index.dev \
    --endpoint-url http://localhost:4566
```

### Creating S3 bucket
```
$ aws s3 mb s3://ltd.noooner.dam.core.uploads --endpoint-url http://localhost:4566
make_bucket: ltd.noooner.dam.core.uploads
```

### Copying file to the bucket
```
$ aws s3 cp package.json s3://ltd.noooner.dam.core.uploads --endpoint-url http://localhost:4566
upload: ./package.json to s3://ltd.noooner.dam.core.uploads/package.json 
```

### Listing files in the bucket
```
$ aws s3 ls s3://ltd.noooner.dam.core.uploads --endpoint-url http://localhost:4566
2021-02-24 14:44:00        155 package.json
```



# Credits & ThankU's
* [Localstack](https://github.com/localstack/localstack) test/mocking framework for developing Cloud applications
* [Serverless Framework](https://www.serverless.com/plugins/serverless-wsgi) WSGI server
* [DILLINGER](https://dillinger.io/) markdown editor used to create this very README