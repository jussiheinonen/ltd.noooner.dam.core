# Noooner DAM Core API documentation

API documentation is based on [OpenAPI v3.0.3](https://spec.openapis.org/oas/v3.0.3) specification in YAML format.

Documentation lives in the file [documentation / openapi.yaml](https://github.com/jussiheinonen/ltd.noooner.dam.core/blob/main/documentation/openapi.yaml)

## Scope

Documentation is limited to publicly accessible endpoints in ltd.noooner.dam.core stack. 

### Presign API  
### ...for Uploading and Downloading files
Endpoint URL: https://tm7do0vu9j.execute-api.eu-west-1.amazonaws.com

##### Description
Name Presign API derives from AWS concept called [presigned URL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html). 
Presigned URL in the Noooner DAM stack is used for uploading images into the system as well as taking images out of the system by downloading them.
In other words, Noooner DAM stack _does not_ have dedicated APIs for uploads and downloads. 
Instead, upload and download functionalities are enabled by Presign API.

##### HTTP methods

Supported methods to request presigned url are GET and POST.

###### GET example

Upload URL: `/presign?filename=noooner_m.png&action=put_object`
Download URL: `/presign?filename=noooner_m.png&action=get_object`

###### POST example

```
# Upload URL
/presign -d \
{
    "filename": "noooner_m.png",
    "action": "put_object"
}

# Download URL
/presign -d \
{
    "filename": "noooner_m.png",
    "action": "get_object"
}
```

##### Uploading an image

Uploading an image involves 2 requests

 1. Requesting upload URL from the Presign API
 2. Uploading image directly to S3 using the upload URL

Requests paramaters and responses are described more in detail in [documentation / openapi.yaml](https://github.com/jussiheinonen/ltd.noooner.dam.core/blob/main/documentation/openapi.yaml).

For quick exploration here is an upload example using cUrl

``` 
# Get presigned upload URL (action=put_object) for file noooner_m.png (filename=noooner_m.png)
  curl -s 'https://tm7do0vu9j.execute-api.eu-west-1.amazonaws.com/presign?filename=noooner_m.png&action=put_object'
 
# Make note of the upload URL included in the response field as it's needed in the next step
# {"response": "https://s3.eu-west-1.amazonaws.com/ltd.noooner.dam.core.upload.ltd-noooner-index/noooner_m.png?AWSAccessKeyId=A....

# Uploading image noooner_m.png 
  curl -X PUT -T noooner_m.png 'https://s3.eu-west-1.amazonaws.com/ltd.noooner.dam.core.upload.ltd-noooner-index/noooner_m.png?AWSAccessKeyId=A
```

##### Downloading an image

Downloading image is a nearly idendtical process to uploading image

 1. Requesting dwonload URL from the Presign API
 2. Downloading image directly from S3 using the download URL

The only difference in request sent to Presign API is the _action_ parameter that has value _get_object_ (put_object action is used for upload)

The easiest way to experiment with download functionality is via Search API. Search results returned by Search API include attribute _get_download_url_ which is a the URL for Presign API to request download URL of an image.

### Search API
#### ...for Searching images
Endpoint URL: https://yibz2ntz2d.execute-api.eu-west-1.amazonaws.com

##### Description
Search API is used for searching image metadata. Request parameter `q=` specifices a list of keywords that is compared to image metadata. Images matching keywords are included in the results set that is returned to client. 

##### HTTP methods
Supported method is GET. 

##### Example Search API request

[https://yibz2ntz2d.execute-api.eu-west-1.amazonaws.com/search?q=real+madrid+champions+league+football](https://yibz2ntz2d.execute-api.eu-west-1.amazonaws.com/search?q=real+madrid+champions+league+football)

## OpenAPI plug-in for VS Code

One can use any text editor to view the documentation but better experience can be achieved with [VSCode OpenAPI add-on](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi).

### OpenAPI SwaggerUI preview 

Preview mode can be used to make requests to endpoints. 

At this time Presign and Search endpoints uses inidividual URLs which you can select from Servers drop-down menu.

![VS Code OpenAPI preview](https://raw.githubusercontent.com/jussiheinonen/ltd.noooner.dam.core/main/documentation/assets/vscode-openapi-preview.png "VS Code OpenAPI preview")
