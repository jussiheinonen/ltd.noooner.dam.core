#!/usr/bin/env python3

from app import lambda_handler
from pprint import pprint
import os, boto3, argparse

parser = argparse.ArgumentParser(description='Image metadata processor')
parser.add_argument('-i', '--id', dest='id', required=True, help="Image ID to process, eg. a451196f4a1317e5133ec57d29b8ecf1")
parser.add_argument('-m', '--method', dest='method', default='GET', help="HTTP method, eg. GET, PUT, POST")
parser.add_argument('-d', '--data', dest='data', default={}, help="Data in JSON document format")
args = parser.parse_args()

id = args.id
method = args.method
data = args.data

def mockAPITrigger(id, method, data):
    
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
                        "id": id
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
                    "body": data,
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

payload = mockAPITrigger(id, method, data)

results = lambda_handler(payload, None)
#print('lambda_handler returned object type ' + str(type(results)))
print('HERE IS WHAT WE GOT:')
pprint(results)