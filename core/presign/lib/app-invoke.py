#!/usr/bin/env python3

from app import lambda_handler
    
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

def mockAPITrigger(bucket, key, expiration=300):
    event = dict(
        {
            "body": {"method": bucket, "filename": key,  "expiration": expiration }
        }
    )
    return event

event = mockAPITrigger('put_object', '2BCBG15_over_medium.jpg', 500)

lambda_handler(event, None)