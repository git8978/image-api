# tests/test_api.py

import pytest
import json
from io import BytesIO
from botocore.exceptions import ClientError
from app.config import Config # Import for referencing the bucket name

# Fixtures (client, s3_service_client, setup_s3_data) are imported implicitly from conftest.py

# --- Unit Tests for API Endpoints ---

def test_upload_image_success(client, s3_service_client):
    """Test successful image upload with metadata."""
    data = {
        'file': (BytesIO(b"test image content"), 'my_photo.png'),
        'metadata': json.dumps({"description": "Sunset pic", "camera": "iPhone"})
    }
    
    response = client.post("/images/upload", data=data, content_type='multipart/form-data')
    response_data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'key' in response_data['data']
    
    # Verify the file is in the mocked S3 bucket
    s3_key = response_data['data']['key']
    s3_object = s3_service_client.s3_client.get_object(Bucket=s3_service_client.bucket_name, Key=s3_key)
    assert s3_object['ContentLength'] == len(b"test image content")
    assert s3_object['Metadata']['description'] == 'Sunset pic'
    
def test_upload_image_no_file(client):
    """Test upload failure when 'file' part is missing."""
    response = client.post("/images/upload", data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == "Missing 'file' part in request."

def test_upload_image_invalid_metadata(client):
    """Test upload failure when metadata is not valid JSON."""
    data = {
        'file': (BytesIO(b"test content"), 'image.png'),
        'metadata': 'this is not json'
    }
    response = client.post("/images/upload", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == "Metadata must be a valid JSON string."

def test_list_images_success(client, setup_s3_data):
    """Test successful listing of all images."""
    response = client.get("/images/")
    response_data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(response_data['data']) == 2
    
def test_list_images_with_prefix_filter(client, setup_s3_data):
    """Test listing images filtered by a prefix."""
    response = client.get("/images/?prefix=20250101")
    response_data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(response_data['data']) == 1
    assert 'image_alpha.png' in response_data['data'][0]['key']

def test_list_images_with_limit_filter(client, setup_s3_data):
    """Test listing images filtered by a limit."""
    response = client.get("/images/?limit=1")
    response_data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(response_data['data']) == 1
    
def test_list_images_invalid_limit(client):
    """Test listing failure with invalid limit parameter."""
    response = client.get("/images/?limit=abc")
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == "'limit' must be an integer."

def test_view_image_metadata_success(client, setup_s3_data):
    """Test viewing image metadata (default mode)."""
    image_key = setup_s3_data[0] # key1
    response = client.get(f"/images/{image_key}?mode=view")
    response_data = json.loads(response.data)
    
    assert response.status_code == 200
    assert response_data['data']['key'] == image_key
    assert response_data['data']['metadata']['author'] == 'alice'

def test_download_image_success(client, setup_s3_data):
    """Test successful image download."""
    image_key = setup_s3_data[0] # key1
    response = client.get(f"/images/{image_key}?mode=download")
    
    assert response.status_code == 200
    assert response.data == b"image content 1"
    assert response.content_type == "image/png"
    assert 'attachment; filename=' in response.headers['Content-Disposition']

def test_get_image_not_found(client):
    """Test getting an image that doesn't exist."""
    response = client.get("/images/non-existent-key?mode=view")
    assert response.status_code == 404
    assert json.loads(response.data)['message'] == "Image not found with key: non-existent-key"

def test_delete_image_success(client, setup_s3_data, s3_service_client):
    """Test successful image deletion."""
    image_key = setup_s3_data[0] # key1
    
    response = client.delete(f"/images/{image_key}")
    response_data = json.loads(response.data)
    
    assert response.status_code == 200
    assert response_data['data']['status'] == 'deleted'
    
    # Verify deletion in S3
    with pytest.raises(ClientError):
        s3_service_client.s3_client.head_object(Bucket=s3_service_client.bucket_name, Key=image_key)
    
def test_delete_image_not_found(client):
    """Test deleting an image that doesn't exist."""
    response = client.delete("/images/non-existent-key")
    assert response.status_code == 404
    assert json.loads(response.data)['message'] == "Image not found with key: non-existent-key"