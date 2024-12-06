import boto3
from botocore.exceptions import ClientError
import logging
from flask import current_app as app

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=app.config['AWS_REGION']
    )

def upload_video_to_s3(video_file, filename):
    """
    Upload a video file from form data to S3 bucket
    
    Args:
        video_file: The video file from form-data/multipart request
        filename: The name to give the file in S3
    
    Returns:
        tuple: (bool, str) - (Success status, URL or error message)
    """
    try:
        # Get env variables
        bucket_name = app.config['AWS_BUCKET_NAME']
        region = app.config['AWS_REGION']

        # Upload the video file to S3
        get_s3_client().put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=video_file.read(),  # Read the file data from form
            ContentType=video_file.content_type or 'video/mp4'
        )
        
        # Generate the URL for the uploaded video
        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        return True, url
    
    except ClientError as e:
        logging.error(e)
        return False, str(e)