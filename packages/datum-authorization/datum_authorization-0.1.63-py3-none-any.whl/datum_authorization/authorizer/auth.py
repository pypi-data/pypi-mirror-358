import logging
import json
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_authorizer(event, context):
    # Print event for debugging
    logger.info(f"Incoming event: {json.dumps(event)}")
    return {}
