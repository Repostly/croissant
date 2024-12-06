from flask import Blueprint, request, jsonify
from app.services.s3 import upload_video_to_s3

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=['POST'])
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