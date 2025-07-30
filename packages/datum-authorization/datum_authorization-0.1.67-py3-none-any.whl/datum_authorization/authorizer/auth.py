import logging
import json

from datum_authorization import enable_authorize

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@enable_authorize()
def lambda_authorizer(event, context):
    # Print event for debugging
    logger.info(f"Incoming event: {json.dumps(event)}")
    return {
        "statusCode": 200,
        "body": "Hello"
    }