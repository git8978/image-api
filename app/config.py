# app/config.py

import os

class Config:
    # LocalStack and AWS Configuration
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "image-storage-bucket")
    LOCALSTACK_ENDPOINT_URL = os.environ.get("LOCALSTACK_ENDPOINT_URL", "http://localhost:4566")
    # AWS Credentials (Needed by Boto3, even for LocalStack)
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")
    
    
    # Dummy credentials for LocalStack
    #AWS_ACCESS_KEY_ID = "test"
    #AWS_SECRET_ACCESS_KEY = "test"
    #AWS_REGION = "us-east-1"
    
    # Flask Configuration
    SECRET_KEY = os.environ.get("SECRET_KEY", "a_strong_dev_secret")
    TESTING = False