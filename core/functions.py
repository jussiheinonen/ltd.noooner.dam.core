#!/usr/bin/env python3

from pprint import pprint
import time


def createDDBObject(dict):
    # construct DynamoDB object from dictionary
    id = time.time_ns() # Type of int
    ddb_item = { 'id' : {'S': str(id)} }
    for key, value in dict.items():
        type = isTypeOf(value)
        if type == 'SS': 
            value = list( dict.fromkeys(value)) #remove duplicates on the list / stringset, prevent error "Input collection []  contains duplicates"
        #print("'" + str(key) + "': {" + "'" + type + "':" + "'" + str(value) + "'}")
        type_value = { type : value }
        ddb_item[key] = type_value
    return ddb_item

def isTypeOf(value):
    # data types https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item

    if type(value) is list: # Stringset 
        return 'SS'
    elif type(value) is dict: # Map :
        return 'M'
    else:
        return 'S'


def writeDictionaryToDDB(dict, table_name, client):
    print('writing metadata')
    
    ddb_obj = createDDBObject(dict)
    pprint(ddb_obj)

    resp = client.put_item( 
        TableName=table_name, 
        Item=ddb_obj
        )

    print(str(resp))

'''
aws dynamodb create-table \
--table-name ltd.nooonert.dam.core.index.dev \
--attribute-definitions AttributeName=id,AttributeType=S \
--key-schema AttributeName=id,KeyType=HASH \
--provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
--endpoint-url http://localhost:4566

aws dynamodb list-tables --endpoint-url http://localhost:4566

aws dynamodb scan \
    --table-name ltd.nooonert.dam.core.index.dev \
    --endpoint-url http://localhost:4566
'''