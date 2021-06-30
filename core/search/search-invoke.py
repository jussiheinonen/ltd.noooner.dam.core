#!/usr/bin/env python3

from search import lambda_handler
import argparse, sys
from pprint import pprint

def mockAPITrigger(query_string_parameters = None, method = 'GET'):
    if query_string_parameters:
        query = query_string_parameters
    else:
        query = "value1"
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
                        "q": query,
                        "sort_dicts": sort
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
                    "body": "Hello from Lambda",
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

def mockSearchResults():
    '''
    Proposal for document structure for search results of multiple keywords search
    3 keyword search: q=real+madrid+white
    '''
    ids_per_keyword = {
        "real": [ "f21c81d1d5f9d8303fbffb9b325ee236", "db70be6b0173e1b4aafcb9d49151cfaf" ],
        "madrid": [ "f21c81d1d5f9d8303fbffb9b325ee236", "db70be6b0173e1b4aafcb9d49151cfaf" ],
        "white": [ "9e09840ecc13c72fa6c4f75db20ca29e", "cf545fd7526d8ff21e5737b529be9621" ]
    }

    programmatic_keywords_per_id = swapDictKeysAndValues(ids_per_keyword)

    return programmatic_keywords_per_id

def swapDictKeysAndValues(ids_per_keyword):
    '''
    Process dictionary keys and values and swap them around so they look like keywords_per_id
    '''
    keywords_per_id = {
        "f21c81d1d5f9d8303fbffb9b325ee236": [ "real", "madrid" ],
        "db70be6b0173e1b4aafcb9d49151cfaf": [ "real", "madrid" ],
        "9e09840ecc13c72fa6c4f75db20ca29e": [ "white" ],
        "cf545fd7526d8ff21e5737b529be9621": [ "white" ]
    }
    id_keywords = {}
    for key, value_lst in ids_per_keyword.items():
        for id in value_lst:
            #print('Adding keyword ' + str(key) + ' against id ' + str(id))
            id_keywords.setdefault(id, []).append(key) # Solution provided by Paul Panzer in https://stackoverflow.com/questions/43060655/update-values-of-a-list-of-dictionaries-in-python
    return id_keywords


parser = argparse.ArgumentParser(description='Search a record based on keyword')
parser.add_argument('-w', '--word', dest='word', required=True, help="Keyword to search in DynamoDB")
parser.add_argument('-m', '--method', dest='method', default='GET', help="HTTP method, eg. GET|POST")
parser.add_argument('-s', '--sort_dicts', dest='sort', default='True', help="Sort search results, True or False")
args = parser.parse_args()

word = args.word
method= args.method
sort= args.sort

'''
results = mockSearchResults()
pprint(results)
sys.exit(0)
'''

payload = mockAPITrigger(word, method)

results = lambda_handler(payload, None)

print('HERE IS WHAT WE GOT:')
#print(str(results))
pprint(results, sort_dicts=False)
