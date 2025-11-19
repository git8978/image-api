# app/services/s3_service.py
import boto3
import os
import io
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError
from flask import send_file
from werkzeug.utils import secure_filename

from app.config import Config
from app.exceptions import APIError, NotFoundError, InvalidInputError

class S3Service:
    def __init__(self, config: Config):
        self.bucket_name = config.S3_BUCKET_NAME
        self.config = config
        
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=config.LOCALSTACK_ENDPOINT_URL,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Creates the S3 bucket if it doesn't exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['404','NoSuchBucket']:
                print(f"Bucket {self.bucket_name} not found. Creating it...")
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                raise APIError(f"Error checking bucket existence: {e}", status_code=500)

    def upload_image(self, file_storage, metadata: Dict[str, str]) -> Dict[str, str]:
        """Uploads an image with custom metadata."""
        if not file_storage.filename:
            raise InvalidInputError("No file selected for upload.")

        filename = secure_filename(file_storage.filename)
        s3_key = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{filename}"

        s3_metadata = {k: str(v) for k, v in metadata.items()}

        try:
            self.s3_client.upload_fileobj(
                file_storage,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file_storage.content_type,
                    'Metadata': s3_metadata
                }
            )
            return {"key": s3_key, "url": f"{self.config.LOCALSTACK_ENDPOINT_URL}/{self.bucket_name}/{s3_key}"}
        except ClientError as e:
            raise APIError(f"S3 Upload failed: {e}", status_code=500)

    def list_images(self, prefix: Optional[str] = None, max_keys: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lists images with optional filters (prefix and max_keys)."""
        params = {'Bucket': self.bucket_name}
        if prefix:
            params['Prefix'] = prefix
        if max_keys:
            params['MaxKeys'] = max_keys

        try:
            response = self.s3_client.list_objects_v2(**params)
            
            if 'Contents' not in response:
                return []
            
            images = []
            for item in response.get('Contents', []):
                try:
                    head_object = self.s3_client.head_object(Bucket=self.bucket_name, Key=item['Key'])
                    images.append({
                        'key': item['Key'],
                        'last_modified': item['LastModified'].isoformat(),
                        'size_bytes': item['Size'],
                        'metadata': head_object.get('Metadata', {})
                    })
                except ClientError:
                    continue
            return images
        except ClientError as e:
            raise APIError(f"S3 List failed: {e}", status_code=500)

    def get_image(self, key: str, download: bool = False):
        """Retrieves and streams an image or its metadata."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            
            if download:
                file_stream = io.BytesIO(response['Body'].read())
                return send_file(
                    file_stream,
                    mimetype=response['ContentType'],
                    as_attachment=True,
                    download_name=key
                )
            else:
                return {
                    'key': key,
                    'last_modified': response['LastModified'].isoformat(),
                    'size_bytes': response['ContentLength'],
                    'content_type': response['ContentType'],
                    'metadata': response.get('Metadata', {})
                }

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise NotFoundError(f"Image not found with key: {key}")
            raise APIError(f"S3 Get failed: {e}", status_code=500)

    def delete_image(self, key: str) -> Dict[str, str]:
        """Deletes an image from the S3 bucket."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return {"key": key, "status": "deleted"}
        except ClientError as e:
            if e.response['Error']['Code'] in ['404', 'NoSuchKey']:
                raise NotFoundError(f"Image not found with key: {key}")
            raise APIError(f"S3 Delete failed: {e}", status_code=500)