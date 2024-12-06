from flask import Blueprint, request, jsonify, current_app as app
from app.services.aws_lambda import invoke_lambda_function

post_bp = Blueprint('post', __name__)

@post_bp.route("/post", methods=['POST'])
def post():
    try:
        # Extract data from the request
        data = request.json
        required_fields = ['video_url', 'title', 'access_token', 'refresh_token', 'social_media']
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        # Prepare the payload for the Lambda function
        payload = {
            'video_url': data['video_url'],
            'title': data['title'],
            'description': data.get('description', ''),
            'privacy_status': data.get('privacy_status', 'private'),
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'social_media': data['social_media']
        }

        # Determine which Lambda function to call based on social_media
        match data['social_media']:
            case "youtube":
                function_name = app.config['YOUTUBE_UPLOAD_LAMBDA_FUNCTION']
            case "tiktok":
                function_name = app.config['TIKTOK_UPLOAD_LAMBDA_FUNCTION']
            case "instagram":
                function_name = app.config['INSTAGRAM_UPLOAD_LAMBDA_FUNCTION']
            case _:
                return jsonify({
                    "success": False,
                    "error": f"Unknown social media: {data['social_media']}"
                }), 400

        # Invoke the Lambda function
        success, result = invoke_lambda_function(function_name, payload)

        if success:
            return jsonify({
                "success": True,
                "result": result
            }), 200
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