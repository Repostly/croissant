# import flast module
from flask import Flask, render_template, url_for, redirect, request, jsonify
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import logging

# Load environment variables
load_dotenv()

# AWS Configuration
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_bucket = os.getenv('AWS_BUCKET_NAME')
aws_region = os.getenv('AWS_REGION')

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
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
        # Upload the video file to S3
        s3_client.put_object(
            Bucket=aws_bucket,
            Key=filename,
            Body=video_file.read(),  # Read the file data from form
            ContentType=video_file.content_type or 'video/mp4'
        )
        
        # Generate the URL for the uploaded video
        url = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{filename}"
        return True, url
    
    except ClientError as e:
        logging.error(e)
        return False, str(e)

# instance of flask application
app = Flask(__name__)

# Route for video upload to S3
@app.route("/upload", methods=['POST'])
def upload():
    try:
        # Get the first file from the files array
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file part in request"
            }), 400
            
        video_file = request.files['file']
        filename = request.form.get('filename')
        
        # Validate inputs
        if not video_file:
            return jsonify({
                "success": False,
                "error": "No video file selected"
            }), 400
        if not filename:
            return jsonify({
                "success": False,
                "error": "No filename provided"
            }), 400
            
        success, result = upload_video_to_s3(video_file, filename)
        
        if success:
            return jsonify({
                "success": True,
                "url": result
            })
        else:
            return jsonify({
                "success": False,
                "error": result
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':  
   app.run()