#!/usr/bin/env python3

'''
EXAMPLE GET REQUEST
https://tm7do0vu9j.execute-api.eu-west-1.amazonaws.com/presign?filename=train01.jpg&action=get_object&expiration=500
'''

from app import lambda_handler, default_expiration
import argparse
    
def mockS3Trigger(bucket, key):
    event = dict(
        {
            "Records": [
            {
                "s3": {
                "bucket": {
                    "name": bucket
                },
                "object": {
                    "key": key
                }
                }
            }
            ]
        }
    )

    return event

def mockAPITrigger(filename = 'file1', method = 'GET', action = 'put_object', expiration = 300):
    #Payload format https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    event = dict(
                    {
                    "version": "2.0",
                    "routeKey": "$default",
                    "rawPath": "/my/path",
                    "rawQueryString": "parameter1=value1&parameter1=value2&parameter2=value",
                    "cookies": [
                        "cookie1",
                        "cookie2"
                    ],
                    "headers": {
                        "header1": "value1",
                        "header2": "value1,value2"
                    },
                    "queryStringParameters": {
                        "filename": filename,
                        "action": action,
                        "expiration": expiration,
                    },
                    "requestContext": {
                        "accountId": "123456789012",
                        "apiId": "api-id",
                        "authentication": {
                        "clientCert": {
                            "clientCertPem": "CERT_CONTENT",
                            "subjectDN": "www.example.com",
                            "issuerDN": "Example issuer",
                            "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                            "validity": {
                            "notBefore": "May 28 12:30:02 2019 GMT",
                            "notAfter": "Aug  5 09:36:04 2021 GMT"
                            }
                        }
                        },
                        "authorizer": {
                        "jwt": {
                            "claims": {
                            "claim1": "value1",
                            "claim2": "value2"
                            },
                            "scopes": [
                            "scope1",
                            "scope2"
                            ]
                        }
                        },
                        "domainName": "id.execute-api.us-east-1.amazonaws.com",
                        "domainPrefix": "id",
                        "http": {
                        "method": method,
                        "path": "/my/path",
                        "protocol": "HTTP/1.1",
                        "sourceIp": "IP",
                        "userAgent": "agent"
                        },
                        "requestId": "id",
                        "routeKey": "$default",
                        "stage": "$default",
                        "time": "12/Mar/2020:19:03:58 +0000",
                        "timeEpoch": 1583348638390
                    },
                    "body": {"action": action, "filename": filename,  "expiration": expiration },
                    "pathParameters": {
                        "parameter1": "value1"
                    },
                    "isBase64Encoded": False,
                    "stageVariables": {
                        "stageVariable1": "value1",
                        "stageVariable2": "value2"
                    }
                    }        
    )
    return event

def mockAPITriggerPOST(bucket, key, expiration=300):
    event = dict(
        {
            "body": {"method": bucket, "filename": key,  "expiration": expiration }
        }
    )
    return event

parser = argparse.ArgumentParser(description='Generate Presign URL from either POST or GET')
parser.add_argument('-f', '--filename', dest='filename', required=True, help="Filename to generate URL for")
parser.add_argument('-a', '--action', dest='action', required=True, help="put_object or get_object")
parser.add_argument('-m', '--method', dest='method', default='GET', help="HTTP method, eg. GET|POST")
parser.add_argument('-e', '--expiration', dest='expiration', default=default_expiration, help="URL expiry in seconds")
args = parser.parse_args()

filename = args.filename
method= args.method
action= args.action
expiration= args.expiration
event = mockAPITrigger(filename, method, action, expiration)


#event = mockAPITrigger('put_object', '2BCBG15_over_medium.jpg', 500)

lambda_handler(event, None)