import json
import boto3
from botocore.exceptions import ClientError
import logging
from flask import current_app as app

def get_lambda_client():
    return boto3.client(
        'lambda',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=app.config['AWS_REGION']
    )

def invoke_lambda_function(function_name, payload):
    """
    Invoke an AWS Lambda function
    
    Args:
        function_name (str): The name or ARN of the Lambda function
        payload (dict): The payload to send to the Lambda function
    
    Returns:
        tuple: (bool, dict) - (Success status, Response or error message)
    """
    try:
        lambda_client = get_lambda_client()
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Check if the invocation was successful
        if response['StatusCode'] == 200:
            return True, json.loads(response['Payload'].read())
        else:
            return False, f"Lambda invocation failed with status code: {response['StatusCode']}"
    
    except ClientError as e:
        logging.error(e)
        return False, str(e)