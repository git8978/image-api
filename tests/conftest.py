# tests/conftest.py

import pytest
from moto import mock_aws

# Import the application factory and config for testing
from app import create_app
from app.config import Config
from app.services.s3_service import S3Service

# Define a TestConfig class
class TestConfig(Config):
    TESTING = True

# --- Fixtures for Boto3/S3 Mocking ---

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    # When create_app is called, S3Service is initialized, which attempts to 
    # create the bucket. @mock_aws must be active for this.
    with mock_aws(): 
        flask_app = create_app(TestConfig)
        with flask_app.app_context():
            yield flask_app

@pytest.fixture
def client(app):
    """A Flask test client for making requests."""
    return app.test_client()

@pytest.fixture
def s3_service_client(app):
    """Provides the S3Service instance attached to the mocked app."""
    # This automatically uses the mocked S3 environment set up by moto
    return app.s3_service

@pytest.fixture
def setup_s3_data(s3_service_client):
    """Sets up some test data in the mocked S3 bucket."""
    
    keys = []
    bucket_name = s3_service_client.bucket_name
    
    # Test Image 1
    key1 = f"20250101000000-image_alpha.png"
    s3_service_client.s3_client.put_object(
        Bucket=bucket_name,
        Key=key1,
        Body=b"image content 1",
        ContentType="image/png",
        Metadata={"author": "alice", "project": "demo"}
    )
    keys.append(key1)

    # Test Image 2
    key2 = f"20250102000000-other_beta.jpg"
    s3_service_client.s3_client.put_object(
        Bucket=bucket_name,
        Key=key2,
        Body=b"image content 2",
        ContentType="image/jpeg",
        Metadata={"author": "bob", "project": "test"}
    )
    keys.append(key2)
    
    return keys