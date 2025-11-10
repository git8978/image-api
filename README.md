
Here’s the complete content:

---

```markdown
# Image API Service

## Project Overview

This project provides a **Flask-based image management API** that uses **AWS S3 (via LocalStack)** to upload, list, retrieve, download, and delete images.
Metadata can also be stored with each image.
The service is fully containerized with Docker and orchestrated with Docker Compose.

---

## Table of Contents

1. [Project Structure](#project-structure)  
2. [Environment Variables](#environment-variables)  
3. [Docker Setup](#docker-setup)  
4. [Running Locally](#running-locally)  
5. [API Endpoints](#api-endpoints)  
6. [Example CURL Requests](#example-curl-requests)  
7. [Notes](#notes)

---

## Project Structure

```

image-api/
├── app/
│   ├── **init**.py          # Flask app factory
│   ├── config.py            # Configuration class
│   ├── api.py               # API routes
│   ├── exceptions.py        # Custom exceptions and error handlers
│   └── services/
│       └── s3_service.py    # AWS S3 service class
├── Dockerfile               # Flask app Dockerfile
├── docker-compose.yml       # Docker Compose setup with LocalStack
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation

````

---

## Environment Variables

| Variable                     | Description                                           | Example                     |
|-------------------------------|------------------------------------------------------|-----------------------------|
| `LOCALSTACK_ENDPOINT_URL`     | URL for LocalStack S3 service                        | `http://localstack:4566`   |
| `S3_BUCKET_NAME`              | S3 bucket name used to store images                 | `image-storage-bucket`      |
| `AWS_REGION`                  | AWS region (used by LocalStack and boto3)          | `us-east-1`                 |
| `AWS_ACCESS_KEY_ID`           | AWS access key (for LocalStack testing)            | `test`                       |
| `AWS_SECRET_ACCESS_KEY`       | AWS secret key (for LocalStack testing)            | `test`                       |

---

## Docker Setup

### docker-compose.yml

```yaml
version: '3.8'
services:
  localstack:
    container_name: localstack_image_api
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
      - "8080:8080"
    environment:
      - SERVICES=s3
      - DEBUG=1
      - AWS_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
    volumes:
      - "${LOCALSTACK_VOLUME_DIR:-./volume}:/var/lib/localstack"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4566/health"]
      interval: 15s
      timeout: 10s
      retries: 10

  image-api:
    build: .
    container_name: image_api_flask
    ports:
      - "5000:5000"
    environment:
      - LOCALSTACK_ENDPOINT_URL=http://localstack:4566
      - S3_BUCKET_NAME=image-storage-bucket
    depends_on:
      localstack:
        condition: service_healthy
````

---

## Running Locally

### 1. Build and Start Containers

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### 2. Test Flask App

Visit:

```
http://localhost:5000/images
```

Response:

```json
{"status":"success","data":[]}

```

---

## API Endpoints

| Endpoint              | Method | Description                                               |
| --------------------- | ------ | --------------------------------------------------------- |
| `/images/`            | GET    | List all images (with optional `prefix` & `limit`)        |
| `/images/upload`      | POST   | Upload an image with metadata                             |
| `/images/<image_key>` | GET    | View metadata (`mode=view`) or download (`mode=download`) |
| `/images/<image_key>` | DELETE | Delete an image                                           |

### Request Parameters

#### Upload Image

* Form Data:

  * `file` (required): File to upload
  * `metadata` (optional): JSON string containing metadata

Example metadata:

```json
{"description": "Sample image", "tags": "sample,test"}
```

#### List Images

* Query Parameters:

  * `prefix` (optional): Filter keys starting with this string
  * `limit` (optional): Max number of keys to return

#### Get or Download Image

* Query Parameters:

  * `mode` (optional): `view` (default) or `download`

---

## Example CURL Requests

### Upload Image

```bash
curl -F "file=@/path/to/image.jpg" \
     -F 'metadata={"description":"sample image"}' \
     http://localhost:5000/images/upload
```

### List Images

```bash
curl http://localhost:5000/images
```

### View Metadata

```bash
curl http://localhost:5000/images/<image_key>
```

### Download Image

```bash
curl -O "http://localhost:5000/images/<image_key>?mode=download"
```

### Delete Image

```bash
curl -X DELETE http://localhost:5000/images/<image_key>
```

---

## Notes

1. **LocalStack** is used as a mock AWS environment, so all S3 operations are local.
2. Images are uploaded to the S3 bucket defined by `S3_BUCKET_NAME`.
3. Metadata is stored in S3 object metadata.
4. Flask app runs on port `5000` and exposes API under `/images` prefix.

```

---


```
