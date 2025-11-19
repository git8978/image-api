# app/api.py

import json
from flask import Blueprint, request, jsonify, current_app

from app.exceptions import InvalidInputError

# Define a Blueprint for the API routes
bp = Blueprint('api', __name__, url_prefix='/images')

@bp.route("/upload", methods=["POST"])
def upload_image_api():
    """API for uploading an image with metadata."""
    s3_service = current_app.s3_service
    
    if 'file' not in request.files:
        raise InvalidInputError("Missing 'file' part in request.")
    
    file_to_upload = request.files['file']
    metadata_json = request.form.get('metadata', '{}')
    
    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError:
        raise InvalidInputError("Metadata must be a valid JSON string.")
        
    result = s3_service.upload_image(file_to_upload, metadata)
    return jsonify({"status": "success", "data": result}), 201

@bp.route("/", methods=["GET"])
def list_images_api():
    """API to list images with filtering."""
    s3_service = current_app.s3_service
    
    prefix_filter = request.args.get('prefix')
    max_keys_str = request.args.get('limit')
    max_keys = None
    
    if max_keys_str:
        try:
            max_keys = int(max_keys_str)
        except ValueError:
            raise InvalidInputError("'limit' must be an integer.")

    images = s3_service.list_images(prefix=prefix_filter, max_keys=max_keys)
    return jsonify({"status": "success", "data": images})

@bp.route("/<path:image_key>", methods=["GET"])
def view_or_download_image_api(image_key):
    """API to view metadata or download an image."""
    s3_service = current_app.s3_service
    
    mode = request.args.get('mode', 'view').lower()
    
    if mode == 'download':
        return s3_service.get_image(image_key, download=True)
    elif mode == 'view':
        metadata = s3_service.get_image(image_key, download=False)
        return jsonify({"status": "success", "data": metadata})
    else:
        raise InvalidInputError("Invalid 'mode' parameter. Must be 'view' or 'download'.")

@bp.route("/<path:image_key>", methods=["DELETE"])
def delete_image_api(image_key):
    """API to delete an image."""
    s3_service = current_app.s3_service
    result = s3_service.delete_image(image_key)
    return jsonify({"status": "success", "data": result})